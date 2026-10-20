import re
import requests
import asyncio
import aiohttp
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urljoin

# defines the name of the url I'm getting everything from (shoutout iptv)
# also the url changes sometimes, so go to the iptv github page to find up to date urls
PLAYLIST_URL = "https://iptv-org.github.io/iptv/countries/us.m3u"

DB_PATH = "tv.db"


# does an http get request to get a url
def download_playlist(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    # returns the result of the above 2 lines as a string
    return response.text


def parse_m3u(text):
    # list of channels, starts out empty
    channels = []
    # the channel we're currently building (None until we see a #EXTINF line)
    current = None

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#EXTINF"):
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', line))
            name = line.rsplit(",", 1)[-1].strip()
            current = {
                "name": name,
                "logo": attrs.get("tvg-logo", ""),
                "group": attrs.get("group-title", ""),
                "tvg_id": attrs.get("tvg-id", ""),
            }
        elif line.startswith("#"):
            continue
        else:
            if current is not None:
                current["url"] = line
                channels.append(current)
                current = None
    return channels


async def fetch_text(session, url):
    async with session.get(url) as resp:
        if resp.status != 200:
            return None
        return await resp.text()


def first_url(playlist_text, base_url):
    for line in playlist_text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return urljoin(base_url, line)
    return None


async def check_stream(session, semaphore, channel):
    async with semaphore:
        try:
            url = channel["url"]

            text = await fetch_text(session, url)
            if text is None or not text.lstrip().startswith("#EXTM3U"):
                return False

            next_url = first_url(text, url)
            if next_url is None:
                return False

            if ".m3u8" in next_url:
                text = await fetch_text(session, next_url)
                if text is None or not text.lstrip().startswith("#EXTM3U"):
                    return False
                next_url = first_url(text, next_url)
                if next_url is None:
                    return False

            async with session.get(next_url) as resp:
                if resp.status != 200:
                    return False
                chunk = await resp.content.read(1024)
                return len(chunk) > 0

        except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeDecodeError):
            return False


async def check_all(channels):
    semaphore = asyncio.Semaphore(50)
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [check_stream(session, semaphore, ch) for ch in channels]
        results = await asyncio.gather(*tasks)

    return results


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            logo TEXT,
            category TEXT,
            tvg_id TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL REFERENCES channels(id),
            url TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'unknown',
            last_checked TEXT,
            failure_count INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    return conn


def save_results(conn, channels, results):
    now = datetime.now(timezone.utc).isoformat()

    for ch, ok in zip(channels, results):
        row = conn.execute(
            "SELECT id FROM streams WHERE url = ?", (ch["url"],)
        ).fetchone()

        if row is None:
            cursor = conn.execute(
                "INSERT INTO channels (name, logo, category, tvg_id) VALUES (?, ?, ?, ?)",
                (ch["name"], ch["logo"], ch["group"], ch["tvg_id"]),
            )
            channel_id = cursor.lastrowid

            conn.execute(
                "INSERT INTO streams (channel_id, url, status, last_checked, failure_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (channel_id, ch["url"], "working" if ok else "failed", now, 0 if ok else 1),
            )
        elif ok:
            conn.execute(
                "UPDATE streams SET status = 'working', last_checked = ?, failure_count = 0 "
                "WHERE url = ?",
                (now, ch["url"]),
            )
        else:
            conn.execute(
                "UPDATE streams SET status = 'failed', last_checked = ?, "
                "failure_count = failure_count + 1 WHERE url = ?",
                (now, ch["url"]),
            )

    conn.commit()


def get_working_channels(conn):
    return conn.execute("""
        SELECT channels.name, channels.category, streams.url
        FROM streams
        JOIN channels ON channels.id = streams.channel_id
        WHERE streams.status = 'working'
        ORDER BY channels.name
    """).fetchall()


if __name__ == "__main__":
    text = download_playlist(PLAYLIST_URL)
    channels = parse_m3u(text)
    print(f"Checking {len(channels)} channels...")

    results = asyncio.run(check_all(channels))

    conn = init_db()
    save_results(conn, channels, results)

    working = get_working_channels(conn)
    print(f"{len(working)} working streams saved to {DB_PATH}")
    for row in working[:10]:
        print(" -", row["name"], "|", row["category"])

    conn.close()

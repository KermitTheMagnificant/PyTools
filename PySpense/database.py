# imports sqlite and the Path function
import sqlite3
from pathlib import Path
# Sets the path of the database using aforementioned path function
DB_PATH = Path(__file__).parent / "expense.db"

# func which connects the .py and .db files
def get_connection():
    # Opens SQLite DB at the defined path of the .db file
    conn = sqlite3.connect(DB_PATH)
    # Makes the SQLite connection return requested data in a more readable format
    conn.row_factory = sqlite3.Row
    return conn

# func which initializes the db, creating a table if it doesn't already exist
def init_db():
    # calls get_connection and names the result conn
    with get_connection() as conn:
        # creates table called expenses if doesn't exist
        # sqlite syntax stored in a python string, executed using conn.execute
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                category    TEXT NOT NULL,
                note        TEXT DEFAULT ''
            )

        """)

# defines add_expense, adding an expense to the db
def add_expense(date, amount_cents, category, note=""):
    #defines connection to db w/ get_connection()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO EXPENSES (date, amount_cents, category, note) VALUES (?, ?, ?, ?)",
            (date, amount_cents, category, note),
        )
        return cursor.lastrowid

# deletes expense
def delete_expense(expense_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

# func which lists expenses in db, returned in desc. order by date and id
def list_expenses():
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, date, amount_cents, category, note "
            "FROM expenses ORDER BY date DESC, id DESC"
        )
        return cursor.fetchall()

# func which totals monthly expenses returned in desc. order by month
def total_by_month():
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT strftime('%Y-%m', date) AS month, SUM(amount_cents) AS total "
            "FROM expenses GROUP BY month ORDER BY month DESC"
        )
        return cursor.fetchall()

# func which totals expenses by category
def total_by_category(month=None):
    query = "SELECT category, SUM(amount_cents) AS total FROM expenses"
    params = ()
    if month:
        query += " WHERE substr(date, 1, 7) = ?"
        params = (month,)
    query += " GROUP BY category ORDER BY total DESC"

    with get_connection() as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchall()


# if program is run using python3 database.py, init_db() is called and gives user db path
if __name__ == "__main__":
    init_db()
    print("Database ready at ", DB_PATH)


# im getting to the end of making this and I am just fucking tired and I still have schoolwork to do.
# Fuck my stupid chungus life

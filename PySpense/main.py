# imports date from datetime and database.py
from datetime import date
import database

def parse_amount(text):
    # defines dollars as the float of the input
    dollars = float(text)
    # converts dollars into cents, rounds
    return round(dollars * 100)

# turns the cents into a readable dollar amount
def format_cents(cents):
    return f"${cents / 100:.2f}"

# func which adds an expense to the db
def add_flow():
    # gets amount number
    amount_text = input("Enter amount (ex: 2.50, (dollars).(cents)): ")
    try: 
        amount_cents = parse_amount(amount_text)
    # if not valid float warns user and returns to above text
    except ValueError:
        print("Invalid amount. Please enter a valid number. (Follow format as (dollars).(cents)")
        return

    # takes category, strips whitespace and converts to lowercase
    category = input("Enter category: ").strip().lower()
    # if empty warns user and returns to above text
    if not category:
        print("Category cannot be empty.")
        return
    # takes note and strips whitespace
    note = input("Enter note (optional): ").strip()

    # gets date and adds the expense to the db (YYYY-MM-DD format)
    today = date.today().isoformat()
    expense_id = database.add_expense(today, amount_cents, category, note)
    # lists id num
    print(f"Saved expense id as #{expense_id}.")

# func which lists expenses in db
def list_flow():
    rows = database.list_expenses()
    # tells user if there are no expenses 
    if not rows:
        print("No expenses found.")
        return

    # gets list of rows 
    for row in rows:
        # prints the info of each expense in a readable format 
        print(
            f"{row['id']:>3} {row['date']}  "
            f"{format_cents(row['amount_cents']):>8}  "
            f"{row['category']:<12}" f"{row['note']}"
        )

# ngl i used ai for ts 
def summary_flow():
    month_rows = database.total_by_month()
    if not month_rows:
        print("No expenses yet.")
        return

    print("\nSpending by month:")
    for row in month_rows:
        print(f"  {row['month']}  {format_cents(row['total']):>10}")

    month = input("\nCategory breakdown for which month? (YYYY-MM, or Enter for all time): ").strip()
    rows = database.total_by_category(month or None)
    if not rows:
        print("No expenses for that month.")
        return

    grand_total = sum(row["total"] for row in rows)
    label = month if month else "all time"
    print(f"\nBy category ({label}):")
    for row in rows:
        share = row["total"] / grand_total * 100 if grand_total else 0
        print(
            f"  {row['category']:<12} "
            f"{format_cents(row['total']):>10}  {share:5.1f}%"
        )
    print(f"  {'TOTAL':<12} {format_cents(grand_total):>10}")

def remove_flow():
    expense_id = input("Enter the ID of the expense you want to remove: ").strip()
    if not expense_id.isdigit():
        print("Invalid ID. Please enter a valid number.")
        return
    with database.get_connection() as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if cursor.rowcount == 0:
            print(f"No expense found with ID {expense_id}.")
        else:
            print(f"Expense with ID {expense_id} has been removed.")

# menu loop tingy
def main():
    # makes sure db is init.
    database.init_db()
    # menu loop allowing user to add, list and exit
    while True:
        print("\nWelcome to PySpense version 0.1!")
        print("1, Add Expense")
        print("2, List Expenses")
        print("3, Summary")
        print("4, Remove Expense")
        print("5, Exit")
        choice = input("Enter choice (1-5): ").strip()
        # choice handler
        if choice == "1":
            add_flow()
        elif choice == "2":
            list_flow()
        elif choice == "3":
            summary_flow()
        elif choice == "4":
            remove_flow()
        elif choice == "5":
            print("Exiting, Goodbye!")
            break
        else:
            print("Invalid! Enter a number between 1 and 5.")

# makes sure main() is called if the program is run by using python3 main.py
if __name__ == "__main__":
    main()
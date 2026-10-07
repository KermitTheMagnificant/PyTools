# imports tkinter and other related stuff
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import database

from main import parse_amount, format_cents

version = "v0.2"


class PySenseApp:
    def __init__(self, root):
        # stores window and sets title
        self.root = root
        root.title("PySense " + version)

        # big thanks to stackoverflow and claude for this... gui's are a pain in the ass
        # I realistically wrote only like 20% :sob:
        # creates frame
        form = ttk.Frame(root, padding="10")
        form.pack(fill="x")

        # creates labels and does row and column stuff
        ttk.Label(form, text="Amount").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Category").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Note").grid(row=0, column=2, sticky="w")

        # creates entry boxes and does row and column stuff
        self.amount_entry = ttk.Entry(form, width=10)
        self.category_entry = ttk.Entry(form, width=15)
        self.note_entry = ttk.Entry(form, width=30)
        self.amount_entry.grid(row=1, column=0, padx=(0, 5))
        self.category_entry.grid(row=1, column=1, padx=(0, 5))
        self.note_entry.grid(row=1, column=2, padx=(0, 5))

        # add expense respect button v
        ttk.Button(form, text="Add Expense", command=self.add_expense).grid(row=1, column=3)

        # I may also be dumb lmao
        # le table
        # column names
        columns = ("id", "date", "amount_cents", "category", "note")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

        # sets the names and widths of the columns
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("id", width=40, anchor="e")
        self.tree.column("date", width=90)
        self.tree.column("amount_cents", width=90, anchor="e")
        self.tree.column("category", width=110)
        self.tree.column("note", width=220)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # delete button
        ttk.Button(root, text="Delete Selected", command=self.delete_selected).pack(
            anchor="e", padx=10, pady=(0, 10)
        )
        self.refresh()

    # reloads table
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in database.list_expenses():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["id"],
                    row["date"],
                    format_cents(row["amount_cents"]),
                    row["category"],
                    row["note"],
                ),
            )

    # (kinda) copy paste from add_flow... this is so refreshing, somewhat at least
    def add_expense(self):
        try:
            amount_cents = parse_amount(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a number like 12.50.")
            return

        category = self.category_entry.get().strip().lower()
        if not category:
            messagebox.showerror("Missing category", "Category can't be empty.")
            return
        note = self.note_entry.get().strip()

        database.add_expense(date.today().isoformat(), amount_cents, category, note)

        for entry in (self.amount_entry, self.category_entry, self.note_entry):
            entry.delete(0, tk.END)
        self.amount_entry.focus()
        self.refresh()

    def delete_selected(self):
        # smth about the ids and trees man idk
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Nothing Selected", "Click on a row first.")
            return

        expense_id = int(self.tree.item(selected[0], "values")[0])
        if messagebox.askyesno("Confirm", f"Delete expense #{expense_id}?"):
            database.delete_expense(expense_id)
            self.refresh()


# main time
if __name__ == "__main__":
    database.init_db()
    root = tk.Tk()
    app = PySenseApp(root)
    root.mainloop()
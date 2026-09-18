

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import re

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.db")


# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------
class ContactDatabase:
    """Handles all SQLite operations for the contact book."""

    def __init__(self, db_path=DB_FILE):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                address TEXT
            )
            """
        )
        self.conn.commit()

    def add_contact(self, name, phone, email, address):
        cursor = self.conn.execute(
            "INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_contact(self, contact_id, name, phone, email, address):
        self.conn.execute(
            "UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?",
            (name, phone, email, address, contact_id),
        )
        self.conn.commit()

    def delete_contact(self, contact_id):
        self.conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
        self.conn.commit()

    def get_all_contacts(self):
        cursor = self.conn.execute(
            "SELECT id, name, phone, email, address FROM contacts ORDER BY name COLLATE NOCASE ASC"
        )
        return cursor.fetchall()

    def search_contacts(self, term):
        like_term = f"%{term}%"
        cursor = self.conn.execute(
            """
            SELECT id, name, phone, email, address FROM contacts
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY name COLLATE NOCASE ASC
            """,
            (like_term, like_term),
        )
        return cursor.fetchall()

    def get_contact(self, contact_id):
        cursor = self.conn.execute(
            "SELECT id, name, phone, email, address FROM contacts WHERE id=?",
            (contact_id,),
        )
        return cursor.fetchone()

    def close(self):
        self.conn.close()


# ---------------------------------------------------------------------------
# GUI layer
# ---------------------------------------------------------------------------
class ContactBookApp:
    PHONE_PATTERN = re.compile(r"^[0-9+\-\s()]{6,20}$")
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, root):
        self.root = root
        self.db = ContactDatabase()
        self.selected_contact_id = None

        self._configure_root()
        self._build_style()
        self._build_layout()
        self.refresh_list()

    # -- window setup -------------------------------------------------
    def _configure_root(self):
        self.root.title("Contact Book")
        self.root.geometry("880x520")
        self.root.minsize(760, 460)
        self.root.configure(bg="#f2f4f7")

    def _build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#f2f4f7")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f2f4f7", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#f2f4f7",
                         font=("Segoe UI", 16, "bold"), foreground="#1f2937")
        style.configure("SubHeader.TLabel", background="#ffffff",
                         font=("Segoe UI", 12, "bold"), foreground="#1f2937")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Accent.TButton",
                  background=[("!disabled", "#2563eb")],
                  foreground=[("!disabled", "#ffffff")])
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # -- layout ---------------------------------------------------------
    def _build_layout(self):
        header = ttk.Label(self.root, text="\U0001F4D6 Contact Book", style="Header.TLabel")
        header.pack(anchor="w", padx=20, pady=(15, 5))

        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=20, pady=10)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_list_panel(body)
        self._build_form_panel(body)

    # -- left panel: search + list --------------------------------------
    def _build_list_panel(self, parent):
        left = ttk.Frame(parent, style="Card.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        # search bar
        search_frame = ttk.Frame(left, style="Card.TFrame")
        search_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        search_frame.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10))
        search_entry.grid(row=0, column=0, sticky="ew", ipady=4)
        search_entry.insert(0, "")

        placeholder_label = ttk.Label(search_frame, text="\U0001F50D Search by name or phone",
                                       style="Card.TLabel", foreground="#6b7280")
        placeholder_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        clear_btn = ttk.Button(search_frame, text="Clear", command=self._clear_search)
        clear_btn.grid(row=0, column=1, padx=(8, 0))

        # count label
        self.count_label = ttk.Label(left, text="", style="Card.TLabel", foreground="#6b7280")
        self.count_label.grid(row=1, column=0, sticky="w", padx=12)

        # contact list (Treeview)
        columns = ("name", "phone")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Name")
        self.tree.heading("phone", text="Phone Number")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("phone", width=160, anchor="w")
        self.tree.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6, 12))

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=2, column=1, sticky="ns", pady=(6, 12))

        self.tree.bind("<<TreeviewSelect>>", self._on_select_contact)

        # bottom action buttons
        action_bar = ttk.Frame(left, style="Card.TFrame")
        action_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        ttk.Button(action_bar, text="Delete Selected", command=self.delete_selected).pack(side="left")
        ttk.Button(action_bar, text="Refresh", command=self.refresh_list).pack(side="left", padx=(8, 0))

    # -- right panel: add / edit form ------------------------------------
    def _build_form_panel(self, parent):
        right = ttk.Frame(parent, style="Card.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        self.form_title = ttk.Label(right, text="Add New Contact", style="SubHeader.TLabel")
        self.form_title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))

        fields_frame = ttk.Frame(right, style="Card.TFrame")
        fields_frame.grid(row=1, column=0, sticky="ew", padx=16)
        fields_frame.columnconfigure(0, weight=1)

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()

        self._add_field(fields_frame, 0, "Full Name *", self.name_var)
        self._add_field(fields_frame, 1, "Phone Number *", self.phone_var)
        self._add_field(fields_frame, 2, "Email", self.email_var)

        ttk.Label(fields_frame, text="Address", style="Card.TLabel").grid(
            row=3, column=0, sticky="w", pady=(8, 2)
        )
        self.address_text = tk.Text(fields_frame, height=5, font=("Segoe UI", 10),
                                     wrap="word", relief="solid", borderwidth=1)
        self.address_text.grid(row=4, column=0, sticky="ew")

        # buttons
        btn_frame = ttk.Frame(right, style="Card.TFrame")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=16)

        self.save_btn = ttk.Button(btn_frame, text="Add Contact", style="Accent.TButton",
                                    command=self.save_contact)
        self.save_btn.pack(side="left")

        self.update_btn = ttk.Button(btn_frame, text="Update Contact",
                                      command=self.update_contact, state="disabled")
        self.update_btn.pack(side="left", padx=(8, 0))

        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=(8, 0))

        self.status_label = ttk.Label(right, text="", style="Card.TLabel", foreground="#16a34a")
        self.status_label.grid(row=3, column=0, sticky="w", padx=16, pady=(0, 10))

    def _add_field(self, parent, row, label_text, var):
        ttk.Label(parent, text=label_text, style="Card.TLabel").grid(
            row=row * 2, column=0, sticky="w", pady=(8 if row else 0, 2)
        )
        entry = ttk.Entry(parent, textvariable=var, font=("Segoe UI", 10))
        entry.grid(row=row * 2 + 1, column=0, sticky="ew", ipady=4)

    # -- data operations --------------------------------------------------
    def refresh_list(self, contacts=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if contacts is None:
            contacts = self.db.get_all_contacts()

        for contact_id, name, phone, email, address in contacts:
            self.tree.insert("", "end", iid=str(contact_id), values=(name, phone))

        self.count_label.config(text=f"{len(contacts)} contact(s)")

    def _on_search_changed(self, *args):
        term = self.search_var.get().strip()
        if term:
            results = self.db.search_contacts(term)
        else:
            results = self.db.get_all_contacts()
        self.refresh_list(results)

    def _clear_search(self):
        self.search_var.set("")

    def _on_select_contact(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        contact_id = int(selection[0])
        contact = self.db.get_contact(contact_id)
        if not contact:
            return

        self.selected_contact_id = contact_id
        _, name, phone, email, address = contact
        self.name_var.set(name)
        self.phone_var.set(phone)
        self.email_var.set(email or "")
        self.address_text.delete("1.0", "end")
        self.address_text.insert("1.0", address or "")

        self.form_title.config(text=f"Editing: {name}")
        self.save_btn.config(state="disabled")
        self.update_btn.config(state="normal")

    def _validate_form(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()

        if not name:
            messagebox.showwarning("Validation Error", "Name is required.")
            return None
        if not phone or not self.PHONE_PATTERN.match(phone):
            messagebox.showwarning(
                "Validation Error",
                "Please enter a valid phone number (digits, spaces, +, -, parentheses only)."
            )
            return None
        if email and not self.EMAIL_PATTERN.match(email):
            messagebox.showwarning("Validation Error", "Please enter a valid email address.")
            return None

        address = self.address_text.get("1.0", "end").strip()
        return name, phone, email, address

    def save_contact(self):
        data = self._validate_form()
        if not data:
            return
        name, phone, email, address = data
        self.db.add_contact(name, phone, email, address)
        self._show_status(f"Added '{name}' to contacts.")
        self.clear_form()
        self._on_search_changed()

    def update_contact(self):
        if self.selected_contact_id is None:
            return
        data = self._validate_form()
        if not data:
            return
        name, phone, email, address = data
        self.db.update_contact(self.selected_contact_id, name, phone, email, address)
        self._show_status(f"Updated '{name}'.")
        self.clear_form()
        self._on_search_changed()

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a contact to delete.")
            return

        contact_id = int(selection[0])
        contact = self.db.get_contact(contact_id)
        name = contact[1] if contact else "this contact"

        confirmed = messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete '{name}'?"
        )
        if confirmed:
            self.db.delete_contact(contact_id)
            self._show_status(f"Deleted '{name}'.")
            self.clear_form()
            self._on_search_changed()

    def clear_form(self):
        self.selected_contact_id = None
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_text.delete("1.0", "end")
        self.form_title.config(text="Add New Contact")
        self.save_btn.config(state="normal")
        self.update_btn.config(state="disabled")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def _show_status(self, message):
        self.status_label.config(text=message)
        self.root.after(3500, lambda: self.status_label.config(text=""))

    def on_close(self):
        self.db.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ContactBookApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
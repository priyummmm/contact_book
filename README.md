# contact_book
# 📖 Contact Book

A simple, clean desktop **Contact Management System** built with **Python (Tkinter)** and **SQLite**. Add, search, update, and delete contacts through a two-panel graphical interface — no external dependencies, no setup hassle.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-07405e?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🗂️ **Store contact details** — name, phone number, email, and address
- ➕ **Add new contacts** through a simple form
- 📋 **View all contacts** in a searchable, sortable list
- 🔍 **Live search** by name or phone number as you type
- ✏️ **Update** any existing contact's details
- 🗑️ **Delete** contacts with a confirmation prompt
- 💾 **Persistent storage** — all data saved locally in a SQLite database (`contacts.db`)
- 🎨 **Clean, user-friendly interface** styled with `ttk`

---

## 🖥️ Preview

> The app opens with a contact list on the left and an add/edit form on the right.

```
┌─────────────────────────────┬───────────────────────────┐
│  🔍 Search by name or phone │      Add New Contact       │
├─────────────────────────────┤                             │
│  Name          Phone        │  Full Name *  [________]   │
│  ─────────────────────────  │  Phone No. *  [________]   │
│  Aditi Sharma  98765xxxxx   │  Email        [________]   │
│  Rohan Verma   91234xxxxx   │  Address      [________]   │
│  ...                        │               [________]   │
│                              │  [Add Contact] [Update]    │
│  [Delete Selected] [Refresh]│                             │
└─────────────────────────────┴───────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component     | Technology              |
|---------------|--------------------------|
| Language      | Python 3                |
| GUI           | Tkinter / ttk            |
| Database      | SQLite3 (built-in)       |
| Validation    | Python `re` module       |

No third-party packages required — everything runs on Python's standard library.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher installed on your system

### Installation

```bash
# Clone the repository
git clone https://github.com/priyummmm/contact-book.git
cd contact-book

# Run the application
python contact_book.py
```

That's it — no `pip install` needed. A `contacts.db` file will be created automatically in the same folder the first time you run the app.

---

## 📁 Project Structure

```
contact-book/
├── contact_book.py     # Main application (GUI + database logic)
├── contacts.db          # SQLite database (auto-created on first run)
└── README.md            # Project documentation
```

---

## 🧩 How It Works

- **`ContactDatabase`** — handles all SQLite operations (create, insert, update, delete, search).
- **`ContactBookApp`** — builds the Tkinter interface and wires up user actions (buttons, search box, list selection) to the database layer.

Selecting a contact from the list loads its details into the form for editing; clearing the form returns it to "Add" mode.

---

## 🔮 Future Enhancements

- [ ] Contact photos and group/category tagging
- [ ] Import/export via CSV or vCard (`.vcf`)
- [ ] Sort contacts by name or date added
- [ ] Dark mode theme
- [ ] Packaged as a standalone `.exe` / `.app` using PyInstaller

---

## 👤 Author

**Priyam Singh**
- GitHub: [@priyummmm](https://github.com/priyummmm)
- LinkedIn: [priyamsingh-](https://linkedin.com/in/priyamsingh-)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

⭐ If you found this project useful, consider giving it a star!

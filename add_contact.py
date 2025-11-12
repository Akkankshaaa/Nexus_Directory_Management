import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def open_add_contact_window(root, refresh_callback):
    popup = tk.Toplevel(root)
    popup.title("Add Contact")
    popup.geometry("400x450")
    popup.configure(bg="#F6F2FF")

    tk.Label(popup, text="Full Name:", bg="#F6F2FF").pack(pady=5)
    name_entry = ttk.Entry(popup, width=35)
    name_entry.pack()

    tk.Label(popup, text="Phone:", bg="#F6F2FF").pack(pady=5)
    phone_entry = ttk.Entry(popup, width=35)
    phone_entry.pack()

    tk.Label(popup, text="Email:", bg="#F6F2FF").pack(pady=5)
    email_entry = ttk.Entry(popup, width=35)
    email_entry.pack()

    tk.Label(popup, text="Birthday (DD-MM-YYYY):", bg="#F6F2FF").pack(pady=5)
    birthday_entry = ttk.Entry(popup, width=35)
    birthday_entry.pack()

    tk.Label(popup, text="Category:", bg="#FFE8D6").pack(pady=5)
    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(popup, textvariable=category_var, values=[
        "Family", "Friend", "College", "Work", "Online", "Other"
    ], state="readonly", width=32)
    category_dropdown.pack()
    category_dropdown.current(0)  # Default selection

    tk.Label(popup, text="Notes:", bg="#F6F2FF").pack(pady=5)
    notes_entry = tk.Text(popup, width=35, height=4)
    notes_entry.pack()

    favorite_var = tk.IntVar()
    tk.Checkbutton(popup, text="⭐ Favorite", variable=favorite_var, bg="#F6F2FF").pack(pady=8)

    def save_contact():
        name = name_entry.get()
        phone = phone_entry.get()
        email = email_entry.get()
        birthday = birthday_entry.get()
        category = category_var.get()

        notes = notes_entry.get("1.0", tk.END).strip()
        favorite = favorite_var.get()

        if name.strip() == "":
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        # STRICT 10-DIGIT PHONE VALIDATION
        if phone:
            if not phone.isdigit():
                messagebox.showerror("Invalid Phone", "Phone number must contain only digits.")
                return
            if len(phone) != 10:
                messagebox.showerror("Invalid Phone", "Phone number must be exactly 10 digits.")
                return
        # STRICT GMAIL VALIDATION
        if email:
            if not email.endswith("@gmail.com"):
                messagebox.showerror("Invalid Email", "Only Gmail addresses are allowed (example: name@gmail.com).")
                return
            if " " in email or email.count("@") != 1 or email.index("@") == 0:
                messagebox.showerror("Invalid Email", "Please enter a valid Gmail address.")
                return

        conn = sqlite3.connect("data/contacts.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, phone, email, birthday, category, favorite, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (name, phone, email, birthday, category, favorite, notes))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"{name} added successfully 🤍")
        popup.destroy()
        refresh_callback()  # refresh table after saving

    ttk.Button(popup, text="Save Contact", command=save_contact).pack(pady=15)

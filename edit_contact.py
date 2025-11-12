import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def open_edit_contact_window(root, selected_item, refresh_callback):
    values = selected_item  # row values from table
    name_old = values[0]  # we use name to find the correct row

    popup = tk.Toplevel(root)
    popup.title("Edit Contact")
    popup.geometry("400x450")
    popup.configure(bg="#FFE8D6")

    tk.Label(popup, text="Full Name:", bg="#FFE8D6").pack(pady=5)
    name_entry = ttk.Entry(popup, width=35)
    name_entry.insert(0, values[0])
    name_entry.pack()

    tk.Label(popup, text="Phone:", bg="#FFE8D6").pack(pady=5)
    phone_entry = ttk.Entry(popup, width=35)
    phone_entry.insert(0, values[1])
    phone_entry.pack()

    tk.Label(popup, text="Email:", bg="#FFE8D6").pack(pady=5)
    email_entry = ttk.Entry(popup, width=35)
    email_entry.insert(0, values[2])
    email_entry.pack()

    tk.Label(popup, text="Birthday:", bg="#FFE8D6").pack(pady=5)
    birthday_entry = ttk.Entry(popup, width=35)
    birthday_entry.insert(0, values[3])
    birthday_entry.pack()

    tk.Label(popup, text="Category:", bg="#FFE8D6").pack(pady=5)
    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(popup, textvariable=category_var, values=[
        "Family", "Friend", "College", "Work", "Online", "Other"
    ], state="readonly", width=32)
    category_dropdown.pack()
    category_dropdown.set(values[4])

    favorite_var = tk.IntVar(value=values[5])
    tk.Checkbutton(popup, text="⭐ Favorite", variable=favorite_var, bg="#FFE8D6").pack(pady=8)

    def save_changes():
        name = name_entry.get()
        phone = phone_entry.get()
        email = email_entry.get()
        birthday = birthday_entry.get()
        category = category_var.get()
        favorite = favorite_var.get()

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
        cursor.execute("""
            UPDATE contacts
            SET name=?, phone=?, email=?, birthday=?, category=?, favorite=?
            WHERE name=?
        """, (name, phone, email, birthday, category, favorite, name_old))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Contact updated successfully 🤍")
        popup.destroy()
        refresh_callback()

    ttk.Button(popup, text="Save Changes", command=save_changes).pack(pady=15)

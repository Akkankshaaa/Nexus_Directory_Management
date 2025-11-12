# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3, datetime

from database import connect_db
from add_contact import open_add_contact_window
from edit_contact import open_edit_contact_window

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "contacts.db")


# ---------- App Colors (Professional dark blue) ----------
BG_DARK = "#0F172A"   # page background
CARD = "#111827"      # panel
ACCENT = "#1D4ED8"    # buttons/accents
FG = "#E5E7EB"

# ---------- DB init ----------
connect_db()

# ---------- Root ----------
root = tk.Tk()
root.title("Nexus Directory Management")
root.geometry("900x550")
root.resizable(False, False)

# ---------- Background image (optional) ----------
try:
    bg_image = Image.open("data/bg.jpg")
    bg_image = bg_image.resize((900, 550), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception:
    root.configure(bg=BG_DARK)

# ---------- Style ----------
style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background=CARD)
style.configure("TLabel", background=CARD, foreground=FG)
style.configure("TButton", padding=6)
style.configure("Accent.TButton", foreground="white")
style.map("Accent.TButton", background=[("!disabled", ACCENT), ("active", "#2563EB")])

# ---------- Main frame ----------
main_frame = ttk.Frame(root, padding=12, style="TFrame")
main_frame.place(x=20, y=20, width=860, height=510)

# ---------- Top bar ----------
top_frame = ttk.Frame(main_frame, style="TFrame")
top_frame.pack(fill="x")

title_lbl = ttk.Label(top_frame, text="Nexus Directory Protocol", font=("Segoe UI", 14, "bold"))
title_lbl.pack(side=tk.LEFT)

# ---------- Search row ----------
search_frame = ttk.Frame(main_frame, style="TFrame")
search_frame.pack(pady=8, fill="x")

search_entry = ttk.Entry(search_frame, width=40)
search_entry.pack(side=tk.LEFT, padx=6)

def do_search():
    q = search_entry.get().strip()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    like = f"%{q}%"
    cur.execute("""
        SELECT name, phone, email, birthday, category, favorite
          FROM contacts
         WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR category LIKE ?
         ORDER BY name
    """, (like, like, like, like))
    rows = cur.fetchall()
    conn.close()
    fill_table(rows)

search_btn = ttk.Button(search_frame, text="Search", command=do_search, style="Accent.TButton")
search_btn.pack(side=tk.LEFT, padx=4)

def show_all():
    refresh_contacts()

show_all_btn = ttk.Button(search_frame, text="Show All", command=show_all)
show_all_btn.pack(side=tk.LEFT, padx=4)

def show_favorites():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, phone, email, birthday, category, favorite
          FROM contacts WHERE favorite=1 ORDER BY name
    """)
    rows = cur.fetchall()
    conn.close()
    fill_table(rows)

fav_btn = ttk.Button(search_frame, text="⭐ Favorites", command=show_favorites)
fav_btn.pack(side=tk.LEFT, padx=4)

# ---------- Table ----------
columns = ("name", "phone", "email", "birthday", "category", "favorite")
table = ttk.Treeview(main_frame, columns=columns, show="headings", height=16)
for col in columns:
    table.heading(col, text=col.capitalize())
    table.column(col, width=130 if col != "favorite" else 80, anchor="center")
table.pack(fill="both", expand=True, pady=6)

def fill_table(rows):
    for r in table.get_children():
        table.delete(r)
    for row in rows:
        # pretty print favorite as ⭐/blank
        row = list(row)
        row[5] = "⭐" if str(row[5]) == "1" else ""
        table.insert("", tk.END, values=row)

def refresh_contacts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, phone, email, birthday, category, favorite
          FROM contacts
         ORDER BY name
    """)
    rows = cur.fetchall()
    conn.close()
    fill_table(rows)

# ---------- Buttons ----------
btn_frame = ttk.Frame(main_frame, style="TFrame")
btn_frame.pack(pady=8)

def add_contact():
    open_add_contact_window(root, refresh_contacts)

def edit_contact():
    sel = table.focus()
    if not sel:
        messagebox.showwarning("Select", "Choose a contact to edit.")
        return
    values = table.item(sel, "values")
    # values favorite shows ⭐ — map back to 1/0 for editor’s initial state
    vlist = list(values)
    vlist[5] = 1 if vlist[5] == "⭐" else 0
    open_edit_contact_window(root, tuple(vlist), refresh_contacts)

def delete_contact():
    sel = table.focus()
    if not sel:
        messagebox.showwarning("Select", "Choose a contact to delete.")
        return
    name = table.item(sel, "values")[0]
    if not messagebox.askyesno("Confirm", f"Delete {name}?"):
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE name=?", (name,))
    conn.commit()
    conn.close()
    refresh_contacts()
    messagebox.showinfo("Deleted", f"{name} removed.")

ttk.Button(btn_frame, text="Add Contact", command=add_contact, style="Accent.TButton").pack(side=tk.LEFT, padx=6)
ttk.Button(btn_frame, text="Edit Contact", command=edit_contact).pack(side=tk.LEFT, padx=6)
ttk.Button(btn_frame, text="Delete", command=delete_contact).pack(side=tk.LEFT, padx=6)
ttk.Button(btn_frame, text="Refresh", command=refresh_contacts).pack(side=tk.LEFT, padx=6)

# ---------- Birthday reminders ----------


def notify_today_birthdays():
    global _last_reminder_date
    today = datetime.date.today()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, birthday FROM contacts WHERE birthday IS NOT NULL AND birthday!=''")
    rows = cur.fetchall()
    conn.close()

    birthdays_today = []

    for name, birthday in rows:
        for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
            try:
                bd = datetime.datetime.strptime(birthday, fmt).date()
                break
            except:
                bd = None
        if not bd:
            continue

        # Compare only month & day
        if bd.month == today.month and bd.day == today.day:
            birthdays_today.append(name)

    now_date = today.isoformat()

    if birthdays_today and _last_reminder_date != now_date:
        names = ", ".join(birthdays_today)
        messagebox.showinfo("🎂 Birthday Today!", f"Wish {names} ✨")
        _last_reminder_date = now_date

    # check every 1 hour (3600000 ms); for quick testing use 5000 (5 sec)
    root.after(5000, notify_today_birthdays)


# ---------- First load ----------
refresh_contacts()
_last_reminder_date = None
notify_today_birthdays()
root.mainloop()


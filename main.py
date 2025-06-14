import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random
import gspread
import matplotlib.pyplot as plt
from oauth2client.service_account import ServiceAccountCredentials
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

NAMES = ["NAKUL", "SAQIB", "CHETHAN"]

def pick_random():
    selected = random.choice(NAMES)
    messagebox.showinfo("Selected Member", f"Congratulations {selected}, You are selected!")

def connect_sheet(tab_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "nacsa-treasure-vault-afc6da1241e6.json", scope)
    client = gspread.authorize(creds)
    return client.open("NACSA Treasure Vault").worksheet(tab_name)

def populate_treeview(tree, sheet_name):
    sheet = connect_sheet(sheet_name)
    records = sheet.get_all_records()
    tree.delete(*tree.get_children())
    if not records:
        return
    tree["columns"] = list(records[0].keys())
    tree["show"] = "headings"
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    for row in records:
        tree.insert("", "end", values=list(row.values()))

def refresh_all():
    populate_treeview(tree1, "Monthly Records")
    populate_treeview(tree2, "Vault Summary")
    populate_treeview(tree3, "Bonus & History")
    draw_graph()

def draw_graph():
    sheet = connect_sheet("Vault Summary")
    records = sheet.get_all_records()
    months = [row['Month'] for row in records if 'Month' in row and 'Total Contributions' in row]
    values = [int(row['Total Contributions'].replace('₹', '').strip()) for row in records if 'Total Contributions' in row]
    fig = plt.Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(months, values, marker='o', color='#735bff')
    ax.set_title('VAULT MONEY GROWTH')
    ax.set_xlabel('Month')
    ax.set_ylabel('Money')
    for widget in graph_frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("NACSA Treasure Vault")
root.geometry("1600x800")
root.resizable(True, True)

# Background Image
bg_image = Image.open("background.jpg")
bg_image = bg_image.resize((1600, 800), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Top Button Panel
button_frame = tk.Frame(root, bg="#000000")
button_frame.pack(pady=10)

tk.Button(button_frame, text="🎲 Pick Random Member", command=pick_random,
          bg="black", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=10)
tk.Button(button_frame, text="🔄 Refresh All", command=refresh_all,
          bg="green", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=10)

# 2x2 Grid Layout Frame
grid_frame = tk.Frame(root, bg="black")
grid_frame.pack(padx=10, pady=5, fill="both", expand=True)

# Reusable function to create treeview with scrollbars
def create_scrollable_treeview(parent):
    frame = tk.Frame(parent)
    tree = ttk.Treeview(frame, xscrollcommand=None, yscrollcommand=None)
    tree.pack(side="left", fill="both", expand=True)

    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    y_scroll.pack(side="right", fill="y")
    tree.configure(yscrollcommand=y_scroll.set)

    x_scroll = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
    x_scroll.pack(fill="x")
    tree.configure(xscrollcommand=x_scroll.set)

    return frame, tree

# --- Section 1: Monthly Records --- #
frame1 = tk.Frame(grid_frame, bd=2, relief="ridge", bg="#F5F4EB")
frame1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
tk.Label(frame1, text="📘 MONTHLY RECORDS", font=("Arial", 12, "bold"), bg="lightblue").pack()
tree_frame1, tree1 = create_scrollable_treeview(frame1)
tree_frame1.pack(fill="both", expand=True)

# --- Section 2: Vault Trend (Graph) --- #
graph_frame = tk.Frame(grid_frame, bd=2, relief="ridge", bg="#F5F4EB")
graph_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
tk.Label(graph_frame, text="📈 VAULT TREND (Monthly)", font=("Arial", 12, "bold"), bg="lightgreen").pack()

# --- Section 3: Vault Summary --- #
frame2 = tk.Frame(grid_frame, bd=2, relief="ridge", bg="#F5F4EB")
frame2.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
tk.Label(frame2, text="📗 VAULT SUMMARY", font=("Arial", 12, "bold"), bg="lightyellow").pack()
tree_frame2, tree2 = create_scrollable_treeview(frame2)
tree_frame2.pack(fill="both", expand=True)

# --- Section 4: Bonus & History --- #
frame3 = tk.Frame(grid_frame, bd=2, relief="ridge", bg="#F5F4EB")
frame3.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
tk.Label(frame3, text="📙 MEMBER CONTRIBUTION HISTORY", font=("Arial", 12, "bold"), bg="lightpink").pack()
tree_frame3, tree3 = create_scrollable_treeview(frame3)
tree_frame3.pack(fill="both", expand=True)

# Grid Weights for responsiveness
grid_frame.grid_columnconfigure(0, weight=1)
grid_frame.grid_columnconfigure(1, weight=1)
grid_frame.grid_rowconfigure(0, weight=1)
grid_frame.grid_rowconfigure(1, weight=1)

# Load initial data
refresh_all()
root.mainloop()

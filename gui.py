import os
import io
import base64
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk

from client import Client

# Prompt user login with limited attempts
def login_prompt(max_attempts=3):
    global client
    global username
    attempts = 0
    temp_client = Client()
    temp_client.connect()
    login_root = tk.Tk()
    login_root.withdraw()

    while attempts < max_attempts:
        username = simpledialog.askstring("Login", "Enter username:", parent=login_root)
        if username is None:
            temp_client.client.send("EXIT".encode())
            temp_client.client.close()
            login_root.destroy()
            return False

        password = simpledialog.askstring("Login", "Enter password:", show='*', parent=login_root)
        if password is None:
            temp_client.client.send("EXIT".encode())
            temp_client.client.close()
            login_root.destroy()
            return False

        temp_client.client.send(username.encode("utf-8"))
        temp_client.client.send(password.encode("utf-8"))
        auth = temp_client.client.recv(temp_client.BUFSIZE).decode().strip()

        if auth == "True":
            messagebox.showinfo("Login", "Login successful!", parent=login_root)
            login_root.destroy()
            client = temp_client
            return True
        else:
            attempts += 1
            messagebox.showerror("Login Failed", f"Invalid credentials. Attempts left: {max_attempts - attempts}", parent=login_root)

    messagebox.showwarning("Access Denied", "Too many failed attempts.", parent=login_root)
    temp_client.client.send("EXIT".encode())
    temp_client.client.close()
    login_root.destroy()
    return False

# Safely send command to server
def send_command_safe(command):
    try:
        if client is None:
            return "Error: Not connected to server"
        return client.send_command(command)
    except Exception as e:
        return f"Error sending command: {e}"

# Search for product image file
def find_image_file(product_id):
    base_path = "images"
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        img_path = os.path.join(base_path, f"product_{product_id}{ext}")
        if os.path.isfile(img_path):
            return img_path
    return None

# Display products with add-to-cart option
def view_products():
    show_products_view()
    for widget in product_frame.winfo_children():
        widget.destroy()

    response = send_command_safe("VIEW")
    lines = response.strip().split("\n")[2:]

    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        try:
            pid = int(parts[0])
            name = " ".join(parts[1:-2])
            price = parts[-2].replace("$", "")
            stock = parts[-1]
        except:
            continue

        frame = tk.Frame(product_frame, bd=2, relief=tk.RIDGE, padx=10, pady=10, bg="white")
        frame.pack(padx=10, pady=5, fill="x")

        img_path = find_image_file(pid)
        if img_path:
            image = Image.open(img_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)
            img_label = tk.Label(frame, image=photo)
            img_label.image = photo
            img_label.pack(side="left")

        details = tk.Label(frame, text=f"{name}\nPrice: ${price} | Stock: {stock}", font=("Arial", 12), justify="left", bg="white")
        details.pack(side="left", padx=10)

        qty_label = tk.Label(frame, text="Qty:", bg="white")
        qty_label.pack(side="left")

        qty_entry = tk.Entry(frame, width=5)
        qty_entry.pack(side="left", padx=5)

        def add_func(pid=pid, entry=qty_entry):
            quantity = entry.get().strip()
            if not quantity.isdigit():
                messagebox.showerror("Error", "Invalid quantity.")
                return
            result = send_command_safe(f"ADD {pid} {quantity}")
            messagebox.showinfo("Info", result)
            view_products()

        add_btn = tk.Button(frame, text="Add to Cart", command=add_func)
        add_btn.pack(side="left", padx=10)

# Display cart contents with option to remove items
def view_cart():
    show_products_view()
    for widget in product_frame.winfo_children():
        widget.destroy()

    response = send_command_safe("CART")
    lines = response.strip().split("\n")[2:]

    if not lines:
        messagebox.showinfo("Cart", "Your cart is empty.")
        return

    for line in lines:
        if not line.strip():
            continue
        parts = line.strip().split()
        try:
            pid = int(parts[0])
            name = " ".join(parts[1:-2])
            total_price = parts[-2].replace("$", "")
            qty = parts[-1]
        except:
            continue

        frame = tk.Frame(product_frame, bd=2, relief=tk.RIDGE, padx=10, pady=5, bg="white")
        frame.pack(padx=10, pady=5, fill="x")

        info = f"{name}\nQty: {qty} | Total: ${total_price}"
        tk.Label(frame, text=info, font=("Arial", 12), justify="left", bg="white").pack(side="left", padx=10)

        def remove_func(pid=pid, qty=qty):
            result = send_command_safe(f"REMOVE {pid} {qty}")
            messagebox.showinfo("Removed", result)
            view_cart()

        tk.Button(frame, text="🗑️", command=remove_func, font=("Arial", 12)).pack(side="right", padx=10)

# View transaction history and display sales chart
def view_history():
    show_text_display()
    history_text = send_command_safe("HISTORY")
    update_display(history_text)
    try:
        if client is None:
            return
        chart_data = client.send_command_large("CHART")
        if chart_data == "NO_CHART":
            return
        image_bytes = base64.b64decode(chart_data)
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail((600, 400), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        text_display.config(state='normal')
        text_display.insert(tk.END, "\n\n📊 Sales Chart:\n")
        text_display.image_create(tk.END, image=photo)
        text_display.insert(tk.END, "\n")
        text_display.image = photo
        text_display.config(state='disabled')
    except Exception as e:
        text_display.config(state='normal')
        text_display.insert(tk.END, f"\n[Error loading chart: {e}]\n")
        text_display.config(state='disabled')

# Allow admin to update stock quantities
def edit_stock():
    show_products_view()
    for widget in product_frame.winfo_children():
        widget.destroy()

    response = send_command_safe("VIEW")
    lines = response.strip().split("\n")[2:]

    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        try:
            pid = int(parts[0])
            name = " ".join(parts[1:-2])
            price = parts[-2].replace("$", "")
            stock = parts[-1]
        except:
            continue

        frame = tk.Frame(product_frame, bd=2, relief=tk.RIDGE, padx=10, pady=10, bg="white")
        frame.pack(padx=10, pady=5, fill="x")

        img_path = find_image_file(pid)
        if img_path:
            image = Image.open(img_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)
            img_label = tk.Label(frame, image=photo)
            img_label.image = photo
            img_label.pack(side="left")

        details = tk.Label(frame, text=f"{name}\nPrice: ${price} | Stock: {stock}", font=("Arial", 12), justify="left", bg="white")
        details.pack(side="left", padx=10)

        qty_label = tk.Label(frame, text="New Stock:", bg="white")
        qty_label.pack(side="left")

        qty_entry = tk.Entry(frame, width=5)
        qty_entry.pack(side="left", padx=5)

        def update_stock_func(pid=pid, entry=qty_entry):
            quantity = entry.get().strip()
            if not quantity.isdigit():
                messagebox.showerror("Error", "Invalid quantity.")
                return
            result = send_command_safe(f"CHANGE_STOCK {pid} {quantity}")
            messagebox.showinfo("Stock Updated", result)
            edit_stock()

        tk.Button(frame, text="Update Stock", command=update_stock_func).pack(side="left", padx=10)

# Confirm checkout and show receipt
def checkout():
    receipt = send_command_safe("RECEIPT")
    if receipt == "Empty":
        messagebox.showinfo("Cart Empty", "Your cart is empty. Cannot proceed to checkout.")
        return

    show_text_display()

    def confirm_action():
        checkout_button_frame.destroy()
        txt_display.delete(1.0, tk.END)
        response = send_command_safe("CHECKOUT")
        txt_display.insert(tk.END, response)
        if "The cart is empty" not in response:
            tk.Label(
                checkout_window,
                text="✅ Purchase completed successfully!\nPlease exit this window.",
                font=("Arial", 12, "bold"),
                fg="green",
                bg="#FFB4B4"
            ).pack(pady=10)
            update_display(greeting)

    def cancel_action():
        checkout_window.destroy()

    checkout_window = tk.Toplevel(root)
    checkout_window.title("Checkout Window")
    checkout_window.geometry("800x600")

    txt_display = tk.Text(
        checkout_window,
        width=80, height=20,
        padx=10, pady=10,
        font=("Courier New", 10),
        background="#FFB4B4"
    )
    txt_display.insert(tk.END, "Do you want to confirm your purchase?\n\n")
    txt_display.insert(tk.END, receipt)
    txt_display.pack(padx=20, pady=20)

    checkout_button_frame = tk.Frame(checkout_window)
    checkout_button_frame.pack(pady=10)
    tk.Button(checkout_button_frame, text="Yes", width=15, command=confirm_action).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(checkout_button_frame, text="No", width=15, command=cancel_action).grid(row=0, column=1, padx=5, pady=5)

# GUI helpers
def clear_display():
    show_text_display()
    text_display.config(state='normal')
    text_display.delete(1.0, tk.END)
    text_display.config(state='disabled')

def update_display(text):
    text_display.config(state='normal')
    text_display.delete(1.0, tk.END)
    text_display.insert(tk.END, text)
    text_display.config(state='disabled')

def show_products_view():
    text_display.pack_forget()
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    scrollbar.pack(side="right", fill="y")

def show_text_display():
    canvas.pack_forget()
    scrollbar.pack_forget()
    text_display.pack(padx=20, pady=20)

def on_closing():
    try:
        if client:
            client.send_command("EXIT")
            client.client.close()
    except:
        pass
    root.destroy()

# Main Application Start
client = None
username = None
if not login_prompt():
    exit()

root = tk.Tk()
root.geometry("1000x800")
root.title("Smart Vending Machine")
root.configure(background="#E14434")

text_display = tk.Text(
    root,
    width=100, height=30,
    padx=20, pady=20,
    font=("Courier New", 10),
    background="#FFB4B4"
)
text_display.config(state='disabled')
text_display.pack(padx=20, pady=20)

canvas = tk.Canvas(root, height=600, background="#FFB4B4")
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
product_frame = ttk.Frame(canvas)
product_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=product_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack_forget()
scrollbar.pack_forget()

# Buttons
button_frame = tk.Frame()
button_frame.pack(pady=10)
tk.Button(button_frame, text="View Products", width=15, command=view_products).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="View Cart", width=15, command=view_cart).grid(row=0, column=1, padx=5, pady=5)
if username == "admin":
    tk.Button(button_frame, text="Order History", width=15, command=view_history).grid(row=0, column=2, padx=5, pady=5)
    tk.Button(button_frame, text="Edit Stock", width=15, command=edit_stock).grid(row=0, column=3, padx=5, pady=5)
tk.Button(button_frame, text="Checkout", width=15, command=checkout).grid(row=1, column=0, padx=5, pady=10)
tk.Button(button_frame, text="Clear Display", width=15, command=clear_display).grid(row=1, column=1, padx=5, pady=10)
tk.Button(button_frame, text="Exit", width=15, command=on_closing).grid(row=1, column=2, padx=5, pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
greeting = """Welcome to the Smart Vending Machine!\nClick 'View Products' to start browsing."""
update_display(greeting)
root.mainloop()

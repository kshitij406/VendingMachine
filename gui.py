import os
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Assuming 'client.py' exists and is correctly implemented
from client import Client

# --- CORE APPLICATION LOGIC (Login and Server Communication are unchanged) ---

def login_prompt(max_attempts=3):
    global client, username
    attempts = 0
    temp_client = Client()
    try:
        temp_client.connect()
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
        return False

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
            messagebox.showerror("Login Failed", f"Invalid credentials. Attempts left: {max_attempts - attempts}",
                                 parent=login_root)

    messagebox.showwarning("Access Denied", "Too many failed attempts.", parent=login_root)
    temp_client.client.send("EXIT".encode())
    temp_client.client.close()
    login_root.destroy()
    return False

def send_command_safe(command):
    try:
        if client is None:
            return "Error: Not connected to server"

        response = client.send_command(command)

        # 🛡️ If response is suspicious (chart noise), retry once
        if "PNG" in response or response.count("\n") < 2 or "IDAT" in response:
            print("[WARN] Suspected corrupted response, retrying...")
            response = client.send_command(command)

        return response

    except Exception as e:
        messagebox.showerror("Connection Error", f"Lost connection to the server: {e}")
        on_closing()
        return f"Error sending command: {e}"

def find_image_file(product_id):
    base_path = "images"
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        img_path = os.path.join(base_path, f"product_{product_id}{ext}")
        if os.path.isfile(img_path):
            return img_path
    return None

# --- GUI FUNCTIONS (UI/UX Refactored) ---
def view_products():
    """Displays all products with an option to add them to the cart."""
    show_products_view()
    product_canvas_container.pack_forget()
    product_canvas_container.pack(fill="both", expand=True)
    clear_product_frame()

    response = send_command_safe("VIEW")

    # 🛡️ Validate proper format before trying to parse
    if not response or "ProductID" not in response or "Price" not in response:
        ttk.Label(product_frame, text="⚠️ Failed to load product list.",
                  font=("Segoe UI", 14), style="Header.TLabel").pack(pady=20)
        return

    lines = response.strip().split("\n")[2:]  # Skip the headers

    for line in lines:
        if not line.strip():
            continue
        try:
            parts = line.split()
            pid = int(parts[0])
            name = " ".join(parts[1:-2])
            price = parts[-2]
            stock = parts[-1]
        except (ValueError, IndexError):
            continue  # 🧯 skip malformed lines

        item_frame = ttk.Frame(product_frame, padding=10, relief="solid", borderwidth=1, style="Card.TFrame")
        item_frame.pack(padx=10, pady=6, fill="x")
        item_frame.columnconfigure(1, weight=1)

        # Product Image
        img_path = find_image_file(pid)
        img_label = ttk.Label(item_frame, style="Card.TLabel")
        if img_path:
            try:
                image = Image.open(img_path)
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)
                img_label.image = photo
                img_label.configure(image=photo)
            except Exception:
                img_label.configure(text="No Img", font=("Segoe UI", 9))
        img_label.grid(row=0, column=0, rowspan=2, padx=(0, 15), sticky="w")

        # Product Details
        details_text = f"{name}\nPrice: {price} | Stock: {stock}"
        ttk.Label(item_frame, text=details_text, font=("Segoe UI", 11), style="Card.TLabel", justify="left")\
            .grid(row=0, column=1, rowspan=2, sticky="w")

        # Action Frame (for quantity and button)
        action_frame = ttk.Frame(item_frame, style="Card.TFrame")
        action_frame.grid(row=0, column=2, rowspan=2, sticky="e")

        ttk.Label(action_frame, text="Qty:", style="Card.TLabel").pack(side="left", padx=(0, 5))
        qty_entry = ttk.Entry(action_frame, width=5, font=("Segoe UI", 10))
        qty_entry.pack(side="left", padx=5)

        def add_func(p=pid, entry=qty_entry):
            quantity = entry.get().strip()
            if not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showerror("Error", "Please enter a valid, positive quantity.")
                return
            result = send_command_safe(f"ADD {p} {quantity}")
            messagebox.showinfo("Info", result)
            view_products()

        add_btn = ttk.Button(action_frame, text="Add to Cart", command=add_func)
        add_btn.pack(side="left", padx=5)

    product_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0)

def view_cart():
    """Displays items currently in the user's cart."""
    show_products_view()
    product_canvas_container.pack_forget()
    product_canvas_container.pack(fill="both", expand=True)
    clear_product_frame()

    response = send_command_safe("CART")

    # 🛡️ Protect against wrong format / polluted history data
    if "Cart is empty." in response or "Cart:" not in response:
        ttk.Label(product_frame, text="Your cart is empty. 🛒",
                  font=("Segoe UI", 14), style="Header.TLabel").pack(pady=20)
        return

    lines = response.strip().split("\n")
    header = lines[0]
    items = lines[2:]

    ttk.Label(product_frame, text=header, font=("Segoe UI", 14, "bold"),
              style="Header.TLabel").pack(pady=(5, 15), fill="x")

    for line in items:
        if not line.strip():
            continue
        try:
            parts = line.strip().split()
            pid = int(parts[0])
            name = " ".join(parts[1:-2])
            total_price = parts[-2]
            qty = parts[-1]
        except (ValueError, IndexError):
            continue  # 🧯 Don’t crash on garbage data

        item_frame = ttk.Frame(product_frame, padding=10, relief="solid", borderwidth=1, style="Card.TFrame")
        item_frame.pack(padx=10, pady=6, fill="x")
        item_frame.columnconfigure(0, weight=1)

        info = f"{name}\nQuantity: {qty} | Total: {total_price}"
        ttk.Label(item_frame, text=info, font=("Segoe UI", 11), justify="left", style="Card.TLabel").grid(
            row=0, column=0, sticky="w")

        def remove_func(p=pid, q=qty):
            result = send_command_safe(f"REMOVE {p} {q}")
            messagebox.showinfo("Removed", result)
            view_cart()

        remove_btn = ttk.Button(item_frame, text="🗑️ Remove", command=remove_func, style="Danger.TButton")
        remove_btn.grid(row=0, column=1, sticky="e", padx=10)

    product_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0)

# helper: completely clear out product_frame (and reset chart_holder + scroll pos)
def clear_product_frame():
    global chart_holder
    for widget in product_frame.winfo_children():
        widget.destroy()
    chart_holder = None
    canvas.yview_moveto(0)

# --- USER-PROVIDED CHARTING & HISTORY FUNCTIONS ---

def render_matplotlib_chart(fig, holder):
    """Renders a matplotlib figure into a specified holder frame."""
    for widget in holder.winfo_children():
        widget.destroy()

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    chart_canvas = FigureCanvasTkAgg(fig, master=holder)
    chart_canvas.draw()
    chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    holder.update_idletasks()

def generate_chart(chart_type, product_id, holder):
    """Generates and displays a chart based on user selection into given holder."""
    try:
        conn = sqlite3.connect("vending_machine.db")
        cur = conn.cursor()
        fig, ax = plt.subplots(figsize=(8, 5))

        if chart_type == "Top 10 Selling Products":
            cur.execute("""
                        SELECT p.productName, SUM(t.quantity)
                        FROM CartTransactions t
                                 JOIN Products p ON p.productID = t.productID
                        GROUP BY p.productID
                        ORDER BY SUM(t.quantity) DESC LIMIT 10
                        """)
            data = cur.fetchall()
            if not data:
                messagebox.showinfo("No Data", "No sales data found.")
                plt.close(fig)
                return
            names, values = zip(*data)
            ax.bar(names, values, color='#007bff')
            ax.set_title("Top 10 Selling Products", fontsize=14)
            ax.set_ylabel("Units Sold")
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        elif chart_type == "Stock Trend":
            product_id = product_id.strip()
            if not product_id or not product_id.isdigit():
                messagebox.showerror("Input Error", "Enter a valid Product ID.")
                plt.close(fig)
                return
            cur.execute("SELECT productName FROM Products WHERE productID=?", (product_id,))
            result = cur.fetchone()
            product_name = result[0] if result else f"ID {product_id}"

            cur.execute("""
                        SELECT transactionDate, quantity
                        FROM CartTransactions
                        WHERE productID = ?
                        ORDER BY transactionDate ASC
                        """, (product_id,))
            data = cur.fetchall()
            if not data:
                messagebox.showinfo("No Data", f"No transaction data for Product ID {product_id}.")
                plt.close(fig)
                return
            dates, qty = zip(*data)
            ax.plot(dates, qty, marker='o', linestyle='-', color='#28a745')
            ax.set_title(f"Sales Trend for: {product_name}", fontsize=14)
            ax.set_ylabel("Quantity Sold")
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        render_matplotlib_chart(fig, holder)

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not generate chart: {e}")
    except Exception as e:
        messagebox.showerror("Chart Error", str(e))
    finally:
        if 'conn' in locals():
            conn.close()

def view_history():
    """Admin function to view transaction history and generate sales charts"""
    hist_win = tk.Toplevel(root)
    hist_win.title("📜 Transaction History & Analytics")
    hist_win.geometry("1100x700")
    hist_win.configure(bg="#e9ecef")
    hist_win.transient(root)
    hist_win.grab_set()

    container = ttk.Frame(hist_win, padding=10, style="Header.TFrame")
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="📜 Transaction History & Analytics",
              font=("Segoe UI", 16, "bold"), style="Header.TLabel").pack(pady=10, fill="x")

    # Local history display widget, not text_display
    response = send_command_safe("HISTORY")

    text_frame = ttk.Frame(container, padding=5, style="Card.TFrame")
    text_frame.pack(fill="both", expand=False, padx=10, pady=5)

    local_history_display = tk.Text(
        text_frame,
        height=12,
        wrap="word",
        font=("Consolas", 10),
        bg="#ffffff",
        fg="#444"
    )
    local_history_display.insert("1.0", response)
    local_history_display.config(state="disabled")
    local_history_display.pack(side="left", fill="both", expand=True)

    sc = ttk.Scrollbar(text_frame, orient="vertical", command=local_history_display.yview)
    sc.pack(side="right", fill="y")
    local_history_display.configure(yscrollcommand=sc.set)

    # Chart UI
    chart_ui = ttk.Frame(container, padding=10, style="Card.TFrame")
    chart_ui.pack(fill="x", padx=10, pady=10)
    chart_type_var = tk.StringVar(value="Top 10 Selling Products")

    ttk.Label(chart_ui, text="Select Chart:", style="Header.TLabel").pack(side="left", padx=(0, 5))
    chart_selector = ttk.Combobox(chart_ui, textvariable=chart_type_var,
                                  values=["Top 10 Selling Products", "Stock Trend"],
                                  width=25, state="readonly")
    chart_selector.pack(side="left", padx=5)

    ttk.Label(chart_ui, text="Product ID (Trend):", style="Header.TLabel").pack(side="left", padx=(15, 5))
    product_id_entry = ttk.Entry(chart_ui, width=10)
    product_id_entry.pack(side="left", padx=5)

    local_chart_holder = ttk.Frame(container, height=350, style="Card.TFrame")
    local_chart_holder.pack(fill="both", expand=True, padx=10, pady=(0, 20))
    local_chart_holder.pack_propagate(False)

    ttk.Button(chart_ui, text="📊 Generate", command=lambda:
               generate_chart(chart_type_var.get(), product_id_entry.get(), local_chart_holder))\
        .pack(side="left", padx=10)

def edit_stock():
    """Admin function to update product stock quantities."""
    show_products_view()
    product_canvas_container.pack_forget()
    product_canvas_container.pack(fill="both", expand=True)
    clear_product_frame()

    response = send_command_safe("VIEW")

    # 🛡️ Validate expected format
    if not response or "ProductID" not in response or "Price" not in response:
        ttk.Label(product_frame, text="⚠️ Failed to load product list.",
                  font=("Segoe UI", 14), style="Header.TLabel").pack(pady=20)
        return

    lines = response.strip().split("\n")[2:]  # Skip header

    for line in lines:
        if not line.strip():
            continue
        try:
            parts = line.split()
            pid = int(parts[0])
            name = " ".join(parts[1:-2])
            price = parts[-2]
            stock = parts[-1]
        except (ValueError, IndexError):
            continue

        item_frame = ttk.Frame(product_frame, padding=10, relief="solid", borderwidth=1, style="Card.TFrame")
        item_frame.pack(padx=10, pady=6, fill="x")
        item_frame.columnconfigure(1, weight=1)

        img_path = find_image_file(pid)
        img_label = ttk.Label(item_frame, style="Card.TLabel")
        if img_path:
            try:
                image = Image.open(img_path)
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)
                img_label.image = photo
                img_label.configure(image=photo)
            except Exception:
                img_label.configure(text="No Img", font=("Segoe UI", 9))
        img_label.grid(row=0, column=0, rowspan=2, padx=(0, 15), sticky="w")

        details_text = f"{name}\nPrice: {price} | Current Stock: {stock}"
        ttk.Label(item_frame, text=details_text, font=("Segoe UI", 11), justify="left", style="Card.TLabel")\
            .grid(row=0, column=1, rowspan=2, sticky="w")

        action_frame = ttk.Frame(item_frame, style="Card.TFrame")
        action_frame.grid(row=0, column=2, rowspan=2, sticky="e")

        ttk.Label(action_frame, text="Set New Stock:", style="Card.TLabel").pack(side="left", padx=(0, 5))
        qty_entry = ttk.Entry(action_frame, width=8, font=("Segoe UI", 10))
        qty_entry.pack(side="left", padx=5)

        def update_stock_func(p=pid, entry=qty_entry):
            quantity = entry.get().strip()
            if not quantity.isdigit():
                messagebox.showerror("Error", "Invalid quantity. Please enter a number.")
                return
            result = send_command_safe(f"CHANGE_STOCK {p} {quantity}")
            messagebox.showinfo("Stock Updated", result)
            edit_stock()  # Refresh view

        ttk.Button(action_frame, text="Update Stock", command=update_stock_func).pack(side="left", padx=5)

    product_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0)

def checkout():
    """Initiates the checkout process in a new window."""
    receipt = send_command_safe("RECEIPT")
    if not receipt or "ProductID" not in receipt or "Cart is empty" in receipt or "Your cart is empty" in receipt:
        messagebox.showinfo("Cart Empty", "Your cart is empty. Cannot proceed to checkout.")
        return

    checkout_window = tk.Toplevel(root)
    checkout_window.title("Confirm Purchase")
    checkout_window.geometry("700x550")
    checkout_window.configure(bg="#f7f7fc")
    checkout_window.transient(root)  # Keep window on top
    checkout_window.grab_set()  # Modal behavior

    main_frame = ttk.Frame(checkout_window, padding=20)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(main_frame, text="Please confirm your purchase details:", font=("Segoe UI", 14, "bold")).pack(
        pady=(0, 10))

    receipt_display = tk.Text(main_frame, height=15, width=80, relief="solid", borderwidth=1, font=("Courier New", 10),
                              wrap="word", bg="#ffffff")
    receipt_display.insert(tk.END, receipt)
    receipt_display.config(state="disabled")
    receipt_display.pack(pady=10, fill="both", expand=True)

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=10)

    def confirm_action():
        response = send_command_safe("CHECKOUT")
        for widget in main_frame.winfo_children():
            widget.destroy()  # Clear window

        result_text = "✅ Purchase completed successfully!\nThank you for your order."
        ttk.Label(main_frame, text=result_text, font=("Segoe UI", 16, "bold"), foreground="green",
                  justify="center").pack(pady=40, padx=20)
        ttk.Button(main_frame, text="Close", command=checkout_window.destroy, style="Success.TButton").pack(pady=10)
        update_display(greeting)  # Reset main display

        for widget in main_frame.winfo_children():
            widget.destroy()  # Clear window

            # Show success and then offer a button which closes _both_ windows
        result_text = "✅ Purchase completed successfully!\nThank you for your order."
        ttk.Label(main_frame,
                  text=result_text,
                  font=("Segoe UI", 16, "bold"),
                  foreground="green",
                  justify="center") \
            .pack(pady=40, padx=20)

        def close_everything():
            checkout_window.destroy()
            root.destroy()

        ttk.Button(main_frame,
                   text="Close",
                   command=close_everything,
                   style="Success.TButton") \
            .pack(pady=10)

    def cancel_action():
        checkout_window.destroy()

    ttk.Button(button_frame, text="✅ Confirm Purchase", width=20, command=confirm_action, style="Success.TButton").grid(
        row=0, column=0, padx=10)
    ttk.Button(button_frame, text="❌ Cancel", width=20, command=cancel_action, style="Danger.TButton").grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=10)

# --- GUI HELPER FUNCTIONS ---

def clear_product_frame():
    """Destroys all widgets inside the main product frame."""
    for widget in product_frame.winfo_children():
        widget.destroy()

def clear_display():
    """Clears the main text display."""
    show_text_display()
    update_display("")

def update_display(text):
    """Updates the main text display with new content."""
    text_display.config(state='normal')
    text_display.delete(1.0, tk.END)
    text_display.insert(tk.END, text)
    text_display.config(state='disabled')

def show_products_view():
    """Switches the view to show the product list."""
    text_display_container.pack_forget()
    product_canvas_container.pack(fill="both", expand=True)

def show_text_display():
    """Switches the view to show the text display."""
    product_canvas_container.pack_forget()
    text_display_container.pack(fill="both", expand=True, padx=20, pady=20)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to exit?"):
        try:
            if client:
                client.send_command("EXIT")
                client.client.close()
        except Exception as e:
            print(f"Error on closing: {e}")  # Log error, but close anyway
        root.destroy()

# ===================================================================
# --- APPLICATION START ---
# ===================================================================

if __name__ == "__main__":
    client = None
    username = None
    chart_holder = None

    if not login_prompt():
        exit()

    root = tk.Tk()
    root.title("Smart Vending Machine Client")
    root.geometry("1100x800")
    root.configure(bg="#e9ecef")
    root.minsize(900, 700)

    # --- STYLE CONFIGURATION ---
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton", padding=8, relief="flat", font=("Segoe UI", 10, "bold"), foreground="white",
                    background="#007bff")
    style.map("TButton", background=[('active', '#0056b3')])
    style.configure("Danger.TButton", background="#dc3545")
    style.map("Danger.TButton", background=[('active', '#c82333')])
    style.configure("Success.TButton", background="#28a745")
    style.map("Success.TButton", background=[('active', '#218838')])
    style.configure("Card.TFrame", background="#ffffff")
    style.configure("Card.TLabel", background="#ffffff")
    style.configure("Header.TFrame", background="#f7f7fc")
    style.configure("Header.TLabel", background="#f7f7fc", foreground="#333")

    # --- MAIN CONTENT AREA (for swapping views) ---
    content_area = ttk.Frame(root, padding=10)
    content_area.pack(fill="both", expand=True)

    # --- 1. Text Display View ---
    text_display_container = ttk.Frame(content_area)
    text_display = tk.Text(text_display_container, wrap="word", font=("Segoe UI", 11), bg="#ffffff", relief="solid",
                           bd=1, padx=15, pady=15)
    text_display.pack(fill="both", expand=True)

    # --- 2. Products/Scrollable View ---
    product_canvas_container = ttk.Frame(content_area)
    canvas = tk.Canvas(product_canvas_container, bg="#f7f7fc", highlightthickness=0)
    scrollbar = ttk.Scrollbar(product_canvas_container, orient="vertical", command=canvas.yview)
    product_frame = ttk.Frame(canvas, style="Header.TFrame")

    product_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=product_frame, anchor="nw", width=1020)  # Set fixed width for items
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- BOTTOM BUTTON BAR ---
    button_frame = ttk.Frame(root, padding=(10, 15))
    button_frame.pack(fill="x")

    ttk.Button(button_frame, text="🛍️ View Products", command=view_products).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="🛒 View Cart", command=view_cart).pack(side="left", padx=5, expand=True)
    if username == "admin":
        ttk.Button(button_frame, text="📈 History & Analytics", command=view_history).pack(side="left", padx=5,
                                                                                          expand=True)
        ttk.Button(button_frame, text="📦 Edit Stock", command=edit_stock).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="💳 Checkout", command=checkout).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="✨ Clear", command=clear_display).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="🚪 Exit", command=on_closing, style="Danger.TButton").pack(side="left", padx=5,
                                                                                             expand=True)

    # --- INITIAL STATE ---
    root.protocol("WM_DELETE_WINDOW", on_closing)
    greeting = f"""Welcome, {username}!\n\nClick 'View Products' to start Browse or select another option below."""
    show_text_display()
    update_display(greeting)

    root.mainloop()
import tkinter as tk
import client as c

# Initialize root window
root = tk.Tk()
root.geometry("1000x800")
root.title("Smart Vending Machine")
root.configure(background="#E14434")

client = c.Client()

# ─── Functions ───────────────────────────────────────────────────────────
def view_products():
    response = client.send_command("VIEW")
    update_display(response)

def add_to_cart():
    pid = entry_pid.get().strip()
    qty = entry_qty.get().strip()

    if not pid or not qty:
        update_display("Please enter both Product ID and Quantity.")
        entry_pid.focus_set()
    else:
        try:
            command = f"ADD {pid} {qty}"
            response = client.send_command(command)
        except Exception as e:
            response = f"Error: {e}"

        update_display(response)

def view_cart():
    response = client.send_command("CART")
    update_display(response)

def checkout():
    response = client.send_command("CHECKOUT")
    update_display(response)

def clear_display():
    text_display.config(state='normal')
    text_display.delete(1.0, tk.END)
    text_display.config(state='disabled')

def update_display(text):
    text_display.config(state='normal')
    text_display.delete(1.0, tk.END)
    text_display.insert(tk.END, text)
    text_display.config(state='disabled')

def on_closing():
    try:
        client.send_command("EXIT")
    except:
        pass
    root.destroy()

# ─── GUI Layout ──────────────────────────────────────────────────────────

# Display Window
text_display = tk.Text(root, width=100, height=30, padx=20, pady=20, font=("Courier New", 10), background="#FFB4B4")
text_display.config(state='disabled')
text_display.pack(padx=20, pady=20)


# Entry Fields
entry_frame = tk.Frame()
entry_frame.pack(pady=10)

tk.Label(entry_frame, text="Product ID:").grid(row=0, column=0, padx=5)
entry_pid = tk.Entry(entry_frame)
entry_pid.grid(row=0, column=1, padx=5)

tk.Label(entry_frame, text="Quantity:").grid(row=0, column=2, padx=5)
entry_qty = tk.Entry(entry_frame)
entry_qty.grid(row=0, column=3, padx=5)

# Buttons
button_frame = tk.Frame()
button_frame.pack(pady=10)

view = tk.Button(button_frame, text="View Products", width=15, command=view_products)
view.grid(row=0, column=0, padx=5, pady=5)

add = tk.Button(button_frame, text="Add to Cart", width=15, command=add_to_cart)
add.grid(row=0, column=1, padx=5, pady=5)

cart = tk.Button(button_frame, text="View Cart", width=15, command=view_cart)
cart.grid(row=0, column=2, padx=5, pady=5)

checkout = tk.Button(button_frame, text="Checkout", width=15, command=checkout)
checkout.grid(row=1, column=0, padx=5, pady=10)

clear = tk.Button(button_frame, text="Clear Display", width=15, command=clear_display)
clear.grid(row=1, column=1, padx=5, pady=10)

exit = tk.Button(button_frame, text="Exit", width=15, command=on_closing)
exit.grid(row=1, column=2, padx=5, pady=10)

# Exit handling
root.protocol("WM_DELETE_WINDOW", on_closing)

# Greeting Message
update_display("""Welcome to the Smart Vending Machine!
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣾⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣴⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡖
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢠⡰⣤⣬⣗⣶⣿⣾⣽⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣶⠟⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⣒⣩⣬⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⡟⠀⠀
⠀⢀⣀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⡟⠀⠀⠀
⠀⠻⢻⢛⢯⠻⡝⠿⡟⢿⢛⣛⣛⣏⣛⡝⣛⠿⣟⢻⠿⣿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⢀⡄⠀⠀⠀⣼⣿⡟⠀⠀⠀⠀
⠀⠀⠀⠈⠉⠐⠟⡷⢟⡖⢯⡹⡱⢮⢭⡹⣬⢳⢎⡳⣽⣾⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣿⣄⣀⣠⣾⣿⡿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠒⠓⠩⠷⠫⡵⢫⡝⡾⣝⡷⣿⣹⣯⣻⣿⣿⣿⣟⡼⣭⣛⠿⣿⣿⣿⡿⣿⢿⡿⣿⣟⡿⢿⡃⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⣳⢾⡵⠫⣞⣵⡻⣞⡿⣿⢿⣿⣿⣿⣳⣯⢿⣼⣿⣿⣿⣇⠻⠋⠉⠀⠙⢿⣇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣯⣳⠏⠀⠀⠀⠀⠉⠉⠉⠙⠛⣿⣿⣿⡍⠈⠛⢿⠋⠉⠛⣿⣷⣶⡄⠀⠀⠀⠉⠂⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣼⣿⡽⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣷⠀⠀⠀⠀⠀⢼⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢠⣾⣿⣿⣿⣷⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡆⠀⠀⢠⣶⣿⣿⢯⣷⡯⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣽⣿⣿⣿⣿⠿⣿⣛⣻⠃⠀⠀⠀⠀⠀⣰⣶⣿⣿⣿⣿⣧⣤⠀⠈⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⢿⣿⢿⢿⢿⣛⣿⡽⠾⠛⠓⠛⠈⠁⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣿⣿⣟⣯⣿⣿⣽⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⢔⣿⡿⣿⣯⣿⢿⣿⣿⣿⣿⠿⣟⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣦⣷⣮⣿⣾⢿⣿⣽⡿⣿⡿⣟⡽⣞⡿⠽⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣻⣿⣿⢷⡿⣟⣻⣻⢯⡷⠿⠙⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠛⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
Click 'View Products' to start browsing.""")

# Run GUI loop
root.mainloop()

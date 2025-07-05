import tkinter as tk
import client as c  # Your custom client module to communicate with the server

# ─── Root Window Setup ──────────────────────────────────────────────────
root = tk.Tk()
root.geometry("1000x800")                          # Set window size
root.title("Smart Vending Machine")                # Window title
root.configure(background="#E14434")               # Background color

client = c.Client()                                # Create client object (connects to server)

# ─── Function Definitions ───────────────────────────────────────────────

# View available products from the vending machine
def view_products():
    response = client.send_command("VIEW")
    update_display(response)

# Add selected product ID and quantity to the cart
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
        finally:
            entry_pid.delete(0, tk.END)
            entry_qty.delete(0, tk.END)

        update_display(response + "\n\n" + client.send_command("VIEW"))

# View current contents of the shopping cart
def view_cart():
    response = client.send_command("CART")
    update_display(response)

def view_history():
    response = client.send_command("HISTORY")
    update_display(response)

# Handle checkout logic with confirmation prompt
def checkout():
    def confirm_action():
        checkout_button_frame.destroy()                # Remove Yes/No buttons
        txt_display.delete(1.0, tk.END)
        response = client.send_command("CHECKOUT")     # Finalize purchase
        txt_display.insert(tk.END, response)

        # Show confirmation message
        confirmation_label = tk.Label(
            checkout_window,
            text="✅ Purchase completed successfully!\nPlease exit this window.",
            font=("Arial", 12, "bold"),
            fg="green",
            bg="#FFB4B4"
        )
        confirmation_label.pack(pady=10)

        update_display(greeting)  # Reset main display with greeting

    def cancel_action():
        checkout_window.destroy()  # Close the checkout window

    # Create a new window for checkout confirmation
    checkout_window = tk.Toplevel(root)
    checkout_window.title("Checkout Window")
    checkout_window.geometry("800x600")

    # Text area to display receipt
    txt_display = tk.Text(
        checkout_window,
        width=80, height=20,
        padx=10, pady=10,
        font=("Courier New", 10),
        background="#FFB4B4"
    )
    txt_display.insert(tk.END, "Do you want to confirm your purchase?\n\n")
    txt_display.pack(padx=20, pady=20)

    receipt = client.send_command("receipt")           # Get receipt preview from server
    txt_display.insert(tk.END, receipt)

    # Frame for confirm/cancel buttons
    checkout_button_frame = tk.Frame(checkout_window)
    checkout_button_frame.pack(pady=10)

    confirm_button = tk.Button(checkout_button_frame, text="Yes", width=15, command=confirm_action)
    confirm_button.grid(row=0, column=0, padx=5, pady=5)

    revert_button = tk.Button(checkout_button_frame, text="No", width=15, command=cancel_action)
    revert_button.grid(row=0, column=1, padx=5, pady=5)

# Clear the main text display
def clear_display():
    text_display.config(state='normal')
    text_display.delete(1.0, tk.END)
    text_display.config(state='disabled')

# Update the text in the main display window
def update_display(text):
    text_display.config(state='normal')
    text_display.delete(1.0, tk.END)
    text_display.insert(tk.END, text)
    text_display.config(state='disabled')

# Cleanly exit application and notify server
def on_closing():
    try:
        client.send_command("EXIT")
    except:
        pass
    root.destroy()

# ─── GUI Layout ──────────────────────────────────────────────────────────

# Main display area
text_display = tk.Text(
    root,
    width=100, height=30,
    padx=20, pady=20,
    font=("Courier New", 10),
    background="#FFB4B4"
)
text_display.config(state='disabled')  # Make it read-only initially
text_display.pack(padx=20, pady=20)

# Entry section for Product ID and Quantity
entry_frame = tk.Frame()
entry_frame.pack(pady=10)

tk.Label(entry_frame, text="Product ID:").grid(row=0, column=0, padx=5)
entry_pid = tk.Entry(entry_frame)
entry_pid.grid(row=0, column=1, padx=5)

tk.Label(entry_frame, text="Quantity:").grid(row=0, column=2, padx=5)
entry_qty = tk.Entry(entry_frame)
entry_qty.grid(row=0, column=3, padx=5)

# Buttons for core functionality
button_frame = tk.Frame()
button_frame.pack(pady=10)

view = tk.Button(button_frame, text="View Products", width=15, command=view_products)
view.grid(row=0, column=0, padx=5, pady=5)

add = tk.Button(button_frame, text="Add to Cart", width=15, command=add_to_cart)
add.grid(row=0, column=1, padx=5, pady=5)

cart = tk.Button(button_frame, text="View Cart", width=15, command=view_cart)
cart.grid(row=0, column=2, padx=5, pady=5)

history = tk.Button(button_frame, text="Order History", width=15, command=view_history)
history.grid(row=0, column=3, padx=5, pady=5)

checkout = tk.Button(button_frame, text="Checkout", width=15, command=checkout)
checkout.grid(row=1, column=0, padx=5, pady=10)

clear = tk.Button(button_frame, text="Clear Display", width=15, command=clear_display)
clear.grid(row=1, column=1, padx=5, pady=10)

exit = tk.Button(button_frame, text="Exit", width=15, command=on_closing)
exit.grid(row=1, column=2, padx=5, pady=10)

# Handle window close (X button)
root.protocol("WM_DELETE_WINDOW", on_closing)

# Greeting message with ASCII art
greeting = """Welcome to the Smart Vending Machine!
Click 'View Products' to start browsing."""
update_display(greeting)

# ─── Start the GUI loop ──────────────────────────────────────────────────
root.mainloop()

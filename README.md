# Smart Vending Machine for Digital Goods

This project is a full-stack Python application that simulates a digital vending machine for purchasing downloadable items. It implements a client-server model with a GUI frontend, persistent storage using SQLite, and advanced features such as currency conversion and sales analytics.

---

## Features

- Multi-tier architecture: client, server, backend logic, and database
- Graphical User Interface built with Tkinter
- Secure login system with credential validation from SQLite
- Shopping cart functionality with add, remove, and checkout capabilities
- Transaction logging and receipt generation
- Sales analytics via matplotlib charts
- Live currency conversion using exchangerate.guru
- Modular codebase with clear separation of concerns

---

## Project Structure

```

.
├── backend.py           # Business logic and database operations
├── client.py            # Client-side networking logic
├── server.py            # Socket server handling all requests
├── gui.py               # Tkinter GUI and user interactions
├── shop.sql             # SQL script for database schema and sample data
├── vending\_machine.db   # SQLite database (should be generated or included)
├── images/              # Product images used by the GUI
├── README.md
└── report.pdf           # Project report

````

---

## Technologies Used

- Python 3.13
- Tkinter (GUI)
- socket, threading (networking)
- SQLite (data persistence)
- requests + BeautifulSoup (web scraping exchange rates)
- matplotlib (visual analytics)
- Pillow (image display)

---

## Setup Instructions

1. **Install dependencies**:
   `pip install requests beautifulsoup4 pillow matplotlib`

2. **Database**:
   Ensure `vending_machine.db` is in the root directory. You can create it using the schema in `shop.sql`.

3. **Run the server**:
   `python server.py`

4. **Run the client GUI in a separate terminal**:

   `python gui.py`

---

## Usage

* Log in with valid credentials from the `Users` table in the database.
* The application terminates after three failed login attempts.
* Available operations via the GUI:

  * View products with names, prices, stock, and optional images
  * Add products to cart with quantity selection
  * Remove items from the cart
  * Checkout and receive a formatted receipt
  * Admins can view transaction history and generate analytics charts
  * Currency display can be changed (USD, GBP, INR, MUR)

---

## Implementation Summary

* **`backend.py`**:

  * Inventory management
  * Currency conversion (via web scraping)
  * Transaction logging and checkout logic

* **`server.py`**:

  * TCP server using socket and threading
  * Handles user authentication, product viewing, cart updates, and analytics commands

* **`client.py`**:

  * Sends user requests to the server and returns responses to the GUI

* **`gui.py`**:

  * Handles login, main GUI interface, interaction with client commands
  * Visualizes transaction history and analytics using matplotlib

---

## Future Improvements

* Add GUI-based user registration
* Integrate OAuth (Google sign-in)
* Replace threading with asynchronous I/O or thread pool
* Enhance visual design and responsiveness of the GUI
* Add backend unit tests
* Migrate to a web interface using Flask or FastAPI
* Add real-time inventory updates and notifications

---

## Technical Specifications

| Component        | Details                      |
| ---------------- | ---------------------------- |
| Programming Lang | Python 3.13                  |
| UI               | Tkinter                      |
| Networking       | socket, threading            |
| DB               | SQLite with `sqlite3` module |
| Analytics        | matplotlib                   |
| Image Handling   | Pillow (PIL)                 |
| Currency Support | requests + BeautifulSoup     |
| Platform         | Cross-platform               |


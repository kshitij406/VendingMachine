# Smart Vending Machine for Digital Goods

The Smart Vending Machine for Digital Goods is a full-stack Python application that simulates a digital vending system for purchasing downloadable items. The system follows a client-server architecture and integrates a graphical user interface, persistent database storage, live currency conversion, and sales analytics.

This project was developed to demonstrate real-world software engineering concepts including modular design, networking, authentication, and data visualization.

## Key Features

* Multi-tier architecture separating client, server, backend logic, and database
* Graphical user interface built using Tkinter
* Secure login system with credential validation via SQLite
* Shopping cart with add, remove, and checkout functionality
* Transaction logging and receipt generation
* Sales analytics visualized using matplotlib
* Live currency conversion using exchangerate.guru
* Modular and maintainable codebase with clear separation of concerns

## System Architecture

The application is structured into distinct layers:

* **GUI Layer**: Handles user interaction and presentation
* **Client Layer**: Sends requests and receives responses from the server
* **Server Layer**: Manages authentication, requests, and concurrency
* **Backend Layer**: Handles business logic, currency conversion, and database operations
* **Database Layer**: Stores users, products, and transaction data using SQLite

## Project Structure

```
.
├── backend.py            # Business logic and database operations
├── client.py             # Client-side networking logic
├── server.py             # Socket server handling all requests
├── gui.py                # Tkinter GUI and user interactions
├── shop.sql              # SQL schema and sample data
├── vending_machine.db    # SQLite database
├── images/               # Product images used by the GUI
├── README.md
└── report.pdf            # Project report
```

## Setup Instructions

### Requirements

Install the required dependencies:

```
pip install requests beautifulsoup4 pillow matplotlib
```

### Database Setup

Ensure `vending_machine.db` exists in the root directory.
If not present, create it using the schema provided in `shop.sql`.

### Running the Application

Start the server:

```
python server.py
```

In a separate terminal, start the client GUI:

```
python gui.py
```

## Usage

* Log in using valid credentials stored in the `Users` table
* The application exits after three failed login attempts
* Available operations include:

  * Viewing products with price, stock, and images
  * Adding and removing items from the cart
  * Completing purchases and receiving receipts
  * Viewing transaction history and sales analytics (admin access)
  * Switching display currency (USD, GBP, INR, MUR)

## Implementation Overview

### backend.py

* Inventory management
* Currency conversion using live exchange rates
* Transaction handling and logging

### server.py

* TCP socket server with threading
* Handles authentication, product queries, cart operations, and analytics requests

### client.py

* Communicates with the server
* Sends structured requests and processes responses

### gui.py

* Login interface and main vending machine UI
* Displays products, cart state, receipts, and analytics charts

## Technical Specifications

| Component            | Details                 |
| -------------------- | ----------------------- |
| Programming Language | Python 3.13             |
| User Interface       | Tkinter                 |
| Networking           | socket, threading       |
| Database             | SQLite (sqlite3)        |
| Analytics            | matplotlib              |
| Image Handling       | Pillow (PIL)            |
| Currency Conversion  | requests, BeautifulSoup |

## Future Improvements

* GUI-based user registration
* OAuth authentication support
* Asynchronous networking or thread pooling
* Improved GUI responsiveness and styling
* Automated backend unit tests
* Migration to a web-based interface using Flask or FastAPI
* Real-time inventory updates and notifications

## Author

Kshitij Jha
BSc Computer Science

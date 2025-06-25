-- Create the Products table


CREATE TABLE IF NOT EXISTS Products (
    productID INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each product
    productName TEXT NOT NULL,                  -- Name of the product
    price REAL NOT NULL,                        -- Price of the product
    stock INTEGER NOT NULL                      -- Available stock for the product
);

-- Create the CartTransactions table
CREATE TABLE IF NOT EXISTS CartTransactions (
    transactionID INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each transaction
    productID INTEGER NOT NULL,                      -- The ID of the product in the transaction
    quantity INTEGER NOT NULL,                       -- Quantity of the product in the transaction
    totalPrice REAL NOT NULL,                        -- Total price for the transaction
    transactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of the transaction
    FOREIGN KEY (productID) REFERENCES Products(productID) -- Foreign key linking to Products table
);

-- Insert sample data into the Products table
INSERT INTO Products (productName, price, stock)
VALUES
    ('Sneakers', 49.99, 10),   -- Product: Sneakers
    ('Backpack', 29.99, 15),   -- Product: Backpack
    ('Water Bottle', 9.99, 20),-- Product: Water Bottle
    ('Laptop', 799.99, 5),     -- Product: Laptop
    ('Smartphone', 599.99, 8), -- Product: Smartphone
    ('Headphones', 99.99, 25); -- Product: Headphones

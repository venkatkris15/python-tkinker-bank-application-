import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Establish MySQL connection
try:
    conn = mysql.connector.connect(
        user='root',
        password='2525',
        host='127.0.0.1',
        port=3306,
        database='banking_system'  # Change this to your database name
    )
    print("Connected to MySQL Server successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create accounts table if not exists
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INT AUTO_INCREMENT PRIMARY KEY,
            account_number VARCHAR(20) UNIQUE NOT NULL,
            account_name VARCHAR(100) NOT NULL,
            balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Accounts table created successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Create transactions table if not exists
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            account_number VARCHAR(20) NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description VARCHAR(255),
            amount DECIMAL(15, 2),
            balance DECIMAL(15, 2),
            FOREIGN KEY (account_number) REFERENCES accounts(account_number)
        )
    """)
    print("Transactions table created successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Function to create a new account
def create_account(account_number, account_name):
    try:
        cursor.execute("""
            INSERT INTO accounts (account_number, account_name, balance)
            VALUES (%s, %s, 0.00)
        """, (account_number, account_name))
        conn.commit()
        messagebox.showinfo("Success", f"Account '{account_number}' created successfully!")

    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Error", f"Error: {err}")

# Function to update balance
def update_balance(account_number, amount):
    try:
        cursor.execute("""
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_number = %s
        """, (amount, account_number))
        conn.commit()

    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Error", f"Error: {err}")

# Function to fetch balance
def get_balance(account_number):
    try:
        cursor.execute("""
            SELECT balance FROM accounts
            WHERE account_number = %s
        """, (account_number,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            messagebox.showerror("Error", f"Account '{account_number}' not found.")
            return None

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
        return None

# Function to fetch account statement
def get_account_statement(account_number):
    try:
        cursor.execute("""
            SELECT transaction_date, description, amount, balance
            FROM transactions
            WHERE account_number = %s
            ORDER BY transaction_date
        """, (account_number,))
        statement = cursor.fetchall()
        return statement

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
        return None

def download_statement_as_pdf(account_number, statement):
    pdf_filename = f"account_statement_{account_number}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Account Statement for Account Number: {account_number}")
    c.setFont("Helvetica", 12)
    
    # Set initial y-coordinate for the statement entries
    y = 700
    
    for transaction in statement:
        transaction_date, description, amount, balance = transaction
        c.drawString(100, y, f"Date: {transaction_date}")
        c.drawString(250, y, f"Description: {description}")
        c.drawString(450, y, f"Amount: ₹{amount:.2f}")
        c.drawString(600, y, f"Balance: ₹{balance:.2f}")
        y -= 20
    
    c.save()
    messagebox.showinfo("Success", f"PDF generated: {pdf_filename}")

# Function to add transaction
def add_transaction(account_number, description, amount, balance):
    try:
        cursor.execute("""
            INSERT INTO transactions (account_number, description, amount, balance)
            VALUES (%s, %s, %s, %s)
        """, (account_number, description, amount, balance))
        conn.commit()
        messagebox.showinfo("Success", "Transaction recorded successfully!")

    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Error", f"Error: {err}")

# Function to fetch account holders list
def get_account_holders():
    try:
        cursor.execute("""
            SELECT account_number, account_name, balance
            FROM accounts
        """)
        account_holders = cursor.fetchall()
        return account_holders

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
        return None

# Function to download account holders list as PDF
def download_account_holders_as_pdf(account_holders):
    pdf_filename = "account_holders_list.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Account Holders List")
    c.setFont("Helvetica", 12)
    
    # Set initial y-coordinate for the account holders entries
    y = 700
    
    for account in account_holders:
        account_number, account_name, balance = account
        c.drawString(100, y, f"Account Number: {account_number}")
        c.drawString(300, y, f"Account Name: {account_name}")
        c.drawString(500, y, f"Balance: ₹{balance:.2f}")
        y -= 20
    
    c.save()
    messagebox.showinfo("Success", f"PDF generated: {pdf_filename}")

# Close cursor and connection
def close_connection():
    cursor.close()
    conn.close()
    print("MySQL connection closed.")
    root.destroy()  # Close the Tkinter window

# GUI functions
def create_account_gui():
    account_number = account_number_entry.get()
    account_name = account_name_entry.get()
    create_account(account_number, account_name)

def show_balance_gui():
    account_number = account_number_entry.get()
    balance = get_balance(account_number)
    if balance is not None:
        messagebox.showinfo("Balance", f"Balance for account '{account_number}' is ₹{balance:.2f}")

def deposit_gui():
    account_number = account_number_entry.get()
    amount = float(amount_entry.get())
    update_balance(account_number, amount)
    add_transaction(account_number, "Deposit", amount, get_balance(account_number))

def withdraw_gui():
    account_number = account_number_entry.get()
    amount = float(amount_entry.get())
    update_balance(account_number, -amount)
    add_transaction(account_number, "Withdrawal", -amount, get_balance(account_number))

def display_account_statement_gui():
    account_number = account_number_entry.get()
    statement = get_account_statement(account_number)
    if statement:
        statement_window = tk.Toplevel(root)
        statement_window.title("Account Statement")
        statement_text = tk.Text(statement_window)
        statement_text.pack()
        for transaction in statement:
            transaction_date, description, amount, balance = transaction
            statement_text.insert(tk.END, f"Date: {transaction_date}, Description: {description}, Amount: ₹{amount:.2f}, Balance: ₹{balance:.2f}\n")
        
        def download_statement():
            download_statement_as_pdf(account_number, statement)
        
        download_button = tk.Button(statement_window, text="Download as PDF", command=download_statement)
        download_button.pack()

def show_account_holders_gui():
    account_holders = get_account_holders()
    if account_holders:
        account_holders_window = tk.Toplevel(root)
        account_holders_window.title("Account Holders List")
        account_holders_text = tk.Text(account_holders_window)
        account_holders_text.pack()
        for account in account_holders:
            account_number, account_name, balance = account
            account_holders_text.insert(tk.END, f"Account Number: {account_number}, Account Name: {account_name}, Balance: ₹{balance:.2f}\n")
        
        def download_account_holders():
            download_account_holders_as_pdf(account_holders)
        
        download_button = tk.Button(account_holders_window, text="Download as PDF", command=download_account_holders)
        download_button.pack()

# Main banking GUI
root = tk.Tk()
root.title("SVK BANK")  # Set the title of the window
root.geometry("800x300")  # Set the window size

# Set window icon
icon_path = r"C:\Users\venka\OneDrive\Desktop\New folder\SVK.png"   # Path to your icon file
if os.path.exists(icon_path):
    root.iconphoto(False, tk.PhotoImage(file=icon_path))

# Style configuration
style = ttk.Style()
style.configure('TLabel', font=('Helvetica', 12), background='lightblue')
style.configure('TButton', font=('Helvetica', 12), background='lightgreen')
style.configure('TEntry', font=('Helvetica', 12))

# Widgets
account_number_label = ttk.Label(root, text="Account Number")
account_number_label.grid(row=0, column=0, padx=10, pady=10)
account_number_entry = ttk.Entry(root)
account_number_entry.grid(row=0, column=1, padx=10, pady=10)

account_name_label = ttk.Label(root, text="Account Name")
account_name_label.grid(row=0, column=2, padx=10, pady=10)
account_name_entry = ttk.Entry(root)
account_name_entry.grid(row=0, column=3, padx=10, pady=10)

amount_label = ttk.Label(root, text="Amount")
amount_label.grid(row=0, column=4, padx=10, pady=10)
amount_entry = ttk.Entry(root)
amount_entry.grid(row=0, column=5, padx=10, pady=10)

create_account_button = ttk.Button(root, text="Create Account", command=create_account_gui)
create_account_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

show_balance_button = ttk.Button(root, text="Show Balance", command=show_balance_gui)
show_balance_button.grid(row=1, column=2, columnspan=2, padx=10, pady=10)

deposit_button = ttk.Button(root, text="Deposit", command=deposit_gui)
deposit_button.grid(row=1, column=4, columnspan=2, padx=10, pady=10)

withdraw_button = ttk.Button(root, text="Withdraw", command=withdraw_gui)
withdraw_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

display_account_statement_button = ttk.Button(root, text="Display Account Statement", command=display_account_statement_gui)
display_account_statement_button.grid(row=2, column=2, columnspan=2, padx=10, pady=10)

show_account_holders_button = ttk.Button(root, text="Show Account Holders List", command=show_account_holders_gui)
show_account_holders_button.grid(row=2, column=4, columnspan=2, padx=10, pady=10)

exit_button = ttk.Button(root, text="Exit", command=close_connection)
exit_button.grid(row=3, column=2, columnspan=2, padx=10, pady=10)

# Start the GUI event loop
root.mainloop()

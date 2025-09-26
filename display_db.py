# display_db.py
import mysql.connector
from tabulate import tabulate  # optional, for pretty table display

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password",
        database="gmail_db"  # use the same DB as main.py
    )

def fetch_emails():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT email_id, from_user, subject, body, date_sent FROM email_inbox"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def display_emails():
    emails = fetch_emails()
    if not emails:
        print("No emails in the database.")
        return
    headers = ["Email ID", "From", "Subject", "Body", "Date Sent"]
    print(tabulate(emails, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    display_emails()

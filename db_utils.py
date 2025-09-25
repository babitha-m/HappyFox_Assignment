import mysql.connector

def init_db():
    connection = mysql.connector.connect(
        host= "localhost",
        user="root",
        password="Password",
        database="gmail_db"
    )
    cursor=connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_inbox(
            id INT AUTO_INCREMENT PRIMARY KEY,
            email_id VARCHAR(255) UNIQUE NOT NULL,
            from_user VARCHAR(500),
            subject VARCHAR(1000),
            body VARCHAR(500),
            date_sent VARCHAR(255)
        )
    """)
    connection.commit()
    return connection,cursor

def store_emails(cursor,connection,emails):
    for e in emails:
        try:
            truncated_body = e.get('body', '')[:500]  # truncate to 500 chars
            cursor.execute("""
                INSERT INTO email_inbox (email_id, from_user, subject, body, date_sent)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                e['id'], e.get('from'),
                e.get('subject'), truncated_body, e.get('date')
            ))
        except mysql.connector.IntegrityError:
            print(f"Duplicate entry:{e.get('subject')}")
    connection.commit()
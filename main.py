from fetch_mails import authenticate_gmail,fetch_emails
from db_utils import init_db,store_emails

MAX_EMAILS = 5   #Change the number of mails dynamically
if __name__=='__main__':
    service=authenticate_gmail()
    emails=fetch_emails(service,max_results=MAX_EMAILS)
    
    if not emails:
        print("No emails")
    else:
        print(f"Fetched {len(emails)} emails from Gmail.\n")
    
    connection,cursor=init_db()
    store_emails(cursor,connection,emails)
    print(f"Stored emails into MySQL database\n")
    
    for e in emails:
        body_preview = e.get('body', '')[:500].replace('\n', ' ')
        print(f"From: {e.get('from')}, Subject: {e.get('subject')}, "
              f"Date: {e.get('date')}, Body Preview: {body_preview}\n")
        
    
    cursor.close()
    connection.close()   
    
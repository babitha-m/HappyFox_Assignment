from fetch_mails import authenticate_gmail, fetch_emails
from db_utils import init_db, store_emails
from rules_processing import load_rules, evaluate, apply

MAX_EMAILS = 100 # fetch limit

if __name__ == '__main__':
    # 1. Authenticate and fetch emails
    service = authenticate_gmail()
    emails = fetch_emails(service, max_results=MAX_EMAILS)

    if not emails:
        print("No emails found.")
    else:
        print(f"Fetched {len(emails)} emails from Gmail.\n")

    # 2. Store emails in database
    connection, cursor = init_db()
    store_emails(cursor, connection, emails)
    print("Stored emails into MySQL database.\n")

    # 3. Load rules
    rules = load_rules("rules.json")  # make sure this path is correct

    # 4. Fetch emails from DB for processing
    cursor.execute(
        "SELECT email_id, from_user as `from`, subject, body, date_sent as `date` FROM email_inbox"
    )
    db_emails = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

    # 5. Apply rules
    for e in db_emails:
        for rset in rules:
            try:
                if evaluate(e, rset):
                    apply(service, e["email_id"], rset["actions"])
                    print(f"Applied {rset['actions']} to {e['email_id']}")
            except Exception as exc:
                print(f"Error applying rules to {e['email_id']}: {exc}")

    # 6. Close DB
    cursor.close()
    connection.close()
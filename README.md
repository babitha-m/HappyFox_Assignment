# Inbox Automator: Rule-Based Email Automation
A Python script that fetches emails from Gmail via OAuth using Gmail API ; stores them in a relational database(MySQL in this case) and processes them on the basis of some pre-defined rules.

---

## Features

- **Fetch Emails**: Retrieve emails from Gmail inbox using Gmail API (OAuth authentication).  
- **Database Storage**: Store email details such as sender, subject, body, and date in MySQL.  
- **Rule-Based Processing**: Apply custom rules defined in a JSON file to perform actions on emails.  
- **Actions Supported**:
  - Mark as Read / Unread
  - Move to a specific label/folder

---

## Requirements

- Python 3.11+
- Gmail API credentials (`credentials.json`)
- MySQL server
- Python packages (install via `requirements.txt`):
  - `google-api-python-client`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`
  - `html2text`
  - `mysql-connector-python`
- Pytest for testing

---

## File Structure

```
├── tests
│   ├── test_db_utils.py   # Unit tests for db_utils.py
│   ├── test_fetch_mails.py # Unit tests for fetch_mails.py
│   ├── test_rules_processing.py # Unit tests for rules_processing.py
│   └── test_integration.py # Integration tests for end-to-end flow
├── .gitignore # Ignored files and folders
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── credentials.json # Gmail API credentials (ignored in git)
├── token.json # OAuth token (auto-generated, ignored in git)
├── rules.json # Predefined email processing rules
├── main.py # Entry point: fetch, store, process emails
├── fetch_mails.py # Gmail API authentication & email fetching
├── db_utils.py # MySQL database initialization & storage
└── rules_processing.py # Rule evaluation & Gmail actions
├── display_db.py  # Helper to get a glimpse of db
```

## Setup & Installation

1. **Clone the repository**  
   ```bash
   git clone <repository_url>
   cd <repository_folder>

2. **Install Python dependencies**
   ```bash
    pip install -r requirements.txt

3. **Set up Gmail API credentials**
   - Create a project in Google Cloud Console
   - Enable Gmail API and follow the instructions to get OAuth credentials
   - Download credentials.json and place it in the project root

4. **Configure Database**
   - Ensure MySQL server is running
   - Update database connection in db_utils.py if needed
   - Replace the name and password in db_utils.py with your mysql credentials

## Usage
1. **Run the main script**
   This will fetch emails, store them in the database, and apply rules:
   ```bash
   python main.py

2. **Customize Rules**
   - Open rules.json
   - Add or modify rules based on your email processing needs
      - Each rule has predicate (All / Any), conditions (field, predicate, value), and actions (mark_as_read, mark_as_unread, move_to:<Label>)

3. **View Emails in Database**
    - Connect to your MySQL database and query the email_inbox table:
    ```bash
     SELECT * FROM email_inbox;


4. **Modify Database or Script (Optional)**
    - Adjust MAX_EMAILS in main.py to fetch more emails.

## Testing

This project includes **unit tests** for individual modules (`db_utils.py`, `fetch_mails.py`, `rules_processing.py`) and **integration test** to verify the main workflow.

### Running Unit & Integration Tests

# Make sure MySQL server is running before running integration test.

1. **Unit Tests: To test individual modules**
```bash
py -m unittest tests.test_db_utils
py -m unittest tests.test_fetch_mails
py -m unittest tests.test_rules_processing
```
2. **Integration Test: End-to-end flow with MySQL (mocked Gmail service)**
```bash
py -m unittest tests.test_integration
```
3. **Using `pytest`: To run all together**:

```bash
pip install pytest
pytest



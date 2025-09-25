import json
from datetime import datetime
from email.utils import parsedate_to_datetime  # handles Gmail date format
import re 

def load_rules(path="rules.json"):
    """Load rules from a JSON file."""
    with open(path, "r") as f:
        return json.load(f)

def evaluate(email, rule_set):
    """Check if an email satisfies the rule set (All/Any)."""
    predicate = rule_set.get("predicate", "All")
    rules = rule_set.get("rules", [])
    results = []

    for r in rules:
        field = r["field"].lower()
        value = r["value"]
        email_val = email.get(field, "")

        # simple string match (case-insensitive)
        if r["predicate"].lower() == "contains":
            results.append(value.lower() in str(email_val).lower())
        elif r["predicate"].lower() == "equals":
            results.append(str(email_val).lower() == value.lower())

    return all(results) if predicate.lower() == "all" else any(results)

def sanitize_label_name(name):
    """Keep only valid characters for Gmail labels."""
    sanitized = re.sub(r'[^a-zA-Z0-9 _-]', '', name).strip()
    return sanitized

def apply(service, email_id, actions):
    """Apply actions to the email via Gmail API."""
    for action in actions:
        action_lower = action.lower()
        try:
            if action_lower == "mark_as_read":
                service.users().messages().modify(
                    userId="me",
                    id=email_id,
                    body={"removeLabelIds": ["UNREAD"]}
                ).execute()
            elif action_lower == "mark_as_unread":
                service.users().messages().modify(
                    userId="me",
                    id=email_id,
                    body={"addLabelIds": ["UNREAD"]}
                ).execute()
            elif action_lower.startswith("move_to:"):
                label = action.split(":", 1)[1].strip()
                label = sanitize_label_name(label)
                if not label:
                    print(f"[Skipped] Invalid label for email {email_id}")
                    continue

                # Get existing labels
                labels = service.users().labels().list(userId="me").execute().get("labels", [])
                label_id = next((l["id"] for l in labels if l["name"] == label), None)

                # Create label if it doesn't exist
                if not label_id:
                    label_id = service.users().labels().create(
                        userId="me",
                        body={"name": label}
                    ).execute()["id"]

                # Apply label
                service.users().messages().modify(
                    userId="me",
                    id=email_id,
                    body={"addLabelIds": [label_id]}
                ).execute()
                print(f"[Applied] Label '{label}' to email {email_id}")

        except Exception as e:
            print(f"[Error] Applying action '{action}' to {email_id}: {e}")
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
     # Fetch current labels on this email
    msg = service.users().messages().get(userId="me", id=email_id, format="metadata").execute()
    current_labels = set(msg.get("labelIds", []))

    # Fetch all existing labels once
    all_labels = service.users().labels().list(userId="me").execute().get("labels", [])
    label_map = {l["name"]: l["id"] for l in all_labels}

    for action in actions:
        action_lower = action.lower()
        try:
            if action_lower == "mark_as_read":
                if "UNREAD" in current_labels:
                    service.users().messages().modify(
                        userId="me",
                        id=email_id,
                        body={"removeLabelIds": ["UNREAD"]}
                    ).execute()
                    current_labels.discard("UNREAD")
            elif action_lower == "mark_as_unread":
                if "UNREAD" not in current_labels:
                    service.users().messages().modify(
                        userId="me",
                        id=email_id,
                        body={"addLabelIds": ["UNREAD"]}
                    ).execute()
                    current_labels.add("UNREAD")
            elif action_lower.startswith("move_to:"):
                label_name = action.split(":", 1)[1].strip()
                if not label_name:
                    print(f"Skipping invalid label for email {email_id}")
                    continue

                # Get label ID, create if missing
                label_id = label_map.get(label_name)
                if not label_id:
                    label_id = service.users().labels().create(
                        userId="me",
                        body={"name": label_name}
                    ).execute()["id"]
                    label_map[label_name] = label_id

                if label_id not in current_labels:
                    service.users().messages().modify(
                        userId="me",
                        id=email_id,
                        body={"addLabelIds": [label_id]}
                    ).execute()
                    current_labels.add(label_id)

        except Exception as e:
            print(f"Error applying action '{action}' to {email_id}: {e}")
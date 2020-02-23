import json
import sys

if len(sys.argv) == 1:
    print(f"USAGE: python {sys.argv[0]} MESSAGES_FILE [required messages]")
    sys.exit(1)

with open(sys.argv[1], "r") as messages_file:
    messages = json.load(messages_file)

missing_messages = []
for required_message in sys.argv[2:]:
    if required_message in ("add_hidden_role_public", "remove_hidden_role_public"):
        continue
    if required_message not in messages.keys():
        missing_messages.append(required_message)

if missing_messages:
    print("ERROR: Missing the following messages...")
    for message in missing_messages:
        print(f"\t{message}")
    sys.exit(1)

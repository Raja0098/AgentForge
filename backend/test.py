# test.py
import requests
import json

URL = "http://127.0.0.1:8000/api/execute"

payload = {
    "workflow": {
        "nodes": [
            {
                "id": "node_1",
                "type": "tool",
                "subtype": "parser"
            },
            {
                "id": "node_2",
                "type": "agent",
                "subtype": "document_processor"
            }
        ],
        "connections": [
            {
                "source": "node_1",
                "target": "node_2"
            }
        ]
    },
    "input_data": {
        "node_1": {
            "content": "Hello World",
            "file_type": "txt"
        },
        "node_2": {
            "text": "Summarize this"
        }
    }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(URL, json=payload, headers=headers)

print("Status Code:", response.status_code)

try:
    data = response.json()
except Exception as e:
    print("Failed to parse JSON:", e)
    print(response.text)
    exit(1)

print("\n=== FULL RESPONSE ===")
print(json.dumps(data, indent=2))

print("\n=== RESULT KEYS ===")
if data.get("success"):
    print(list(data.get("result", {}).keys()))
else:
    print("Execution failed:", data.get("error"))

print("\n=== LOGS ===")
for log in data.get("logs", []):
    print(log)

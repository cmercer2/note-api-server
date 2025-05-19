from flask import Flask, request, jsonify
import requests
import json
import re

app = Flask(__name__)

WEBHOOK_URL = 'https://usetrmnl.com/api/custom_plugins/40a4e8a8-832f-4d10-b84b-322a51351199'

@app.route('/note', methods=['GET', 'POST'])
def note():
    if request.method == 'POST':
        try:
            note_data = request.get_json()
            note = note_data.get('list', '')

            # Save locally
            lines = [re.sub(r'^\s*[\u2022\u2023\u25E6\u2043\u2219\-•]+', '', line).strip() for line in note.splitlines() if line.strip()]
            plain_text = '\n'.join(lines)
            with open('received_note.txt', 'w') as f:
                f.write(plain_text)

            # Forward to webhook
            payload = {
                "merge_variables": {
                    "title": "Freezer Contents",
                    "list": plain_text.splitlines()
                }
            }
            print("Webhook payload:\n", json.dumps(payload, indent=2))
            response = requests.post(WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'})

            return jsonify({
                'status': 'received',
                'length': len(note),
                'webhook_status': response.status_code
            })

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    else:
        try:
            with open('received_note.txt', 'r') as f:
                content = f.read()
            return jsonify(content.splitlines())
        except FileNotFoundError:
            return jsonify({'note': '', 'length': 0})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
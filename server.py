from flask import Flask, request, jsonify
import requests
import json
import re
from config import FREEZER_PLUGIN_WEBHOOK_URL, MEAL_PLAN_WEBHOOK_URL

app = Flask(__name__)

@app.route('/freezer-list', methods=['GET', 'POST'])
def note():
    if request.method == 'POST':
        try:
            note_data = request.get_json()
            note = note_data.get('list', '')

            # Save locally
            lines = []
            # Remove bullet points and duplicates, sort alphabetically
            for line in note.splitlines():
                line = re.sub(r'^\s*[\u2022\u2023\u25E6\u2043\u2219\-•]+', '', line).strip()
                if line:
                    lines.append(line)
            lines = list(set(lines))  # Remove duplicates
            lines.sort()  # Sort alphabetically
            plain_text = '\n'.join(lines)
            with open('received_freezer_list.txt', 'w') as f:
                f.write(plain_text)

            # Forward to webhook
            payload = {
                "merge_variables": {
                    "title": "Freezer Contents",
                    "list": plain_text.splitlines()
                }
            }
            print("Webhook payload:\n", json.dumps(payload, indent=2))
            response = requests.post(FREEZER_PLUGIN_WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'})

            return jsonify({
                'status': 'received',
                'length': len(note),
                'webhook_status': response.status_code
            })

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    else:
        try:
            with open('received_freezer_list.txt', 'r') as f:
                content = f.read()
            return jsonify(content.splitlines())
        except FileNotFoundError:
            return jsonify({'note': '', 'length': 0})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# --- Meal plan endpoint ---
@app.route('/meal-plan', methods=['GET', 'POST'])
def meal_plan():
    if request.method == 'GET':
        try:
            with open('received_meal_plan.txt', 'r') as f:
                content = json.load(f)
            weekday_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            ordered_content = {day: content[day] for day in weekday_order if day in content}
            return jsonify(ordered_content)
        except FileNotFoundError:
            return jsonify({'note': '', 'length': 0})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    try:
        note_data = request.get_json()
        note = note_data.get('list', '')

        # Convert bulleted list into a dictionary
        meal_plan_dict = {}
        current_day = None
        for line in note.splitlines():
            line = line.strip()
            line = re.sub(r'^[\u2022\u2023\u25E6\u2043\u2219\-•\*]+', '', line).strip()
            if line.endswith(':'):
                current_day = line[:-1]
                meal_plan_dict[current_day] = []
            elif current_day:
                meal_plan_dict[current_day].append(line)

        # Sort by weekday order
        weekday_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        ordered_meal_plan = {day: meal_plan_dict[day] for day in weekday_order if day in meal_plan_dict}

        with open('received_meal_plan.txt', 'w') as f:
            f.write(json.dumps(ordered_meal_plan, indent=2))

        # Forward to webhook
        payload = {
            "merge_variables": {
                "title": "Weekly Meal Plan",
                "list": ordered_meal_plan
            }
        }
        print("Meal plan webhook payload:\n", json.dumps(payload, indent=2))
        response = requests.post(MEAL_PLAN_WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'})

        return jsonify({
            'status': 'received',
            'length': len(note),
            'webhook_status': response.status_code
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
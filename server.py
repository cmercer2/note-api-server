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
            raw_data = request.get_data(as_text=True)
            with open('raw_freezer_request.txt', 'w') as f:
                f.write(raw_data)

            note_data = json.loads(raw_data)
            note = note_data.get('list', '')

            freezer_dict = {}
            current_category = None
            current_subcategory = None

            lines = [line for line in note.splitlines() if line.strip()]
            if lines and lines[0].strip().lower() == 'freezer':
                lines = lines[1:]

            for idx, raw in enumerate(lines):
                indent = len(raw) - len(raw.lstrip())
                text = re.sub(r'^[\*\-•\u2022\u2023\u25E6\u2043\u2219]+\s*', '', raw.strip())

                if indent == 0:
                    current_category = text
                    freezer_dict[current_category] = []
                    current_subcategory = None
                elif indent == 4:
                    # Peek at next line to decide if this is a subcategory or item
                    next_indent = None
                    if idx + 1 < len(lines):
                        next_raw = lines[idx + 1]
                        next_indent = len(next_raw) - len(next_raw.lstrip())

                    if next_indent is not None and next_indent > indent:
                        current_subcategory = text
                        if isinstance(freezer_dict[current_category], list):
                            freezer_dict[current_category] = {}
                        freezer_dict[current_category][current_subcategory] = []
                    else:
                        # Treat this line as an item
                        if isinstance(freezer_dict[current_category], dict):
                            freezer_dict[current_category][text] = []
                        else:
                            freezer_dict[current_category].append(text)
                elif indent >= 8:
                    if current_subcategory and isinstance(freezer_dict[current_category], dict):
                        freezer_dict[current_category][current_subcategory].append(text)
                    else:
                        freezer_dict[current_category].append(text)

            with open('received_freezer_list.txt', 'w') as f:
                f.write(json.dumps(freezer_dict, indent=2))

            # Forward to webhook
            payload = {
                "merge_variables": {
                    "title": "Freezer Contents",
                    "list": freezer_dict
                }
            }
            print("Freezer webhook payload:\n", json.dumps(payload, indent=2))
            response = requests.post(FREEZER_PLUGIN_WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'})

            return jsonify({'status': 'parsed', 'length': len(note), 'webhook_status': response.status_code})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    else:
        try:
            with open('raw_freezer_request.txt', 'r') as f:
                content = json.load(f)
            return jsonify(content)
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
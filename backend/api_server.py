from flask import Flask, request, jsonify
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PENDING_FILE = "pending_student.json"

@app.route('/pending_student', methods=['POST'])
def register_pending_student():
    data = request.get_json()
    student_id = data.get("student_id")
    name = data.get("name")

    if not student_id or not name:
        return jsonify({"error": "Missing student_id or name"}), 400

    with open(PENDING_FILE, "w") as f:
        json.dump({"student_id": student_id, "name": name}, f)

    return jsonify({"status": "Pending registration saved"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Backend running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify, send_from_directory, make_response
import sqlite3
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'competition.db'
CORS(app)

@app.route('/get_evaluation_dimensions', methods=['GET'])
def get_evaluation_dimensions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, weight , description,project_id FROM evaluation_dimension')
    dimensions = cursor.fetchall()
    conn.close()
    result = [{'id': dim[0], 'name': dim[1], 'weight': dim[2], 'description': dim[3], 'project_id': dim[4]} for dim in dimensions]
    return jsonify(result)

@app.route('/')
def index():
    return send_from_directory('templates', 'app.html')

@app.route('/get_videos', methods=['GET'])
def get_videos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url FROM entry')
    videos = cursor.fetchall()
    conn.close()
    result = [{'id': vid[0], 'title': vid[1], 'url': vid[2]} for vid in videos]
    return jsonify(result)

@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.get_json()
    entry_id = data.get('entry_id')
    project_id = data.get('project_id')
    judge_id = data.get('judge_id')
    score = data.get('score')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO evaluation_record (entry_id, project_id, judge_id, score, score_time)
        VALUES (?,?,?,?,?)
    ''', (entry_id, project_id, judge_id, score, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))  
    conn.commit()
    conn.close()
    return jsonify({'message': '评分提交成功'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    account = data.get('account')
    role = data.get('role')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, organization_id FROM judge WHERE account = ? AND role = ?', (account, role))
    user = cursor.fetchone()
    conn.close()

    if user:
        response = make_response(jsonify({'success': True, 'id': user[0], 'organization': user[1]}))
        return response
    else:
        return jsonify({'success': False, 'message': '登录失败，请检查账号和身份！'}), 401

if __name__ == '__main__':
    app.run(debug=True)
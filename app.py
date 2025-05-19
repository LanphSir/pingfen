from flask import Flask, request, jsonify, send_from_directory, make_response
import sqlite3
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'competition.db'
CORS(app)

@app.route('/')
@app.route('/index.html')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/evaluation.html')
def evaluation_page():
    return send_from_directory('templates', 'evaluation.html')

@app.route('/login.html')
def login_page():
    return send_from_directory('templates', 'login.html')

#获取项目接口
@app.route('/get_evaluation_dimensions', methods=['GET'])
def get_evaluation_dimensions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT ed.id,ed.name,ed.weight,ed.description, ed.project_id,eg.score FROM evaluation_dimension ed INNER JOIN evaluation_grade eg ON ed.id = eg.dimension_id;')
    dimensions = cursor.fetchall()
    conn.close()
    result = [{'id': dim[0], 'name': dim[1], 'weight': dim[2], 'description': dim[3], 'project_id': dim[4], 'score': dim[5]} for dim in dimensions]
    return jsonify(result)

#获取视频接口
@app.route('/get_videos', methods=['GET'])
def get_videos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url FROM entry')
    videos = cursor.fetchall()
    conn.close()
    result = [{'id': vid[0], 'title': vid[1], 'url': vid[2]} for vid in videos]
    return jsonify(result)

#提交评分接口
@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.get_json()
    entry_id = data.get('entry_id')
    project_id = data.get('project_id')
    judge_id = data.get('judge_id')
    score = data.get('score')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 检查是否已经评分
    cursor.execute('SELECT COUNT(*) FROM evaluation_record WHERE entry_id =? AND project_id =? AND judge_id =?', (entry_id, project_id, judge_id))
    if cursor.fetchone()[0] > 0:
        # 如果已经评分，更新评分
        cursor.execute('''
            UPDATE evaluation_record
            SET score =?, score_time =?
            WHERE entry_id =? AND project_id =? AND judge_id =?
        ''', (score, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), entry_id, project_id, judge_id))
    else:
        # 如果没有评分，插入新的评分记录    
        cursor.execute('''
            INSERT INTO evaluation_record (entry_id, project_id, judge_id, score, score_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_id, project_id, judge_id, score, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    return jsonify({'message': '评分提交成功'}), 201

#登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    account = data.get('account')
    role = data.get('role')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, role FROM judge WHERE account = ? AND role = ?', (account, role))
    user = cursor.fetchone()
    conn.close()

    if user:
        response = make_response(jsonify({'success': True, 'id': user[0], 'role': user[1]}))
        return response
    else:
        return jsonify({'success': False, 'message': '登录失败，请检查账号和身份！'}), 401

#获取评委信息接口
@app.route('/get_judge_projects', methods=['POST'])
def get_judge_projects():
    data = request.get_json()
    judge_id = data.get('judge_id')
    role = data.get('role')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #不同身份获取不同的项目 
    if role == 'admin':
        cursor.execute('SELECT id, name FROM project')
    else:
        cursor.execute('SELECT pa.id, pa.name FROM project pa JOIN judge_assignment ja ON pa.id = ja.project_id WHERE ja.judge_id = ?', (judge_id,))

    projects = cursor.fetchall()
    result = []
    for project in projects:
        project_id = project[0]
        cursor.execute('SELECT COUNT(DISTINCT er.entry_id) FROM evaluation_record er WHERE er.project_id = ?', (project_id,))
        reviewed_count = cursor.fetchone()[0] or 0
        cursor.execute('SELECT COUNT(DISTINCT e.id) FROM entry e WHERE e.project_id = ?', (project_id,))
        total_count = cursor.fetchone()[0] or 0
        unreviewed_count = total_count - reviewed_count

        result.append({
            'id': project_id,
            'name': project[1],
            'reviewed_count': reviewed_count,
            'unreviewed_count': unreviewed_count
        })

    conn.close()
    return jsonify(result)

#查询已完成评分的项目作品
@app.route('/get_reviewed_entries', methods=['POST'])
def get_reviewed_entries():
    data = request.get_json()
    judge_id = data.get('judge_id')
    project_id = data.get('project_id')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, e.title, er.score, er.score_time
        FROM entry e
        JOIN evaluation_record er ON e.id = er.entry_id
        WHERE er.judge_id = ? AND er.project_id = ?
    ''', (judge_id, project_id))
    entries = cursor.fetchall()
    conn.close()

    result = [{'id': entry[0], 'title': entry[1], 'score': entry[2], 'score_time': entry[3]} for entry in entries]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
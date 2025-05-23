from flask import Flask, request, jsonify, send_from_directory, make_response
import sqlite3
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'competition.db'
CORS(app)

@app.route('/')
@app.route('/index')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/evaluation/<project_id>')
def evaluation_page(project_id):
    print("evaluation: "+project_id)
    return send_from_directory('templates', 'evaluation.html')

@app.route('/list/<project_id>')
def entries_list(project_id):
    return send_from_directory('templates', 'list.html') 

@app.route('/login')
def login_page():
    return send_from_directory('templates', 'login.html')

@app.route('/userinfo')
def user_info():
    return send_from_directory('templates', 'userinfo.html')

@app.route('/update/<entry_id>')
def update_page(entry_id):
    return send_from_directory('templates', 'update_evaluation.html')

@app.route('/upload')
def upload_page():
    return send_from_directory('templates', 'upload.html')


#获取上传作品表单接口
@app.route('/get_upload_form/<int:competition_id>', methods=['GET'])
def get_upload_form(competition_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT id, name,department,remark FROM organization where remark !='admin' or remark is null''')
    organizations = cursor.fetchall()
    
    cursor.execute('SELECT id, name FROM project where competition_id = ?', (competition_id,))
    projects = cursor.fetchall()
    conn.close()
    result = [{'id': org[0], 'name': org[1],'department':org[2],'remark':org[3]} for org in organizations]
    result2 = [{'id': proj[0], 'name': proj[1]} for proj in projects]
    return jsonify({'organizations': result, 'projects': result2})
    

#获取项目接口
@app.route('/get_evaluation_dimensions', methods=['POST'])
def get_evaluation_dimensions():
    data = request.get_json()
    projectId = data.get('project_id')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT ed.id,ed.name,ed.weight,ed.description, ed.project_id,eg.score FROM evaluation_dimension ed INNER JOIN evaluation_grade eg ON ed.id = eg.dimension_id where ed.project_id = ? order by ed.id;',(projectId,))
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

#通过视频ID获取视频接口
@app.route('/get_entry_info/<int:entry_id>', methods=['POST'])
def get_entry_info(entry_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url,project_id FROM entry WHERE id = ?', (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    return jsonify({'id': entry[0], 'title': entry[1], 'url': entry[2], 'project_id': entry[3]})

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
    cursor.execute('''SELECT id,name,role
                FROM judge j 
                WHERE account = ? AND role = ?''', (account, role))
    user = cursor.fetchone()
    conn.close()

    if user:
        response = make_response(jsonify({'success': True, 'id': user[0], 'name': user[1], 'role': user[2]}))
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
        cursor.execute('SELECT pa.id, pa.name,pa.type FROM project pa JOIN judge_assignment ja ON pa.id = ja.project_id WHERE ja.judge_id = ?', (judge_id,))

    projects = cursor.fetchall()
    result = []
    for project in projects:
        project_id = project[0]
        cursor.execute('SELECT COUNT(id) FROM evaluation_record WHERE project_id = ? AND judge_id = ?', (project_id,judge_id,))
        reviewed_count = cursor.fetchone()[0] or 0
        cursor.execute('SELECT COUNT(DISTINCT e.id) FROM entry e join project p on e.project_id = p.id join judge_assignment ja on p.id = ja.project_id WHERE ja.judge_id = ? AND p.id = ?', (judge_id, project_id))
        total_count = cursor.fetchone()[0] or 0
        unreviewed_count = total_count - reviewed_count

        result.append({
            'id': project_id,
            'name': project[1],
            'type': project[2],
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
    page_size = data.get('page_size', 10)  # 每页显示的记录数，默认为10
    page_number = data.get('page_number', 1)  # 当前页码，默认为1

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, e.title, er.score, er.score_time, p.name, p.type
        FROM entry e
        JOIN evaluation_record er ON e.id = er.entry_id
        JOIN project p ON e.project_id = p.id
        WHERE er.judge_id = ? AND er.project_id = ?
        ORDER BY er.score_time DESC
        LIMIT ? OFFSET ?
    ''', (judge_id, project_id, page_size, (page_number - 1) * page_size))
    entries = cursor.fetchall()
    
    cursor.execute('''
        SELECT COUNT(*)
        FROM entry e
        JOIN evaluation_record er ON e.id = er.entry_id
        JOIN project p ON e.project_id = p.id
        WHERE er.judge_id =? AND er.project_id =?
    ''', (judge_id, project_id))
    total_count = cursor.fetchone()[0]
    conn.close()

    result = [{'id': entry[0], 'title': entry[1], 'score': entry[2], 'score_time': entry[3], 'project_name': entry[4], 'project_type': entry[5], 'total_count': total_count} for entry in entries]
    return jsonify(result)

#查询未完成评分的项目作品
@app.route('/get_unreviewed_entries', methods=['POST'])
def get_unreviewed_entries():
    data = request.get_json()
    judge_id = data.get('judge_id')
    project_id = data.get('project_id')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ja.judge_id,ja.project_id,ja.assign_time,
                e.id, e.title, e.url, e.type, 
                p.name, p.type,e.description
            FROM judge_assignment ja
            JOIN entry e ON ja.project_id = e.project_id
            JOIN project p ON ja.project_id = p.id
            WHERE ja.judge_id = ?AND ja.project_id = ?;
    ''', (judge_id, project_id))
    entries = cursor.fetchall()
    cursor.execute('''
        SELECT e.id, e.title, er.score, er.score_time
        FROM entry e
        JOIN evaluation_record er ON e.id = er.entry_id
        WHERE er.judge_id = ? AND er.project_id = ?
    ''', (judge_id, project_id))
    reviewed_entries = cursor.fetchall()
    reviewed_entry_ids = set(entry[0] for entry in reviewed_entries)
    unentries = [entry for entry in entries if entry[3] not in reviewed_entry_ids]
    conn.close()
    
    
    result = [{'entry_id': entry[3],'judge_id': entry[0], 'project_id': entry[1], 'title': entry[4], 'url': entry[5], 'type': entry[6], 'project_name': entry[7], 'project_type': entry[8], 'description': entry[9]} for entry in unentries]
    return jsonify(result)

#查询评分记录
@app.route('/get_evaluation_record', methods=['POST'])
def get_evaluation_record():
    data = request.get_json()
    entry_id = data.get('entry_id')
    judge_id = data.get('judge_id')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, e.title, e.url, er.score, p.name, p.type,p.id,e.description
        FROM entry e
        JOIN evaluation_record er ON e.id = er.entry_id
        join project p on e.project_id = p.id
        WHERE er.entry_id = ? AND er.judge_id = ?;
    ''', (entry_id, judge_id))
    records = cursor.fetchone()
    
    cursor.execute('''
        SELECT ed.id,ed.name,ed.weight,ed.description, eg.score
        FROM evaluation_dimension ed
        JOIN evaluation_grade eg ON ed.id = eg.dimension_id
        WHERE ed.project_id =?
        ORDER BY ed.id;
    ''', (records[6],))
    dimensions = cursor.fetchall() 
    conn.close()

    return jsonify({'evaluation':{'entry_id': records[0], 'title': records[1], 'url': records[2], 'score': records[3], 'project_name': records[4], 'project_type': records[5], 'project_id': records[6], 'description': records[7]}, 'dimensions': [{'id': dim[0], 'name': dim[1], 'weight': dim[2], 'description': dim[3], 'score': dim[4]} for dim in dimensions]})

@app.route('/update_evaluation', methods=['POST'])
def update_evaluation():
    data = request.get_json()
    entry_id = data.get('entry_id')
    project_id = data.get('project_id')
    judge_id = data.get('judge_id')
    score = data.get('score')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE evaluation_record
        SET score =?, score_time =?
        WHERE entry_id =? AND project_id =? AND judge_id =?
    ''', (score, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), entry_id, project_id, judge_id))
    conn.commit()
    conn.close()
    return jsonify({'message': '评分更新成功'})

#上传作品接口
@app.route('/upload_entry', methods=['POST'])
def upload_entry():
    data = {
        'school': request.form.get('school'),
        'department': request.form.get('department'),
        'account': request.form.get('account'),
        'name': request.form.get('name'),
        'contact': request.form.get('contact'),
        'project': request.form.get('project'),
        'workName': request.form.get('workName'),
        'description': request.form.get('description'),
        'video': request.files.get('videoUpload')
    }    
    
    if data['video']:
        import os
        video_path = f'uploads/{data["video"].filename}'
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        data['video'].save(video_path)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查是否已经存在相同的作品
        cursor.execute('''
            SELECT COUNT(*) FROM entry e join entry_participant ep on e.id = ep.entry_id join participant p on ep.participant_id = p.id
            where e.project_id =? and p.organization_id =? and p.account =? 
        ''', (data['project'], data['department'], data['name']))
        count = cursor.fetchone()[0]
        if count>0 :
            conn.close()
            return jsonify({'message': '您已提交过相同项目的作品'})       
        
        video_path = f'uploads/{data["video"].filename}'
        data['video'].save(video_path)
        # 插入作品
        cursor.execute('''
            INSERT INTO entry (title, url, type, submit_time,project_id)
            VALUES (?,?,?,?,?)
        ''', (data['workName'], video_path, 'video', datetime.now().strftime('%Y-%m-%d %H:%M:%S'),data['project']))
        entry_id = cursor.lastrowid
        
        #查询是否有相同的人员或参赛组织
        cursor.execute('''
            SELECT id FROM participant
            where organization_id =? and account =?
        ''', (data['department'], data['account']))
        participant = cursor.fetchone()
        print(participant)
        participant_id = participant[0] if participant else None
        if participant_id is None:        
            cursor.execute('''
                INSERT INTO participant (name, organization_id, account, contact)
                VALUES (?,?,?,?)
            ''', (data['name'], data['department'], data['account'], data['contact']))
            participant_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO entry_participant (entry_id, participant_id)
            VALUES (?,?)
        ''', (entry_id, participant_id))
        
        conn.commit()
        conn.close()
    
    return jsonify({'message': '作品上传成功'+data['workName']})


if __name__ == '__main__':
    app.run(debug=True)
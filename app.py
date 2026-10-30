from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this'

SITE_OWNER = "Motalli Ibn Mozammel"
APP_NAME = f"{SITE_OWNER}'s CloudPad"

# সাময়িক মেমোরি ডাটাবেজ
users = {}
notes = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .navbar-brand { font-weight: bold; color: #0d6efd !important; }
        .editor-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        #editor { min-height: 250px; border: 1px solid #ced4da; padding: 10px; border-radius: 4px; background: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">{{ app_name }}</a>
            <div>
                {% if username %}
                    <span class="me-3">স্বাগতম, <strong>{{ username }}</strong></span>
                    <a href="/logout" class="btn btn-outline-danger btn-sm">লগআউট</a>
                {% else %}
                    <a href="/login" class="btn btn-outline-primary btn-sm me-2">লগইন</a>
                    <a href="/register" class="btn btn-primary btn-sm">রেজিস্টার</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container">
        {% if username %}
            <div class="row">
                <div class="col-md-8 offset-md-2 editor-container">
                    <h4>নতুন নোট / কোড লিখুন</h4>
                    <form action="/save" method="POST">
                        <div class="mb-3">
                            <input type="text" name="title" class="form-control" placeholder="টাইটেল দিন" required>
                        </div>
                        
                        <div class="mb-2 d-flex gap-2 align-items-center flex-wrap">
                            <label class="small text-muted">ফন্ট:</label>
                            <select onchange="document.execCommand('fontName', false, this.value);" class="form-select form-select-sm w-auto">
                                <option value="Arial">Arial</option>
                                <option value="Times New Roman">Times New Roman</option>
                                <option value="Courier New">Courier New (Code)</option>
                                <option value="Georgia">Georgia</option>
                                <option value="Verdana">Verdana</option>
                            </select>
                            
                            <button type="button" class="btn btn-sm btn-light border" onclick="document.execCommand('bold', false, null);"><b>B</b></button>
                            <button type="button" class="btn btn-sm btn-light border" onclick="document.execCommand('italic', false, null);"><i>I</i></button>
                            <button type="button" class="btn btn-sm btn-light border" onclick="document.execCommand('underline', false, null);"><u>U</u></button>
                        </div>

                        <div id="editor" contenteditable="true" class="mb-3"></div>
                        <input type="hidden" name="content" id="hiddenContent">

                        <button type="submit" onclick="document.getElementById('hiddenContent').value = document.getElementById('editor').innerHTML;" class="btn btn-success">সেভ করুন</button>
                    </form>

                    <hr class="my-4">
                    <h5>আপনার সেভ করা নোটসমূহ:</h5>
                    <ul class="list-group">
                        {% for note in user_notes %}
                            <li class="list-group-item d-flex justify-content-between align-items-start mb-2">
                                <div>
                                    <strong>{{ note.title }}</strong>
                                    <div class="border p-2 bg-light rounded mt-1" style="max-height: 150px; overflow-y: auto;">
                                        {{ note.content | safe }}
                                    </div>
                                </div>
                            </li>
                        {% else %}
                            <li class="list-group-item text-muted">এখনো কোনো নোট সেভ করা হয়নি।</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        {% else %}
            <div class="text-center py-5">
                <h1>{{ app_name }}-এ স্বাগতম</h1>
                <p class="lead">যেকোনো জায়গায় বসেই আপনার দরকারি নোট ও কোড সুরক্ষিত রাখুন।</p>
                <a href="/register" class="btn btn-primary btn-lg">এখনই অ্যাকাউন্ট খুলুন</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    username = session.get('user')
    user_notes = notes.get(username, []) if username else []
    return render_template_string(HTML_TEMPLATE, app_name=APP_NAME, username=username, user_notes=user_notes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname in users:
            return "ইউজার নাম আগে থেকেই নেওয়া আছে। ব্যাকে যান।"
        users[uname] = generate_password_hash(pwd)
        session['user'] = uname
        return redirect(url_for('home'))
    return '''
        <div style="max-width:300px;margin:50px auto;font-family:sans-serif;">
            <h3>রেজিস্ট্রেশন</h3>
            <form method="post">
                <input name="username" placeholder="ইউজারনেম" required style="width:100%;margin-bottom:10px;padding:8px;"><br>
                <input type="password" name="password" placeholder="পাসওয়ার্ড" required style="width:100%;margin-bottom:10px;padding:8px;"><br>
                <button type="submit" style="width:100%;padding:8px;background:#0d6efd;color:white;border:none;">সাইন আপ</button>
            </form>
        </div>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname in users and check_password_hash(users[uname], pwd):
            session['user'] = uname
            return redirect(url_for('home'))
        return "ইউজারনেম বা পাসওয়ার্ড ভুল। ব্যাকে যান।"
    return '''
        <div style="max-width:300px;margin:50px auto;font-family:sans-serif;">
            <h3>লগইন</h3>
            <form method="post">
                <input name="username" placeholder="ইউজারনেম" required style="width:100%;margin-bottom:10px;padding:8px;"><br>
                <input type="password" name="password" placeholder="পাসওয়ার্ড" required style="width:100%;margin-bottom:10px;padding:8px;"><br>
                <button type="submit" style="width:100%;padding:8px;background:#198754;color:white;border:none;">লগইন</button>
            </form>
        </div>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/save', methods=['POST'])
def save():
    if 'user' not in session:
        return redirect(url_for('login'))
    title = request.form['title']
    content = request.form['content']
    username = session['user']
    
    if username not in notes:
        notes[username] = []
    notes[username].append({'title': title, 'content': content})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
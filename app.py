import json
import os
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# 데이터 저장
users_db = {}
messages_db = {}
settings_db = {}

def save_data():
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users_db, f, ensure_ascii=False, indent=2)
    with open('messages.json', 'w', encoding='utf-8') as f:
        json.dump(messages_db, f, ensure_ascii=False, indent=2)
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings_db, f, ensure_ascii=False, indent=2)

def load_data():
    global users_db, messages_db, settings_db
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r', encoding='utf-8') as f:
                users_db = json.load(f)
        if os.path.exists('messages.json'):
            with open('messages.json', 'r', encoding='utf-8') as f:
                messages_db = json.load(f)
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as f:
                settings_db = json.load(f)
    except:
        users_db = {}
        messages_db = {}
        settings_db = {}

load_data()

LOGIN_HTML = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>추석 나무 꾸미기</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Malgun Gothic', sans-serif;
            background: linear-gradient(180deg, #2a1810 0%, #1a0f08 50%, #0f0604 100%);
            min-height: 100vh; display: flex; justify-content: center; align-items: center;
            position: relative; overflow: hidden;
        }
        body::before {
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20px 30px, #fff4e6, transparent),
                radial-gradient(2px 2px at 40px 70px, #fff8f0, transparent),
                radial-gradient(1px 1px at 90px 40px, #ffe4b5, transparent);
            background-repeat: repeat; background-size: 200px 100px; opacity: 0.6; pointer-events: none;
        }
        .container {
            background: linear-gradient(145deg, #f4e8d0, #e8dcc0); padding: 40px; border-radius: 20px;
            box-shadow: 0 0 0 3px #8b4513, 0 15px 35px rgba(0, 0, 0, 0.5);
            text-align: center; width: 100%; max-width: 400px; border: 3px solid #d2691e; position: relative; z-index: 1;
        }
        h1 { color: #8b4513; margin-bottom: 30px; font-size: 2em; text-shadow: 2px 2px 0px #daa520; }
        .moon { font-size: 4em; margin-bottom: 20px; filter: drop-shadow(0 0 20px #fff8dc); }
        input {
            width: 100%; padding: 15px; margin: 10px 0; border: 3px solid #cd853f; border-radius: 10px;
            font-size: 16px; background: #faf0e6; color: #8b4513; transition: all 0.3s ease;
        }
        input:focus { border-color: #daa520; outline: none; box-shadow: 0 0 10px rgba(218, 165, 32, 0.5); }
        button {
            width: 100%; padding: 15px; margin: 10px 0; border: none; border-radius: 10px;
            background: linear-gradient(45deg, #daa520, #cd853f); color: white; font-size: 16px; font-weight: bold;
            cursor: pointer; transition: all 0.3s ease; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(218, 165, 32, 0.4); }
        .message { margin-top: 20px; padding: 10px; border-radius: 5px; }
        .error { background: #ffe6e6; color: #d00; border: 1px solid #fcc; }
        .success { background: #e6ffe6; color: #060; border: 1px solid #cfc; }
        .info { background: #e6f3ff; color: #006; border: 1px solid #ccf; }
    </style>
</head>
<body>
    <div class="container">
        <div class="moon">🌕</div>
        <h1>추석 나무 꾸미기</h1>
        <p style="color: #8b4513; margin-bottom: 20px;">가족과 함께하는 따뜻한 추석</p>
        
        <form method="POST" action="/login">
            <input type="text" name="nickname" placeholder="닉네임" required>
            <input type="password" name="password" placeholder="비밀번호" required>
            <button type="submit">로그인 / 회원가입</button>
        </form>
        
        <p style="color: #8b4513; font-size: 12px; margin-top: 15px;">
            * 닉네임이 없으면 자동으로 새 계정이 생성됩니다
        </p>
        
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>'''

TREE_HTML = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ nickname }}님의 추석 미니홈피</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Malgun Gothic', sans-serif;
            background: linear-gradient(180deg, #2a1810 0%, #1a0f08 50%, #0f0604 100%);
            min-height: 100vh; color: #f4e8d0; overflow-x: hidden; position: relative;
        }
        body::before {
            content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20px 30px, #fff4e6, transparent),
                radial-gradient(2px 2px at 40px 70px, #ff6347, transparent),
                radial-gradient(1px 1px at 90px 40px, #ffa500, transparent);
            background-repeat: repeat; background-size: 250px 150px; opacity: 0.4; pointer-events: none; z-index: -1;
        }
        .pixel-moon {
            position: fixed; top: 50px; right: 50px; width: 80px; height: 80px; background: #fff8dc;
            border-radius: 50%; box-shadow: 0 0 0 2px #f0e68c, 0 0 0 4px #daa520, 0 0 30px #fff8dc; z-index: 1;
        }
        .mobile-container { max-width: 100%; margin: 0; background: rgba(0, 0, 0, 0.3); min-height: 100vh; }
        .header {
            background: linear-gradient(45deg, #8b4513, #cd853f); padding: 15px; color: #f4e8d0;
            position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.2em; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); }
        .logout-btn {
            padding: 8px 15px; background: rgba(255, 99, 71, 0.8); color: white; border: 2px solid #ff6347;
            border-radius: 15px; cursor: pointer; text-decoration: none; font-size: 12px;
        }
        .profile-section {
            background: linear-gradient(145deg, #d2691e, #cd853f); padding: 20px; text-align: center;
            border-bottom: 3px solid #8b4513;
        }
        .profile-img {
            width: 80px; height: 80px; background: linear-gradient(45deg, #fff8dc, #f0e68c);
            border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;
            font-size: 35px; border: 4px solid #daa520; box-shadow: 0 0 0 2px #8b4513, 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        .profile-name { font-size: 1.3em; font-weight: bold; color: #f4e8d0; margin-bottom: 10px; }
        .stats-row { display: flex; justify-content: space-around; margin-top: 15px; }
        .stat-item {
            text-align: center; background: rgba(244, 232, 208, 0.9); padding: 10px; border-radius: 10px;
            font-size: 12px; flex: 1; margin: 0 5px; color: #8b4513; border: 2px solid #cd853f;
        }
        .bgm-section {
            background: linear-gradient(45deg, #ff6347, #ff7f50); padding: 15px; text-align: center;
            border-bottom: 2px solid #ff4500;
        }
        .bgm-content {
            background: rgba(255, 255, 255, 0.9); padding: 10px; border-radius: 10px;
            font-size: 13px; color: #8b4513; border: 2px solid #cd853f;
        }
        .main-content { padding: 15px; }
        .chuseok-room {
            background: linear-gradient(145deg, #8b4513, #a0522d); border-radius: 15px; padding: 20px;
            margin-bottom: 20px; position: relative; border: 3px solid #cd853f; min-height: 300px;
        }
        .room-title { color: #f4e8d0; font-size: 16px; font-weight: bold; margin-bottom: 15px; text-align: center; }
        .tree-area { position: relative; text-align: center; height: 250px; }
        .tree { font-size: 3.5em; margin-bottom: 15px; }
        .ornament {
            position: absolute; font-size: 1.8em; cursor: pointer; transition: all 0.3s ease; z-index: 10;
        }
        .ornament:hover { transform: scale(1.4); filter: drop-shadow(0 0 10px #daa520); }
        .ornament .tooltip {
            position: absolute; background: linear-gradient(45deg, #8b4513, #cd853f); color: #f4e8d0;
            padding: 8px 10px; border-radius: 8px; font-size: 10px; top: -60px; left: 50%;
            transform: translateX(-50%); opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
            max-width: 150px; white-space: normal; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.5); z-index: 20;
        }
        .ornament:hover .tooltip { opacity: 1; }
        .guestbook {
            background: linear-gradient(145deg, #8b4513, #a0522d); border-radius: 15px; padding: 15px;
            border: 3px solid #cd853f;
        }
        .guestbook h3 { color: #f4e8d0; margin-bottom: 15px; font-size: 16px; text-align: center; }
        .message-form { background: rgba(244, 232, 208, 0.95); padding: 15px; border-radius: 10px; margin-bottom: 15px; }
        .form-group { margin-bottom: 12px; }
        .form-label { display: block; font-size: 12px; color: #8b4513; margin-bottom: 5px; font-weight: bold; }
        .message-form input, .message-form textarea, .message-form select {
            width: 100%; padding: 12px; border: 2px solid #cd853f; border-radius: 8px; font-size: 14px;
            background: #faf0e6; color: #8b4513;
        }
        .submit-btn {
            width: 100%; padding: 15px; background: linear-gradient(45deg, #daa520, #cd853f); color: white;
            border: none; border-radius: 25px; cursor: pointer; font-size: 16px; font-weight: bold;
        }
        .menu-tabs {
            display: flex; background: linear-gradient(45deg, #8b4513, #cd853f); position: sticky; bottom: 0; z-index: 100;
        }
        .menu-tab {
            flex: 1; padding: 12px 5px; text-align: center; font-size: 11px; color: #f4e8d0;
            border: none; background: transparent; cursor: pointer;
        }
        .menu-tab.active { color: #fff8dc; background: rgba(218, 165, 32, 0.3); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        @media (max-width: 480px) { .pixel-moon { width: 60px; height: 60px; top: 30px; right: 30px; } }
    </style>
</head>
<body>
    <div class="pixel-moon"></div>
    <div class="mobile-container">
        <div class="header">
            <div class="header-content">
                <h1>🌕 {{ nickname }}님의 미니홈피</h1>
                <a href="/logout" class="logout-btn">로그아웃</a>
            </div>
        </div>
        
        <div class="profile-section">
            <div class="profile-img">🌙</div>
            <div class="profile-name">{{ nickname }}</div>
            <div class="stats-row">
                <div class="stat-item">
                    <div>👥 방문자</div>
                    <div><strong>{{ messages|length * 3 + 47 }}</strong></div>
                </div>
                <div class="stat-item">
                    <div>💌 메시지</div>
                    <div><strong>{{ messages|length }}</strong></div>
                </div>
            </div>
        </div>
        
        <div class="bgm-section">
            <div class="bgm-content">
                <div>🎵 <strong>{{ user_bgm or '추석의 달빛 아래서' }}</strong></div>
                <div style="margin-top: 5px; font-size: 11px;">💿 재생중... ♪♫</div>
            </div>
        </div>
        
        <div class="main-content">
            <div id="home-tab" class="tab-content active">
                <div class="chuseok-room">
                    <div class="room-title">🌾 {{ nickname }}님의 추석 한옥 🌾</div>
                    <div class="tree-area">
                        <div class="tree">🌳</div>
                        {% for msg in messages %}
                        <div class="ornament" style="left: {{ msg.x }}%; top: {{ msg.y }}%;">
                            {{ msg.emoji }}
                            <div class="tooltip">
                                <strong>{{ msg.author }}</strong><br>
                                {{ msg.content }}<br>
                                <small>{{ msg.timestamp }}</small>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <div id="guestbook-tab" class="tab-content">
                <div class="guestbook">
                    <h3>📝 추석 방명록 ({{ messages|length }})</h3>
                    <div class="message-form">
                        <form method="POST" action="/add_message">
                            <div class="form-group">
                                <label class="form-label">👤 이름</label>
                                <input type="text" name="author" placeholder="이름을 입력하세요" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">💝 추석 인사말</label>
                                <textarea name="content" placeholder="따뜻한 추석 인사를 남겨주세요..." required></textarea>
                            </div>
                            <div class="form-group">
                                <label class="form-label">🎁 장식품 선택</label>
                                <select name="emoji" required>
                                    <option value="">장식품을 선택하세요</option>
                                    <option value="🌕">🌕 환한 보름달</option>
                                    <option value="🥮">🥮 달콤한 월병</option>
                                    <option value="🎋">🎋 소원 대나무</option>
                                    <option value="🏮">🏮 따뜻한 등불</option>
                                    <option value="🌰">🌰 고소한 밤</option>
                                    <option value="🍇">🍇 송이송이 포도</option>
                                    <option value="🍎">🍎 빨간 사과</option>
                                    <option value="🍐">🍐 달콤한 배</option>
                                    <option value="🌾">🌾 황금 곡식</option>
                                    <option value="🎊">🎊 축하 폭죽</option>
                                    <option value="💝">💝 마음의 선물</option>
                                    <option value="💖">💖 따뜻한 사랑</option>
                                    <option value="🍂">🍂 가을 단풍</option>
                                    <option value="🌸">🌸 벚꽃</option>
                                </select>
                            </div>
                            <button type="submit" class="submit-btn">💌 방명록에 남기기</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="menu-tabs">
            <button class="menu-tab active" onclick="showTab('home')">
                <div>🏠</div><div>홈</div>
            </button>
            <button class="menu-tab" onclick="showTab('guestbook')">
                <div>📝</div><div>방명록 작성</div>
            </button>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.menu-tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.closest('.menu-tab').classList.add('active');
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    if 'nickname' in session:
        return redirect(url_for('tree'))
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['POST'])
def login():
    nickname = request.form['nickname']
    password = request.form['password']
    
    if not nickname or not password:
        return render_template_string(LOGIN_HTML, 
                                    message="닉네임과 비밀번호를 모두 입력해주세요.", 
                                    message_type="error")
    
    # 기존 계정이 있는 경우 로그인 시도
    if nickname in users_db:
        if users_db[nickname] == password:
            session['nickname'] = nickname
            return redirect(url_for('tree'))
        else:
            return render_template_string(LOGIN_HTML, 
                                        message="비밀번호가 틀렸습니다.", 
                                        message_type="error")
    
    # 새 계정 자동 생성
    else:
        users_db[nickname] = password
        messages_db[nickname] = []
        settings_db[nickname] = {'bgm_title': '추석의 달빛 아래서'}
        save_data()
        
        session['nickname'] = nickname
        return redirect(url_for('tree'))

@app.route('/tree')
def tree():
    if 'nickname' not in session:
        return redirect(url_for('index'))
    
    nickname = session['nickname']
    messages = messages_db.get(nickname, [])
    user_settings = settings_db.get(nickname, {'bgm_title': '추석의 달빛 아래서'})
    
    return render_template_string(TREE_HTML, 
                                nickname=nickname, 
                                messages=messages,
                                user_bgm=user_settings.get('bgm_title', '추석의 달빛 아래서'))

@app.route('/add_message', methods=['POST'])
def add_message():
    if 'nickname' not in session:
        return redirect(url_for('index'))
    
    nickname = session['nickname']
    author = request.form['author']
    content = request.form['content']
    emoji = request.form['emoji']
    
    if nickname not in messages_db:
        messages_db[nickname] = []
    
    message = {
        'author': author,
        'content': content,
        'emoji': emoji,
        'timestamp': datetime.now().strftime('%m/%d %H:%M'),
        'x': round(20 + (60 * len(messages_db[nickname]) * 0.1) % 60, 1),
        'y': round(20 + (40 * len(messages_db[nickname]) * 0.15) % 40, 1)
    }
    
    messages_db[nickname].append(message)
    save_data()
    
    return redirect(url_for('tree'))

@app.route('/logout')
def logout():
    session.pop('nickname', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
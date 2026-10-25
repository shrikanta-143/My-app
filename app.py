from flask import Flask, request, redirect, session, send_from_directory, g
import os, sqlite3, time
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "pro_version_final"

# ==== PASSWORD YAHI HAI ====
ANIMATION_PASSWORD = "Shrikanta@1432"  # Protective Password
ADMIN_PASSWORD = "Teka@#2607"          # Admin Password
APP_NAME = "MY APP"
APP_LOGO = "🎉"
# ===========================

UPLOAD_FOLDER = "uploads"
DATABASE = "database.db"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        try: db.execute("ALTER TABLE users ADD COLUMN last_seen TEXT")
        except: pass
        db.execute('CREATE TABLE IF NOT EXISTS users (mobile TEXT PRIMARY KEY, full_name TEXT, gender TEXT, dob TEXT, email TEXT, password TEXT, forget_code TEXT, bio TEXT, last_seen TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, mobile TEXT, full_name TEXT, caption TEXT, filename TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS likes (post_id INTEGER, mobile TEXT, PRIMARY KEY(post_id,mobile))')
        db.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, full_name TEXT, comment TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, msg TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY AUTOINCREMENT, mobile TEXT, full_name TEXT, filename TEXT, time REAL)')
        db.commit()

init_db()

@app.teardown_appcontext
def close(e):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def update_online():
    if 'mobile' in session:
        db = get_db()
        db.execute("UPDATE users SET last_seen=? WHERE mobile=?", (datetime.now().strftime("%H:%M"), session['mobile']))
        db.commit()

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
body{font-family:'Poppins',Arial;margin:0;background:linear-gradient(135deg,#6aa8ff,#a36bff);min-height:100vh}
.card{max-width:460px;margin:14px auto;background:#fff;padding:18px;border-radius:20px;box-shadow:0 10px 30px #0002;text-align:center}
input,select{width:94%;padding:11px;margin:7px 0;border:1.5px solid #dbe2f0;border-radius:12px;background:#f7f9ff}
button{padding:10px 16px;border:none;border-radius:12px;font-weight:600;cursor:pointer}
.primary{background:linear-gradient(90deg,#2b6cff,#7a5CFF);color:#fff;width:100%;padding:12px}
.btn2{background:#eef3ff;color:#2b6cff;border:1px solid #d0ddff;margin:4px}
.story-bar{display:flex;gap:12px;overflow-x:auto;padding:10px 0}
.story{width:60px;text-align:center;flex-shrink:0}
.story img{width:60px;height:60px;border-radius:50%;border:3px solid #ff6a00;object-fit:cover}
.post-img{width:100%;border-radius:14px;max-height:380px;object-fit:cover}
.online-dot{width:10px;height:10px;background:#00ff00;border-radius:50%;display:inline-block}
</style>
"""

# ==== PROTECTIVE LOCK ====
@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        if request.form.get('pass')==ANIMATION_PASSWORD:
            session['unlocked']=True
            return redirect('/main')
        return STYLE + "<div class='card'><h3>❌ Wrong Protective Password</h3><a href='/'>Try Again</a></div>"
    if session.get('unlocked'):
        return redirect('/main')
    return STYLE + f"<div class='card'><div style='font-size:50px'>{APP_LOGO}</div><h1 style='color:#2b6cff'>{APP_NAME}</h1><p>Enter Protective Password</p><form method='POST'><input type='password' name='pass' placeholder='Protective Password' required><button class='primary'>Unlock</button></form></div>"

@app.route('/main')
def main_page():
    if not session.get('unlocked'): return redirect('/')
    return STYLE + f"<div class='card'><div style='font-size:50px'>{APP_LOGO}</div><h1 style='color:#2b6cff'>{APP_NAME}</h1><a href='/register'><button class='primary'>REGISTER</button></a><br><br><a href='/login'><button class='btn2' style='width:100%'>LOGIN</button></a><br><br><a href='/admin'><button class='btn2' style='width:100%'>ADMIN LOGIN</button></a></div>"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/register', methods=['GET','POST'])
def register():
    if not session.get('unlocked'): return redirect('/')
    if request.method=='POST':
        db=get_db()
        try:
            db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",(request.form['mobile'],request.form['full_name'],request.form['gender'],request.form['dob'],request.form['email'],request.form['password'],request.form['forget_code'],"Hello", "Offline"))
            db.commit()
            return redirect('/login')
        except:
            return "Mobile Already Exists"
    return STYLE + "<div class='card'><h2>Register</h2><form method='POST'><input name='full_name' placeholder='Full Name' required><select name='gender'><option>Male</option><option>Female</option><option>Others</option></select><input name='mobile' placeholder='Mobile' required><input type='date' name='dob' required><input name='email' placeholder='Email' required><input type='password' name='password' placeholder='Password' required><input name='forget_code' placeholder='Code' required><button class='primary'>Submit</button></form></div>"

@app.route('/login', methods=['GET','POST'])
def login():
    if not session.get('unlocked'): return redirect('/')
    if request.method=='POST':
        db=get_db()
        u=db.execute("SELECT * FROM users WHERE mobile=? AND password=?",(request.form['mobile'],request.form['password'])).fetchone()
        if u:
            session['mobile']=u[0]
            return redirect('/dashboard')
        return "Wrong password"
    return STYLE + "<div class='card'><h2>Login</h2><form method='POST'><input name='mobile' placeholder='Mobile' required><input type='password' name='password' placeholder='Password' required><button class='primary'>Login</button></form></div>"

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'mobile' not in session: return redirect('/login')
    update_online()
    db=get_db()
    u=db.execute("SELECT * FROM users WHERE mobile=?",(session['mobile'],)).fetchone()
    if request.method=='POST':
        f=request.files.get('pic')
        if f and f.filename:
            fn=secure_filename(session['mobile']+"_"+f.filename)
            f.save(os.path.join(UPLOAD_FOLDER,fn))
            db.execute("INSERT INTO posts (mobile,full_name,caption,filename) VALUES (?,?,?,?)",(session['mobile'],u[1],request.form.get('caption',''),fn))
            db.commit()
        sf=request.files.get('story_pic')
        if sf and sf.filename:
            fn=secure_filename("story_"+session['mobile']+"_"+sf.filename)
            sf.save(os.path.join(UPLOAD_FOLDER,fn))
            db.execute("INSERT INTO stories (mobile,full_name,filename,time) VALUES (?,?,?,?)",(session['mobile'],u[1],fn,time.time()))
            db.commit()
    stories=db.execute("SELECT * FROM stories WHERE time > ?", (time.time()-86400,)).fetchall()
    story_html="".join([f"<div class='story'><img src='/uploads/{s[3]}'><br><small>{s[2][:6]}</small></div>" for s in stories])
    return STYLE + f"<div class='card'><b>Welcome, {u[1]} <span class='online-dot'></span> {u[8]}</b><br><br><div class='story-bar'>{story_html if story_html else 'No Stories'}</div><br><form method='POST' enctype='multipart/form-data'><input type='file' name='pic'><input name='caption' placeholder='Caption'><button class='primary'>Post</button></form><br><form method='POST' enctype='multipart/form-data'><input type='file' name='story_pic'><button class='btn2' style='width:100%'>Add Story (24h)</button></form><hr><a href='/my_posts'><button class='btn2'>My Posts</button></a><a href='/feed'><button class='btn2'>Feed</button></a><a href='/friends'><button class='btn2'>Friends</button></a><br><br><a href='/logout'><button class='btn2'>Logout</button></a></div>"

@app.route('/feed')
def feed():
    if 'mobile' not in session: return redirect('/login')
    db=get_db()
    posts=db.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    html=""
    for p in posts:
        lc=db.execute("SELECT COUNT(*) FROM likes WHERE post_id=?",(p[0],)).fetchone()[0]
        liked=db.execute("SELECT * FROM likes WHERE post_id=? AND mobile=?",(p[0],session['mobile'])).fetchone()
        heart="❤️" if liked else "🤍"
        comms=db.execute("SELECT * FROM comments WHERE post_id=?",(p[0],)).fetchall()
        chtml="".join([f"<div style='text-align:left;font-size:12px'><b>{c[2]}:</b> {c[3]}</div>" for c in comms])
        html+=f"<div class='card' style='text-align:left'><b>{p[2]}</b><br><img src='/uploads/{p[4]}' class='post-img'><p>{p[3]}</p><a href='/like/{p[0]}'><button class='btn2'>{heart} {lc}</button></a> <a href='/comment/{p[0]}'><button class='btn2'>💬 Comment</button></a>{chtml}</div>"
    return STYLE + f"<div class='card'><h3>{APP_NAME} Feed</h3><a href='/dashboard'>Back</a></div>{html}"

@app.route('/like/<int:pid>')
def like(pid):
    db=get_db()
    ex=db.execute("SELECT * FROM likes WHERE post_id=? AND mobile=?",(pid,session['mobile'])).fetchone()
    if ex: db.execute("DELETE FROM likes WHERE post_id=? AND mobile=?",(pid,session['mobile']))
    else: db.execute("INSERT INTO likes VALUES (?,?)",(pid,session['mobile']))
    db.commit()
    return redirect('/feed')

@app.route('/comment/<int:pid>', methods=['GET','POST'])
def comment(pid):
    db=get_db()
    if request.method=='POST':
        me=db.execute("SELECT * FROM users WHERE mobile=?",(session['mobile'],)).fetchone()
        db.execute("INSERT INTO comments (post_id,full_name,comment) VALUES (?,?,?)",(pid,me[1],request.form['comment']))
        db.commit()
        return redirect('/feed')
    return STYLE + f"<div class='card'><form method='POST'><input name='comment' placeholder='Comment' required><button class='primary'>Send</button></form></div>"

@app.route('/my_posts')
def my_posts():
    if 'mobile' not in session: return redirect('/login')
    db=get_db()
    posts=db.execute("SELECT * FROM posts WHERE mobile=? ORDER BY id DESC",(session['mobile'],)).fetchall()
    items="".join([f"<div><img src='/uploads/{p[4]}' class='post-img' style='height:110px'><br><a href='/delete/{p[0]}'>Delete</a></div>" for p in posts])
    return STYLE + f"<div class='card'><h3>My Posts</h3><div style='display:grid;grid-template-columns:repeat(3,1fr);gap:8px'>{items}</div><br><a href='/dashboard'>Back</a></div>"

@app.route('/delete/<int:pid>')
def delete_post(pid):
    db=get_db()
    db.execute("DELETE FROM posts WHERE id=?",(pid,))
    db.commit()
    return redirect('/my_posts')

@app.route('/friends')
def friends():
    if 'mobile' not in session: return redirect('/login')
    update_online()
    db=get_db()
    users=db.execute("SELECT * FROM users WHERE mobile!=?",(session['mobile'],)).fetchall()
    cards="".join([f"<div class='card' style='padding:10px;text-align:left'><b>{u[1]}</b> <small>{u[8]}</small> <span class='online-dot'></span><a href='/chat/{u[0]}'><button class='btn2' style='float:right'>Chat</button></a></div>" for u in users])
    return STYLE + f"<div class='card'><h3>Friends - Online</h3></div>{cards}<div class='card'><a href='/dashboard'>Back</a></div>"

@app.route('/chat/<mobile>', methods=['GET','POST'])
def chat(mobile):
    if 'mobile' not in session: return redirect('/login')
    db=get_db()
    if request.method=='POST':
        db.execute("INSERT INTO chats VALUES (NULL,?,?,?)",(session['mobile'],mobile,request.form['msg']))
        db.commit()
    msgs=db.execute("SELECT * FROM chats WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id",(session['mobile'],mobile,mobile,session['mobile'])).fetchall()
    bubbles="".join([f"<div style='text-align:{'right' if m[1]==session['mobile'] else 'left'};margin:6px'><span style='padding:8px 12px;border-radius:12px;background:{'#2b6cff' if m[1]==session['mobile'] else '#eef3ff'};color:{'#fff' if m[1]==session['mobile'] else '#000'}'>{m[3]}</span></div>" for m in msgs])
    return STYLE + f"<div class='card'><div style='min-height:300px'>{bubbles}</div><form method='POST'><input name='msg' required><button class='primary'>Send</button></form><br><a href='/friends'>Back</a></div>"

@app.route('/admin', methods=['GET','POST'])
def admin():
    if not session.get('unlocked'): return redirect('/')
    if request.method=='POST':
        if request.form['pass']==ADMIN_PASSWORD:
            session['is_admin']=True
            return redirect('/admin')
        return STYLE + "<div class='card'><h3>❌ Wrong Admin Password</h3><a href='/admin'>Back</a></div>"
    if not session.get('is_admin'):
        return STYLE + "<div class='card'><h2>Admin Login</h2><p>Enter Admin Password</p><form method='POST'><input type='password' name='pass' placeholder='Teka@#2607' required><button class='primary'>Login</button></form></div>"
    db=get_db()
    users=db.execute("SELECT * FROM users").fetchall()
    posts=db.execute("SELECT * FROM posts").fetchall()
    uhtml="".join([f"<div style='text-align:left;border-bottom:1px solid #eee;padding:6px'>{u[1]} - {u[0]} <a href='/admin_del_user/{u[0]}' style='float:right;color:red'>Delete</a></div>" for u in users])
    phtml="".join([f"<div style='text-align:left;border-bottom:1px solid #eee;padding:6px'>{p[2]} - {p[3][:20]} <a href='/admin_del_post/{p[0]}' style='float:right;color:red'>Delete</a></div>" for p in posts])
    return STYLE + f"<div class='card'><h2>ADMIN PANEL</h2><p>Protective: {ANIMATION_PASSWORD} | Admin: {ADMIN_PASSWORD}</p><h3>Users ({len(users)})</h3>{uhtml}<h3>Posts ({len(posts)})</h3>{phtml}<br><a href='/main'><button class='btn2'>Back</button></a> <a href='/admin_logout'><button class='btn2'>Admin Logout</button></a></div>"

@app.route('/admin_del_user/<mobile>')
def admin_del_user(mobile):
    if not session.get('is_admin'): return redirect('/admin')
    db=get_db()
    db.execute("DELETE FROM users WHERE mobile=?",(mobile,))
    db.commit()
    return redirect('/admin')

@app.route('/admin_del_post/<int:pid>')
def admin_del_post(pid):
    if not session.get('is_admin'): return redirect('/admin')
    db=get_db()
    db.execute("DELETE FROM posts WHERE id=?",(pid,))
    db.commit()
    return redirect('/admin')

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin',None)
    return redirect('/main')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

from flask import Flask, request, redirect, session, send_from_directory, g
import os, sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "clean_final_2026"
ANIMATION_PASSWORD = "Shrikanta@1432"
ADMIN_PASSWORD = "Admin123"
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
        db.execute('CREATE TABLE IF NOT EXISTS users (mobile TEXT PRIMARY KEY, full_name TEXT, gender TEXT, dob TEXT, email TEXT, password TEXT, forget_code TEXT, bio TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, mobile TEXT, full_name TEXT, caption TEXT, filename TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS likes (post_id INTEGER, mobile TEXT, PRIMARY KEY(post_id,mobile))')
        db.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, full_name TEXT, comment TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, msg TEXT)')
        db.commit()

@app.teardown_appcontext
def close(e):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
body{font-family:'Poppins',Arial;margin:0;padding:0;background:linear-gradient(135deg,#6aa8ff,#a36bff);min-height:100vh}
.card{max-width:460px;margin:16px auto;background:#fff;padding:20px;border-radius:20px;box-shadow:0 10px 30px #0002;text-align:center}
input,select{width:94%;padding:11px;margin:7px 0;border:1.5px solid #dbe2f0;border-radius:12px;background:#f7f9ff;text-align:left}
button{padding:10px 16px;border:none;border-radius:12px;font-weight:600;cursor:pointer}
.primary{background:linear-gradient(90deg,#2b6cff,#7a5CFF);color:#fff;width:100%;padding:12px;font-size:15px}
.btn2{background:#eef3ff;color:#2b6cff;border:1px solid #d0ddff;margin:4px}
.welcome-anim-main{font-size:55px;animation:bounce 1.2s infinite;cursor:pointer}
.welcome-anim-big{font-size:80px;animation:bounce 1s infinite, glow 1.5s infinite alternate;cursor:pointer}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes glow{0%{text-shadow:0 0 10px #2b6cff}100%{text-shadow:0 0 30px #a36bff}}
.post-img{width:100%;border-radius:14px;max-height:380px;object-fit:cover}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
table{width:100%;border-collapse:collapse} td,th{border:1px solid #ddd;padding:5px;font-size:12px}
</style>
"""

@app.route('/')
def home():
    return STYLE + """
    <div class='card'>
    <div class='welcome-anim-main'>🎉</div>
    <h1 style='color:#2b6cff; margin:5px 0'>MY APP</h1>
    <p style='margin:0; color:#666'>Welcome to our group</p><br>
    <a href='/register'><button class='primary'>REGISTER</button></a><br><br>
    <a href='/login'><button class='btn2' style='width:100%'>LOGIN</button></a><br><br>
    <a href='/welcome'><button class='btn2' style='width:100%; background:linear-gradient(90deg,#ff9a00,#ff6a00); color:#fff; border:none'>Welcome to our group</button></a>
    </div>
    """

@app.route('/welcome', methods=['GET','POST'])
def welcome():
    anim_ok = session.get('anim_ok', False)
    error = ""
    if request.method == 'POST':
        if 'anim_pass' in request.form:
            if request.form['anim_pass'] == ANIMATION_PASSWORD:
                session['anim_ok'] = True
                anim_ok = True
            else:
                error = "Wrong Password"
        if 'admin_pass' in request.form:
            if request.form['admin_pass'] == ADMIN_PASSWORD:
                session['is_admin'] = True
                return redirect('/admin')
            else:
                error = "Wrong Password"
    return STYLE + f"""
    <div class='card' style='min-height:450px; display:flex; flex-direction:column; justify-content:center; align-items:center'>
    <div class='welcome-anim-big' onclick="document.getElementById('animBox').style.display='block'">🎉</div>
    <h1 style='color:#2b6cff;'>Welcome</h1>
    <h3 style='margin:0;'>to our group</h3>
    <p style='color:red; font-size:13px'>{error}</p>
    <div id='animBox' style='display:{"block" if not anim_ok else "none"}; width:100%; margin-top:15px'>
        <form method='POST'><input type='password' name='anim_pass' placeholder='' required><button class='primary'>Unlock</button></form>
    </div>
    <div style='display:{"block" if anim_ok else "none"}; width:100%; margin-top:15px; background:#f7f9ff; padding:15px; border-radius:12px'>
        <button onclick="document.getElementById('adminPassBox').style.display='block'" class='btn2' style='background:#2b6cff; color:#fff; width:100%'>ADMIN</button>
        <div id='adminPassBox' style='display:none; margin-top:10px'>
            <form method='POST'><input type='password' name='admin_pass' placeholder='' required><button class='primary'>Open Admin Panel</button></form>
        </div>
    </div>
    <br><a href='/'><button class='btn2'>Back</button></a></div>
    """

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        db=get_db()
        if db.execute("SELECT * FROM users WHERE mobile=?",(request.form['mobile'],)).fetchone():
            return "Already exists <a href='/login'>Login</a>"
        db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?)",(request.form['mobile'],request.form['full_name'],request.form['gender'],request.form['dob'],request.form['email'],request.form['password'],request.form['forget_code'],"Hello World"))
        db.commit()
        return redirect('/login')
    return STYLE + "<div class='card'><h2>Register</h2><form method='POST'><input name='full_name' placeholder='Full Name' required><select name='gender'><option>Male</option><option>Female</option><option>Others</option></select><input name='mobile' placeholder='Mobile' required><input type='date' name='dob' required><input name='email' placeholder='Email' required><input type='password' name='password' placeholder='Password' required><input name='forget_code' maxlength='6' placeholder='6-digit Code' required><button class='primary' type='submit'>Submit</button></form><br><a href='/'><button class='btn2'>Back</button></a></div>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        db=get_db()
        u=db.execute("SELECT * FROM users WHERE mobile=? AND password=?",(request.form['mobile'],request.form['password'])).fetchone()
        if u:
            session['mobile']=u[0]
            return redirect('/dashboard')
        return "Wrong password"
    return STYLE + "<div class='card'><h2>Login</h2><form method='POST'><input name='mobile' placeholder='Mobile No.' required><input type='password' name='password' placeholder='Password' required><button class='primary' type='submit'>Login</button></form><br><a href='/forgot'><button class='btn2'>Forget Password</button></a> <a href='/'><button class='btn2'>Back</button></a></div>"

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        db=get_db()
        if 'new_pass' in request.form:
            if request.form['new_pass']!=request.form['confirm']:
                return "Mismatch"
            db.execute("UPDATE users SET password=? WHERE mobile=?",(request.form['new_pass'],request.form['mobile']))
            db.commit()
            return redirect('/login')
        u=db.execute("SELECT * FROM users WHERE full_name=? AND forget_code=?",(request.form['full_name'],request.form['code'])).fetchone()
        if not u:
            return "Wrong"
        return STYLE + f"<div class='card'><form method='POST'><input type='hidden' name='mobile' value='{u[0]}'><input type='password' name='new_pass' placeholder='New Password' required><input type='password' name='confirm' placeholder='Confirm Password' required><button class='primary'>Save</button></form></div>"
    return STYLE + "<div class='card'><h3>Forget Password</h3><form method='POST'><input name='full_name' placeholder='Full Name' required><input name='code' placeholder='Code' required><button class='primary'>Verify</button></form></div>"

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    u=db.execute("SELECT * FROM users WHERE mobile=?",(session['mobile'],)).fetchone()
    if request.method=='POST':
        if request.form.get('bio'):
            db.execute("UPDATE users SET bio=? WHERE mobile=?",(request.form['bio'],session['mobile']))
            db.commit()
        f=request.files.get('pic')
        if f and f.filename:
            fn=secure_filename(session['mobile']+"_"+f.filename)
            f.save(os.path.join(UPLOAD_FOLDER,fn))
            db.execute("INSERT INTO posts (mobile,full_name,caption,filename) VALUES (?,?,?,?)",(session['mobile'],u[1],request.form.get('caption',''),fn))
            db.commit()
    return STYLE + f"<div class='card' style='text-align:left'><b>Welcome, {u[1]}</b> <a href='/edit_bio'><button class='btn2'>Edit</button></a><br><br>Bio: {u[7]}<br><br><form method='POST' enctype='multipart/form-data'><input type='file' name='pic' required><input name='caption' placeholder='Caption'><button class='primary'>Post</button></form><hr><div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'><a href='/my_posts'><button class='btn2' style='width:100%'>My Posts</button></a><a href='/friends'><button class='btn2' style='width:100%'>Friend Posts</button></a><a href='/chat_list'><button class='btn2' style='width:100%'>Chat</button></a><a href='/feed'><button class='btn2' style='width:100%'>Live Feed</button></a></div><br><a href='/logout'><button class='btn2' style='width:100%'>Logout</button></a></div>"

@app.route('/edit_bio', methods=['GET','POST'])
def edit_bio():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    if request.method=='POST':
        db.execute("UPDATE users SET bio=? WHERE mobile=?",(request.form['bio'],session['mobile']))
        db.commit()
        return redirect('/dashboard')
    u=db.execute("SELECT * FROM users WHERE mobile=?",(session['mobile'],)).fetchone()
    return STYLE + f"<div class='card'><form method='POST'><input name='bio' value='{u[7]}'><button class='primary'>Save</button></form></div>"

@app.route('/my_posts')
def my_posts():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    posts=db.execute("SELECT * FROM posts WHERE mobile=? ORDER BY id DESC",(session['mobile'],)).fetchall()
    items="".join([f"<div style='position:relative' oncontextmenu=\"document.getElementById('d{p[0]}').style.display='block';return false;\" ondblclick=\"document.getElementById('d{p[0]}').style.display='block'\"><img src='/uploads/{p[4]}' class='post-img' style='height:110px'><div id='d{p[0]}' style='display:none;position:absolute;top:0;left:0;right:0;bottom:0;background:#ffffffee;display:flex;align-items:center;justify-content:center;gap:5px'><a href='/delete/{p[0]}'><button style='background:#ff3b30;color:#fff'>Delete</button></a> <button onclick=\"this.parentElement.style.display='none'\">Cancel</button></div></div>" for p in posts])
    return STYLE + f"<div class='card'><h3>My Posts</h3><div class='grid'>{items}</div><br><a href='/dashboard'><button class='btn2'>Back</button></a></div>"

@app.route('/delete/<int:pid>')
def delete_post(pid):
    db=get_db()
    db.execute("DELETE FROM posts WHERE id=?",(pid,))
    db.commit()
    return redirect('/my_posts')

@app.route('/feed')
def feed():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    posts=db.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    html=""
    for p in posts:
        lc=db.execute("SELECT COUNT(*) FROM likes WHERE post_id=?",(p[0],)).fetchone()[0]
        liked=db.execute("SELECT * FROM likes WHERE post_id=? AND mobile=?",(p[0],session['mobile'])).fetchone()
        heart="❤️" if liked else "🤍"
        comms=db.execute("SELECT * FROM comments WHERE post_id=?",(p[0],)).fetchall()
        chtml="".join([f"<div style='font-size:12px; text-align:left;'><b>{c[2]}:</b> {c[3]}</div>" for c in comms])
        html+=f"<div class='card' style='text-align:left'><b>{p[2]}</b><br><img src='/uploads/{p[4]}' class='post-img'><p>{p[3]}</p><a href='/like/{p[0]}'><button class='btn2'>{heart} {lc}</button></a> <a href='/comment/{p[0]}'><button class='btn2'>Comment</button></a> <a href='/share/{p[0]}'><button class='btn2'>Share</button></a>{chtml}</div>"
    return STYLE + f"<div class='card'><h3>Live Feed</h3><a href='/dashboard'>Back</a></div>{html}"

@app.route('/like/<int:pid>')
def like(pid):
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    ex=db.execute("SELECT * FROM likes WHERE post_id=? AND mobile=?",(pid,session['mobile'])).fetchone()
    if ex:
        db.execute("DELETE FROM likes WHERE post_id=? AND mobile=?",(pid,session['mobile']))
    else:
        db.execute("INSERT INTO likes VALUES (?,?)",(pid,session['mobile']))
    db.commit()
    return redirect('/feed')

@app.route('/comment/<int:pid>', methods=['GET','POST'])
def comment(pid):
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    if request.method=='POST':
        me=db.execute("SELECT * FROM users WHERE mobile=?",(session['mobile'],)).fetchone()
        db.execute("INSERT INTO comments (post_id,full_name,comment) VALUES (?,?,?)",(pid,me[1],request.form['comment']))
        db.commit()
        return redirect('/feed')
    return STYLE + f"<div class='card'><h3>Comment</h3><form method='POST'><input name='comment' placeholder=''><button class='primary'>Send</button></form></div>"

@app.route('/share/<int:pid>')
def share(pid):
    db=get_db()
    users=db.execute("SELECT * FROM users WHERE mobile!=?",(session['mobile'],)).fetchall()
    html="".join([f"<div style='text-align:left; border-bottom:1px solid #eee; padding:8px;'><b>{u[1]}</b> <button class='btn2' style='float:right'>Share</button></div>" for u in users])
    return STYLE + f"<div class='card'><h3>Share</h3>{html}<br><a href='/feed'>Back</a></div>"

@app.route('/friends')
def friends():
    if 'mobile' not in session:
        return redirect('/login')
    q=request.args.get('q','')
    db=get_db()
    if q:
        users=db.execute("SELECT * FROM users WHERE full_name LIKE ? OR mobile LIKE ?",(f"%{q}%",f"%{q}%")).fetchall()
    else:
        users=db.execute("SELECT * FROM users WHERE mobile!=?",(session['mobile'],)).fetchall()
    cards="".join([f"<div class='card' style='padding:10px; text-align:left;'><b>{u[1]}</b><div style='float:right'><a href='/friend_posts/{u[0]}'><button class='btn2'>Posts</button></a> <a href='/chat/{u[0]}'><button class='btn2'>Chat</button></a></div></div>" for u in users])
    return STYLE + f"<div class='card'><h3>Friend Posts</h3><form><input name='q' value='{q}' placeholder=''><button class='primary'>Search</button></form></div>{cards}<div class='card'><a href='/dashboard'>Back</a></div>"

@app.route('/friend_posts/<mobile>')
def friend_posts(mobile):
    db=get_db()
    posts=db.execute("SELECT * FROM posts WHERE mobile=?",(mobile,)).fetchall()
    html="".join([f"<div class='card'><img src='/uploads/{p[4]}' class='post-img'><p>{p[3]}</p></div>" for p in posts])
    return STYLE + f"<div class='card'><a href='/friends'>Back</a></div>{html}"

@app.route('/chat_list')
def chat_list():
    if 'mobile' not in session:
        return redirect('/login')
    q=request.args.get('q','')
    db=get_db()
    if q:
        users=db.execute("SELECT * FROM users WHERE full_name LIKE ? OR mobile LIKE ?",(f"%{q}%",f"%{q}%")).fetchall()
    else:
        users=db.execute("SELECT * FROM users WHERE mobile!=?",(session['mobile'],)).fetchall()
    cards="".join([f"<div class='card' style='padding:10px; text-align:left;'><b>{u[1]}</b><a href='/chat/{u[0]}'><button class='btn2' style='float:right'>Chat</button></a></div>" for u in users])
    return STYLE + f"<div class='card'><h3>Chat</h3><form><input name='q' value='{q}' placeholder=''><button class='primary'>Search</button></form><a href='/dashboard'><button class='btn2'>Back</button></a></div>{cards}"

@app.route('/chat/<mobile>', methods=['GET','POST'])
def chat(mobile):
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    r=db.execute("SELECT * FROM users WHERE mobile=?",(mobile,)).fetchone()
    rname=r[1] if r else "User"
    if request.method=='POST':
        db.execute("INSERT INTO chats VALUES (NULL,?,?,?)",(session['mobile'],mobile,request.form['msg']))
        db.commit()
    msgs=db.execute("SELECT * FROM chats WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id",(session['mobile'],mobile,mobile,session['mobile'])).fetchall()
    bubbles="".join([f"<div style='text-align:{'right' if m[1]==session['mobile'] else 'left'};margin:6px'><span style='display:inline-block;padding:10px 14px;border-radius:18px;background:{'#2b6cff' if m[1]==session['mobile'] else '#eef3ff'};color:{'#fff' if m[1]==session['mobile'] else '#000'}'>{m[3]}</span></div>" for m in msgs])
    return STYLE + f"<div class='card'><div style='display:flex;gap:10px'><a href='/chat_list'>⬅️</a><h3>{rname}</h3></div><div style='background:#f7f9ff;border-radius:16px;padding:10px;min-height:300px;max-height:400px;overflow-y:auto'>{bubbles}</div><form method='POST' style='display:flex;gap:6px;margin-top:10px'><input name='msg' placeholder='' required style='flex:1'><button class='primary' style='width:70px'>Send</button></form></div>"

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect('/welcome')
    db=get_db()
    users=db.execute("SELECT * FROM users").fetchall()
    rows="".join([f"<tr><td>{u[1]}</td><td>{u[0]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[4]}</td><td>{u[5]}</td><td>{u[6]}</td></tr>" for u in users])
    return STYLE + f"<div class='card' style='max-width:95%'><h3>Admin Panel</h3><table><tr><th>Name</th><th>mobile</th><th>Gender</th><th>DOB</th><th>Email</th><th>pass</th><th>code</th></tr>{rows}</table><br><a href='/admin_posts'><button class='btn2'>All Post</button></a> <a href='/admin_chats'><button class='btn2'>Chat</button></a> <a href='/delete_accounts'><button class='btn2'>Delete Account</button></a> <a href='/admin_logout'><button class='btn2'>Logout</button></a></div>"

@app.route('/admin_posts')
def admin_posts():
    if not session.get('is_admin'):
        return redirect('/welcome')
    db=get_db()
    posts=db.execute("SELECT * FROM posts").fetchall()
    html="".join([f"<div style='text-align:left;'>{p[2]} - {p[3]} <img src='/uploads/{p[4]}' width='40'></div>" for p in posts])
    return STYLE + f"<div class='card'><h3>All Posts</h3>{html}<br><a href='/admin'>Back</a></div>"

@app.route('/admin_chats')
def admin_chats():
    if not session.get('is_admin'):
        return redirect('/welcome')
    db=get_db()
    chats=db.execute("SELECT * FROM chats").fetchall()
    html="".join([f"<div style='text-align:left;'>{c[1]} -> {c[2]} : {c[3]}</div>" for c in chats])
    return STYLE + f"<div class='card'><h3>All Chats</h3>{html}<br><a href='/admin'>Back</a></div>"

@app.route('/delete_accounts')
def delete_accounts():
    if not session.get('is_admin'):
        return redirect('/welcome')
    db=get_db()
    users=db.execute("SELECT * FROM users").fetchall()
    rows="".join([f"<tr><td>{u[1]}</td><td>{u[0]}</td><td><a href='/admin_delete_user/{u[0]}'><button style='background:#ff3b30;color:#fff'>Delete</button></a></td></tr>" for u in users])
    return STYLE + f"<div class='card'>

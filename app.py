from flask import Flask, request, redirect, session, send_from_directory, g
import os, sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "clean_final_2026"
ANIMATION_PASSWORD = "Shrikanta@1432"
ADMIN_PASSWORD = "Teka@#2607"
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

# Database banane ke liye ye important hai
init_db()

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
.post-img{width:100%;border-radius:14px;max-height:380px;object-fit:cover}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
</style>
"""

@app.route('/')
def home():
    return STYLE + "<div class='card'><h1 style='color:#2b6cff'>MY APP</h1><a href='/register'><button class='primary'>REGISTER</button></a><br><br><a href='/login'><button class='btn2' style='width:100%'>LOGIN</button></a><br><br><a href='/welcome'><button class='btn2' style='width:100%'>Welcome to our group</button></a></div>"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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
    return STYLE + f"<div class='card'><h1>Welcome</h1><p style='color:red'>{error}</p><form method='POST'><input type='password' name='anim_pass' placeholder='Animation Password' required><button class='primary'>Unlock</button></form><div style='display:{'block' if anim_ok else 'none'}'><br><form method='POST'><input type='password' name='admin_pass' placeholder='Admin Password' required><button class='primary'>Open Admin</button></form></div><br><a href='/'>Back</a></div>"

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        db=get_db()
        if db.execute("SELECT * FROM users WHERE mobile=?",(request.form['mobile'],)).fetchone():
            return "Already exists <a href='/login'>Login</a>"
        db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?)",(request.form['mobile'],request.form['full_name'],request.form['gender'],request.form['dob'],request.form['email'],request.form['password'],request.form['forget_code'],"Hello World"))
        db.commit()
        return redirect('/login')
    return STYLE + "<div class='card'><h2>Register</h2><form method='POST'><input name='full_name' placeholder='Full Name' required><select name='gender'><option>Male</option><option>Female</option><option>Others</option></select><input name='mobile' placeholder='Mobile' required><input type='date' name='dob' required><input name='email' placeholder='Email' required><input type='password' name='password' placeholder='Password' required><input name='forget_code' placeholder='6-digit Code' required><button class='primary'>Submit</button></form></div>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        db=get_db()
        u=db.execute("SELECT * FROM users WHERE mobile=? AND password=?",(request.form['mobile'],request.form['password'])).fetchone()
        if u:
            session['mobile']=u[0]
            return redirect('/dashboard')
        return "Wrong password <a href='/login'>Back</a>"
    return STYLE + "<div class='card'><h2>Login</h2><form method='POST'><input name='mobile' placeholder='Mobile' required><input type='password' name='password' placeholder='Password' required><button class='primary'>Login</button></form><br><a href='/forgot'>Forget Password</a></div>"

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        db=get_db()
        if 'new_pass' in request.form:
            db.execute("UPDATE users SET password=? WHERE mobile=?",(request.form['new_pass'],request.form['mobile']))
            db.commit()
            return redirect('/login')
        u=db.execute("SELECT * FROM users WHERE full_name=? AND forget_code=?",(request.form['full_name'],request.form['code'])).fetchone()
        if not u:
            return "Wrong Code"
        return STYLE + f"<div class='card'><form method='POST'><input type='hidden' name='mobile' value='{u[0]}'><input type='password' name='new_pass' placeholder='New Password' required><button class='primary'>Save</button></form></div>"
    return STYLE + "<div class='card'><h3>Forget Password</h3><form method='POST'><input name='full_name' placeholder='Full Name' required><input name='code' placeholder='Code' required><button class='primary'>Verify</button></form></div>"

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    u=db.execute("SELECT * FROM users WHERE mobile=?",(session['mobile'],)).fetchone()
    if request.method=='POST':
        f=request.files.get('pic')
        if f and f.filename:
            fn=secure_filename(session['mobile']+"_"+f.filename)
            f.save(os.path.join(UPLOAD_FOLDER,fn))
            db.execute("INSERT INTO posts (mobile,full_name,caption,filename) VALUES (?,?,?,?)",(session['mobile'],u[1],request.form.get('caption',''),fn))
            db.commit()
    return STYLE + f"<div class='card'><b>Welcome, {u[1]}</b><br><br><form method='POST' enctype='multipart/form-data'><input type='file' name='pic' required><input name='caption' placeholder='Caption'><button class='primary'>Post</button></form><br><a href='/my_posts'><button class='btn2'>My Posts</button></a><a href='/feed'><button class='btn2'>Live Feed</button></a><a href='/friends'><button class='btn2'>Friends</button></a><a href='/chat_list'><button class='btn2'>Chat</button></a><br><br><a href='/logout'><button class='btn2'>Logout</button></a></div>"

@app.route('/feed')
def feed():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    posts=db.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    html=""
    for p in posts:
        html+=f"<div class='card'><b>{p[2]}</b><br><img src='/uploads/{p[4]}' class='post-img'><p>{p[3]}</p></div>"
    return STYLE + f"<div class='card'><h3>Live Feed</h3><a href='/dashboard'>Back</a></div>{html}"

@app.route('/my_posts')
def my_posts():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    posts=db.execute("SELECT * FROM posts WHERE mobile=? ORDER BY id DESC",(session['mobile'],)).fetchall()
    items="".join([f"<div><img src='/uploads/{p[4]}' class='post-img' style='height:110px'><br><a href='/delete/{p[0]}'>Delete</a></div>" for p in posts])
    return STYLE + f"<div class='card'><h3>My Posts</h3><div class='grid'>{items}</div><br><a href='/dashboard'>Back</a></div>"

@app.route('/delete/<int:pid>')
def delete_post(pid):
    db=get_db()
    db.execute("DELETE FROM posts WHERE id=?",(pid,))
    db.commit()
    return redirect('/my_posts')

@app.route('/friends')
def friends():
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    users=db.execute("SELECT * FROM users WHERE mobile!=?",(session['mobile'],)).fetchall()
    cards="".join([f"<div class='card'><b>{u[1]}</b> <a href='/chat/{u[0]}'><button class='btn2'>Chat</button></a></div>" for u in users])
    return STYLE + f"<div class='card'><h3>Friends</h3><a href='/dashboard'>Back</a></div>{cards}"

@app.route('/chat_list')
def chat_list():
    return redirect('/friends')

@app.route('/chat/<mobile>', methods=['GET','POST'])
def chat(mobile):
    if 'mobile' not in session:
        return redirect('/login')
    db=get_db()
    if request.method=='POST':
        db.execute("INSERT INTO chats VALUES (NULL,?,?,?)",(session['mobile'],mobile,request.form['msg']))
        db.commit()
    msgs=db.execute("SELECT * FROM chats WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id",(session['mobile'],mobile,mobile,session['mobile'])).fetchall()
    bubbles="".join([f"<div style='text-align:{'right' if m[1]==session['mobile'] else 'left'};margin:6px'><span style='padding:8px 12px;border-radius:12px;background:#eef3ff'>{m[3]}</span></div>" for m in msgs])
    return STYLE + f"<div class='card'><div style='min-height:300px'>{bubbles}</div><form method='POST'><input name='msg' required><button class='primary'>Send</button></form><br><a href='/friends'>Back</a></div>"

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect('/welcome')
    db=get_db()
    users=db.execute("SELECT * FROM users").fetchall()
    rows="".join([f"<tr><td>{u[1]}</td><td>{u[0]}</td><td>{u[5]}</td><td><a href='/admin_delete_user/{u[0]}'>Delete</a></td></tr>" for u in users])
    return STYLE + f"<div class='card' style='max-width:95%'><h3>Admin</h3><table border=1><tr><th>Name</th><th>Mobile</th><th>Pass</th><th>Action</th></tr>{rows}</table><br><a href='/admin_logout'>Logout</a></div>"

@app.route('/admin_delete_user/<mobile>')
def admin_delete_user(mobile):
    db=get_db()
    db.execute("DELETE FROM users WHERE mobile=?",(mobile,))
    db.commit()
    return redirect('/admin')

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

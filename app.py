from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, random, hashlib
from datetime import datetime

:
app = Flask(__name__, template_folder='.')
app.secret_key = "CHANGE_THIS_SECRET_KEY"
DB="jnv.db"

QUESTIONS=[
("Mental Ability","ગુજરાતી","સમાનતા શોધો: 2 : 4 :: 3 : ?","6","4","5","9","6","Easy"),
("Mental Ability","ગુજરાતી","અલગ વસ્તુ પસંદ કરો: કેરી, સફરજન, ગાજર, કેળું","ગાજર","કેરી","સફરજન","કેળું","ગાજર","Easy"),
("Arithmetic","ગુજરાતી","200 ના 15% કેટલા થાય?","30","20","30","40","50","Easy"),
("Arithmetic","ગુજરાતી","5 + 2 × 3 = ?","11","21","11","10","15","Easy"),
("Language","ગુજરાતી","'ખુશ' નો સમાનાર્થી શબ્દ કયો છે?","આનંદિત","દુઃખી","ગુસ્સે","રડવું","આનંદિત","Easy"),
("Mental Ability","English","Find the next number: 2, 4, 8, 16, ?","32","20","24","32","36","Easy"),
("Arithmetic","English","What is 25% of 80?","20","10","15","20","25","Easy"),
("Language","English","Choose the synonym of 'Happy'.","Joyful","Sad","Angry","Joyful","Cry","Easy"),
("Mental Ability","हिन्दी","2, 4, 8, 16, ?","32","20","24","32","36","Easy"),
("Arithmetic","हिन्दी","80 का 25% कितना है?","20","10","15","20","25","Easy"),
("Language","हिन्दी","'खुश' का समानार्थी शब्द कौन सा है?","आनंदित","दुःखी","क्रोधित","आनंदित","रोना","Easy")
]

def db():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init():
    c=db()
    c.executescript("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,student_id TEXT UNIQUE,
        password TEXT,parent_mobile TEXT,language TEXT,role TEXT DEFAULT 'student');
        CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,date TEXT,score INTEGER,total INTEGER,
        percentage REAL,details TEXT);
        CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT,language TEXT,question TEXT,
        answer TEXT,a TEXT,b TEXT,c TEXT,d TEXT,difficulty TEXT);
    """)
    if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0]==0:
        c.executemany("""INSERT INTO questions(subject,language,question,answer,a,b,c,d,difficulty)
                         VALUES(?,?,?,?,?,?,?,?,?)""",QUESTIONS)
    if not c.execute("SELECT 1 FROM users WHERE student_id='admin'").fetchone():
        c.execute("INSERT INTO users(name,student_id,password,parent_mobile,language,role) VALUES(?,?,?,?,?,?)",
                  ("Administrator","admin",hashlib.sha256(b"admin123").hexdigest(),"","English","admin"))
    c.commit(); c.close()

@app.route("/")
def home():
    return redirect(url_for("dashboard") if "uid" in session else url_for("login"))

@app.route("/login",methods=["GET","POST"])
def login():
    error=""
    if request.method=="POST":
        sid=request.form["student_id"].strip()
        pw=hashlib.sha256(request.form["password"].encode()).hexdigest()
        c=db(); u=c.execute("SELECT * FROM users WHERE student_id=? AND password=?",(sid,pw)).fetchone(); c.close()
        if u:
            session["uid"]=u["id"]; session["role"]=u["role"]; return redirect(url_for("dashboard"))
        error="Invalid ID or password"
    return render_template("login.html",error=error)

@app.route("/register",methods=["GET","POST"])
def register():
    error=""
    if request.method=="POST":
        try:
            c=db()
            c.execute("INSERT INTO users(name,student_id,password,parent_mobile,language) VALUES(?,?,?,?,?)",
                (request.form["name"],request.form["student_id"],hashlib.sha256(request.form["password"].encode()).hexdigest(),
                 request.form["parent_mobile"],request.form["language"]))
            c.commit(); c.close(); return redirect(url_for("login"))
        except sqlite3.IntegrityError: error="Student ID already exists."
    return render_template("register.html",error=error)

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "uid" not in session:return redirect(url_for("login"))
    c=db(); u=c.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone()
    r=c.execute("SELECT * FROM results WHERE user_id=? ORDER BY id DESC",(u["id"],)).fetchall(); c.close()
    avg=round(sum(x["percentage"] for x in r)/len(r),1) if r else 0
    return render_template("dashboard.html",u=u,results=r,avg=avg)

@app.route("/test")
def test():
    if "uid" not in session:return redirect(url_for("login"))
    lang=request.args.get("lang","English")
    c=db(); qs=c.execute("SELECT * FROM questions WHERE language=? ORDER BY RANDOM() LIMIT 10",(lang,)).fetchall(); c.close()
    return render_template("test.html",qs=qs,lang=lang)

@app.route("/submit",methods=["POST"])
def submit():
    if "uid" not in session:return jsonify(error="login required"),401
    c=db(); qs=c.execute("SELECT * FROM questions WHERE id IN (%s)"%(",".join("?"*len(request.form.getlist("qid")))),request.form.getlist("qid")).fetchall()
    score=0; details=[]
    for q in qs:
        chosen=request.form.get("q_"+str(q["id"]), "")
        ok=chosen==q["answer"]
        score+=ok
        details.append(f'{q["id"]}:{chosen}:{q["answer"]}')
    total=len(qs); pct=round(score*100/total,1) if total else 0
    c.execute("INSERT INTO results(user_id,date,score,total,percentage,details) VALUES(?,?,?,?,?,?)",
              (session["uid"],datetime.now().strftime("%Y-%m-%d %H:%M"),score,total,pct,"|".join(details)))
    c.commit(); c.close()
    return render_template("result.html",score=score,total=total,pct=pct)

@app.route("/admin")
def admin():
    if session.get("role")!="admin": return "Access denied",403
    c=db(); users=c.execute("SELECT id,name,student_id,parent_mobile,language FROM users WHERE role='student'").fetchall()
    results=c.execute("""SELECT users.name,results.date,results.score,results.total,results.percentage
                         FROM results JOIN users ON users.id=results.user_id ORDER BY results.id DESC""").fetchall()
    c.close(); return render_template("admin.html",users=users,results=results)

@app.route("/api/progress")
def progress():
    if "uid" not in session:return jsonify([])
    c=db(); r=c.execute("SELECT date,percentage FROM results WHERE user_id=? ORDER BY id",(session["uid"],)).fetchall(); c.close()
    return jsonify([dict(x) for x in r])

if __name__=="__main__":
    init(); app.run(host="0.0.0.0",port=5000,debug=True)

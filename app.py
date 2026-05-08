import os, uuid, sqlite3, random, re
from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

DB = "data/db.sqlite3"
os.makedirs("data", exist_ok=True)

STATS = ["Strength","Dexterity","Intelligence","Constitution","Charisma"]

# ---------------- DB ----------------

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init():
    c = db().cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS characters(
        id TEXT PRIMARY KEY,
        name TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS stats(
        cid TEXT,
        stat TEXT,
        base INT,
        equip INT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS meta(
        cid TEXT,
        hp INT,
        max_hp INT,
        mana INT,
        max_mana INT,
        level INT,
        gold INT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS equipment(
        cid TEXT,
        text TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS effects(
        id TEXT,
        cid TEXT,
        name TEXT,
        duration INT,
        payload TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id TEXT,
        cid TEXT,
        sender TEXT,
        type TEXT,
        msg TEXT
    )""")

    db().commit()
    db().close()

# ---------------- PARSER ----------------

def parse(text):
    stats = {s:0 for s in STATS}
    skills = {}

    if not text:
        return stats, skills

    for line in text.lower().split("\n"):

        for v,n in re.findall(r"([+-]?\d+)\s*%\s*([a-z ]+)", line):
            skills[n.strip()] = skills.get(n.strip(),0)+int(v)

        for v,n in re.findall(r"([+-]?\d+)\s*([a-z]+)", line):
            for s in STATS:
                if n.startswith(s[:3].lower()):
                    stats[s]+=int(v)

    return stats,skills

# ---------------- HOME ----------------

@app.route("/")
def home():
    c = db().cursor()
    chars = c.execute("SELECT * FROM characters").fetchall()
    return render_template("index.html", chars=chars)

# ---------------- CREATE ----------------

@app.route("/create", methods=["POST"])
def create():
    cid = str(uuid.uuid4())

    c = db().cursor()
    c.execute("INSERT INTO characters VALUES (?,?)",(cid,request.form["name"]))

    for s in STATS:
        c.execute("INSERT INTO stats VALUES (?,?,?,?)",(cid,s,10,0))

    c.execute("INSERT INTO meta VALUES (?,?,?,?,?,?,?)",(cid,100,100,50,50,1,0))

    db().commit()
    return redirect(f"/c/{cid}")

# ---------------- CHARACTER ----------------

@app.route("/c/<cid>")
def character(cid):
    c = db().cursor()

    char = c.execute("SELECT * FROM characters WHERE id=?",(cid,)).fetchone()
    meta = c.execute("SELECT * FROM meta WHERE cid=?",(cid,)).fetchone()

    stats = c.execute("SELECT * FROM stats WHERE cid=?",(cid,)).fetchall()

    eq = c.execute("SELECT text FROM equipment WHERE cid=?",(cid,)).fetchone()
    eq_text = eq["text"] if eq else ""

    eq_stats,_ = parse(eq_text)

    final = {}

    for s in stats:
        total = s["base"] + s["equip"] + eq_stats[s["stat"]]
        final[s["stat"]] = {
            "base":s["base"],
            "total":total,
            "mod":total//5
        }

    return render_template("character.html",
        char=char,
        meta=meta,
        stats=final,
        cid=cid,
        equipment=eq_text
    )

# ---------------- SAVE EQUIPMENT ----------------

@app.route("/save/<cid>", methods=["POST"])
def save(cid):
    data = request.json

    c = db().cursor()
    c.execute("DELETE FROM equipment WHERE cid=?",(cid,))
    c.execute("INSERT INTO equipment VALUES (?,?)",(cid,data["equipment"]))

    db().commit()

    socketio.emit("update",{ "cid":cid },room=cid)

    return {"ok":True}

# ---------------- DICE ENGINE ----------------

@socketio.on("roll")
def roll(data):
    result = random.randint(1,20)
    emit("roll_result",{"result":result},room=data["cid"])

# ---------------- REALTIME JOIN ----------------

@socketio.on("join")
def join(data):
    join_room(data["cid"])

# ---------------- EFFECTS (BUFF SYSTEM) ----------------

@socketio.on("apply_effect")
def effect(data):
    c = db().cursor()

    c.execute("INSERT INTO effects VALUES (?,?,?,?,?)",(
        str(uuid.uuid4()),
        data["cid"],
        data["name"],
        data["duration"],
        data["payload"]
    ))

    db().commit()

    emit("effect_update",data,room=data["cid"])

# ---------------- INIT ----------------

init()

if __name__ == "__main__":
    socketio.run(app,host="0.0.0.0",port=10000)

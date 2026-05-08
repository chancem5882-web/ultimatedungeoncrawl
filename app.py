from flask import Flask, render_template, request, redirect, jsonify
from flask_socketio import SocketIO
from database.db import db
from database.models import Character, Effect, Message
from systems.parser import parse_equipment
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "dcc-secret"

# IMPORTANT: Render-safe absolute DB path
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////opt/render/project/src/data/dcc.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs("/opt/render/project/src/data", exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*")

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------------------
# HOME
# ---------------------------
@app.route("/")
def home():
    chars = Character.query.all()
    return render_template("index.html", chars=chars)


# ---------------------------
# CREATE CHARACTER
# ---------------------------
@app.route("/create", methods=["POST"])
def create():
    name = request.form.get("name")

    char = Character(name=name)

    db.session.add(char)
    db.session.commit()

    return redirect(f"/character/{char.id}")


# ---------------------------
# CHARACTER PAGE
# ---------------------------
@app.route("/character/<int:cid>")
def character(cid):
    char = Character.query.get_or_404(cid)

    parsed = parse_equipment(char.equipment or "")

    effects = Effect.query.filter_by(character_id=cid).all()

    messages = Message.query.filter(
        (Message.target == "all") | (Message.target == str(cid))
    ).all()

    return render_template(
        "character.html",
        char=char,
        parsed=parsed,
        effects=effects,
        messages=messages
    )


# ---------------------------
# UPDATE CHARACTER
# ---------------------------
@app.route("/update/<int:cid>", methods=["POST"])
def update(cid):
    char = Character.query.get_or_404(cid)

    data = request.json

    char.level = data.get("level", 1)

    char.hp = data.get("hp", 100)
    char.max_hp = data.get("max_hp", 100)

    char.mana = data.get("mana", 50)
    char.max_mana = data.get("max_mana", 50)

    char.gold = data.get("gold", 0)

    char.strength = data.get("strength", 10)
    char.dexterity = data.get("dexterity", 10)
    char.intelligence = data.get("intelligence", 10)
    char.constitution = data.get("constitution", 10)
    char.charisma = data.get("charisma", 10)

    char.equipment = data.get("equipment", "")
    char.inventory = data.get("inventory", "")
    char.spells = data.get("spells", "")
    char.skills = data.get("skills", "")

    db.session.commit()

    socketio.emit("character_updated", {"id": cid})

    return jsonify({"success": True})


# ---------------------------
# DM PANEL
# ---------------------------
@app.route("/dm")
def dm():
    chars = Character.query.all()
    effects = Effect.query.all()
    messages = Message.query.all()

    return render_template(
        "dm.html",
        chars=chars,
        effects=effects,
        messages=messages
    )


# ---------------------------
# ADD EFFECT
# ---------------------------
@app.route("/effect", methods=["POST"])
def add_effect():
    effect = Effect(
        character_id=request.form.get("character_id"),
        name=request.form.get("name"),
        duration=request.form.get("duration"),
        effect_text=request.form.get("effect_text")
    )

    db.session.add(effect)
    db.session.commit()

    socketio.emit("effect_added")

    return redirect("/dm")


# ---------------------------
# MESSAGE SYSTEM
# ---------------------------
@app.route("/message", methods=["POST"])
def send_message():
    msg = Message(
        sender=request.form.get("sender"),
        category=request.form.get("category"),
        target=request.form.get("target"),
        content=request.form.get("content")
    )

    db.session.add(msg)
    db.session.commit()

    socketio.emit("new_message")

    return redirect("/dm")


# ---------------------------
# SOCKET CONNECT
# ---------------------------
@socketio.on("connect")
def connect():
    print("Client connected")


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)

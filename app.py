from flask import Flask, render_template, request, redirect, jsonify
from flask_socketio import SocketIO, emit
from database.db import db
from database.models import Character, Effect, Message
from systems.parser import parse_equipment
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "dcc-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/dcc.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs("data", exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*")

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    chars = Character.query.all()
    return render_template("index.html", chars=chars)

@app.route("/create", methods=["POST"])
def create():
    char = Character(
        name=request.form.get("name")
    )

    db.session.add(char)
    db.session.commit()

    return redirect(f"/character/{char.id}")

@app.route("/character/<int:cid>")
def character(cid):

    char = Character.query.get_or_404(cid)

    parsed = parse_equipment(char.equipment)

    effects = Effect.query.filter_by(character_id=cid).all()

    messages = Message.query.filter(
        (Message.target == "all") |
        (Message.target == str(cid))
    ).all()

    return render_template(
        "character.html",
    socketio.run(app, host="0.0.0.0", port=10000)

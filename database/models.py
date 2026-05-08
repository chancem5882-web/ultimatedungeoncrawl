from database.db import db

class Character(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    level = db.Column(db.Integer, default=1)

    hp = db.Column(db.Integer, default=100)
    max_hp = db.Column(db.Integer, default=100)

    mana = db.Column(db.Integer, default=50)
    max_mana = db.Column(db.Integer, default=50)

    gold = db.Column(db.Integer, default=0)

    strength = db.Column(db.Integer, default=10)
    dexterity = db.Column(db.Integer, default=10)
    intelligence = db.Column(db.Integer, default=10)
    constitution = db.Column(db.Integer, default=10)
    charisma = db.Column(db.Integer, default=10)

    equipment = db.Column(db.Text, default="")
    inventory = db.Column(db.Text, default="")
    spells = db.Column(db.Text, default="")
    skills = db.Column(db.Text, default="")

class Effect(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    character_id = db.Column(db.Integer)

    name = db.Column(db.String(100))

    duration = db.Column(db.Integer)

    effect_text = db.Column(db.Text)

class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    sender = db.Column(db.String(100))

    category = db.Column(db.String(100))

    target = db.Column(db.String(100))

    content = db.Column(db.Text)

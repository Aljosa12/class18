import os
from sqla_wrapper import SQLAlchemy
import uuid

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    secret_number = db.Column(db.Integer, unique=False)
    password = db.Column(db.String)
    session_token = db.Column(db.String)

    def profile_url(self):
        return f"/profiles/{self.uid}"


def init_data():
    db.drop_all()
    db.create_all()
    for j in range (1, 6):
        uporabnik1 = User(
            name="Uporabnik" + str(j),
            email="uporabnik" + str(j) + "@neki.domena.si",
            password="password",
            session_token=str(uuid.uuid4()),
            secret_number=-1
        )
        db.add(uporabnik1)
    db.commit()



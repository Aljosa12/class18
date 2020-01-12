import random
import uuid
import hashlib
from random import randint

from flask import Flask, render_template, request, \
    make_response, redirect, url_for
from models import User, db, init_data

db.create_all()
#init_data()

app = Flask(__name__)


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    secret_number = random.randint(1, 30)

    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, password=hashed_password, secret_number=secret_number)

    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:
        session_token = str(uuid.uuid4())

    user.session_token = session_token
    db.add(user)
    db.commit()

    response = make_response(
        redirect(url_for("index"))
    )
    response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
    return response


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("ugibanje.html", user=user)

@app.route("/", methods=["POST"])
def index_post():

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    vpisana = int(request.form.get("ugibanje"))
    uganil = False
    if vpisana > user.secret_number:
        message = "Number is too big"
    elif vpisana == user.secret_number:
        uganil = True
        message = "Bravo, zadel si"
    else:
        message = "Number is too small"
    return render_template("rezultat_ugibanja.html", message=message, uganil=uganil)

@app.route("/reset")
def reset():
    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response

    user.secret_number = randint(0, 100)
    print(user.secret_number)
    db.add(user)
    db.commit()

    response = make_response(
        redirect(url_for("index"))
    )
    return response

@app.route("/profile/")
def profile_view():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    return render_template("profile.html", user=user)

@app.route("/profile/edit", methods=["GET"])
def profile_edit_get():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    return render_template("edit.html", user=user)

@app.route("/profile/edit", methods=["POST"])
def profile_edit_post():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    user.email = request.form.get("email")
    user.name = request.form.get("name")

    db.add(user)
    db.commit()

    return render_template("profile.html", user=user)

@app.route("/profile/delete", methods=["POST"])
def profile_delete_post():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response

    db.delete(user)
    db.commit()

    return make_response(
            redirect(url_for("login_get"))
        )

@app.route("/list", methods=["GET"])
def list_users():
    users = db.query(User).all()

    return render_template("list_users.html", users=users)

@app.route("/profile/password", methods=["GET"])
def profile_password_get():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    return render_template("password.html", user=user)


@app.route("/profile/password", methods=["POST"])
def profile_password_post():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    old_password = request.form.get("old-password")
    new_password = request.form.get("new-password")
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()  # hash the old password
    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()  # hash the old password

    if hashed_old_password == user.password:
        # if yes, save the new password hash in the database
        user.password = hashed_new_password
    else:
        # if not, return error
        return "Wrong (old) password! Go back and try again."

    db.add(user)
    db.commit()

    return render_template("profile.html", user=user)


@app.route("/profiles/<user_uid>")
def view_user(user_uid):
    user = db.query(User).filter_by(uid=user_uid).first()
    return render_template("profile_other.html", user=user)


if __name__ == '__main__':
    app.run()
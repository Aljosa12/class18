from random import randint, seed
seed(100)
from flask import Flask, render_template, request, \
    make_response, redirect, url_for
from models import User, db


db.create_all()

app = Flask(__name__)


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    name = request.form.get("name")
    email = request.form.get("email")

    user = User(name=name, email=email,
                secret_number=6)

    db.add(user)
    db.commit()

    response = make_response(
        redirect(url_for("index"))
    )
    response.set_cookie("email", email)
    return response


@app.route("/")
def index():
    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    print(user.email, user.name)
    return render_template("ugibanje.html")

@app.route("/", methods=["POST"])
def index_post():
    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        response = make_response(
            redirect(url_for("login_get"))
        )
        return response
    vpisana = int(request.form.get("ugibanje"))
    uganil = False
    if vpisana > user.secret_number:
        message = "Ugibana številka je prevelika"
    elif vpisana == user.secret_number:
        message = "Bravo, zadel si"
        uganil = True
    else:
        message = "Ugibana številka je prtremajhna"
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
    db.add(user)
    print(user.secret_number)
    db.commit()
    response = make_response(
        redirect(url_for("index"))
    )
    return response

if __name__ == '__main__':
    app.run()
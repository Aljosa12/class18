from flask import Flask, render_template, request, make_response, redirect, url_for
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

    user = User(name=name, email=email, secret_number=6)

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
    if user is not None:
        print(user.email, user.name)
    return "<h1>naslov</h1>"



if __name__ == '__main__':
    app.run()
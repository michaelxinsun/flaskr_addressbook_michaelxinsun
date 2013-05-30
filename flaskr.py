# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = "/tmp/contacts.db"
DEBUG = True
SECRET_KEY = "development key"
USERNAME = "admin"
PASSWORD = "default"

# create our little application
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config["DATABASE"])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource("schema.sql") as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/")
def show_contacts():
    cur = g.db.execute("select firstname, middlename, lastname, address, phone, email from contacts order by id desc")
    contacts = [dict(firstname = row[0], 
                    middlename = row[1],
                    lastname = row[2],
                    address = row[3],
                    phone = row[4],
                    email = row[5]) for row in cur.fetchall()]
    return render_template("show_contacts.html", contacts=contacts)

@app.route("/add", methods=["POST"])
def add_contact():
    if not session.get("logged_in"):
        abort(401)
    g.db.execute("insert into contacts (firstname, middlename, lastname, address, phone, email) values (?, ?, ?, ?, ?, ?)",
                 [request.form["firstname"], 
                  request.form["middlename"],
                  request.form["lastname"],
                  request.form["address"],
                  request.form["phone"],
                  request.form["email"]])
    g.db.commit()
    flash("New contact was successfully posted")
    return redirect(url_for("show_contacts"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"]:
            error = "Invalid username"
        elif request.form["password"] != app.config["PASSWORD"]:
            error = "Invalid password"
        else:
            session["logged_in"] = True
            flash("You were logged in")
            return redirect(url_for("show_contacts"))
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("show_contacts"))

if __name__ == "__main__":
    init_db()
    app.run()

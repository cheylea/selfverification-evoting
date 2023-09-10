import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/information")
def info():
    return render_template("info.html")

@app.route("/identification")
def id():
    return render_template("id.html")

@app.route("/vote")
def vote():
    return render_template("vote.html")

@app.route("/complete")
def complete():
    return render_template("complete.html")

@app.route("/verify")
def verify():
    #conn = get_db_connection()
    #posts = conn.execute('SELECT * FROM table').fetchall()
    #conn.close()
    return render_template("verify.html")#,posts=table)

if __name__ == '__main__':
    app.run(debug=True, port = 8000)
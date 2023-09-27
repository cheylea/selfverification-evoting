import sqlite3
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from blockchain import Blockchain

blockchain = Blockchain()

app = Flask(__name__)

# Functions for databases

def connect_to_database(database_file):
    conn = sqlite3.connect(database_file, isolation_level=None)
    conn.row_factory = sqlite3.Row
    print("Connection successful!")
    return conn

def execute_sql(conn, sql):
    c = conn.cursor()
    c.execute(sql)

def main():
    app.run(debug=True, port = 8000)
    # Create table for the voters database
    voters = r"databases\voters.db"

    # Table that stores information required to identify is a voter is eligible
    drop_table_voters = """DROP TABLE IF EXISTS voters; """
    create_table_voters = """ CREATE TABLE IF NOT EXISTS voters (
                                id integer PRIMARY KEY,
                                pollstation text,
                                pollnumber integer,
                                name text,
                                address text,
                                postcode text,
                                iseligible integer
                            ); """
    
    # Insert test voters
    insert_table_voters = """ INSERT INTO voters (id, pollstation, pollnumber, name, address, postcode, iseligible)
                              VALUES
                                (1, 'ABC', 1, 'Charlie Voter (Test)', '1 Example Street', 'ZZ01 000', 1),
                                (2, 'ABC', 2, 'Sam Voter (Test)', '2 Example Street', 'ZZ01 000', 1),
                                (3, 'ABC', 3, 'Bailey Voter (Test)', '3 Example Street', 'ZZ01 000', 1);
                              """
    
    conn = connect_to_database(voters)
    if conn is not None:
        execute_sql(conn, drop_table_voters)
        execute_sql(conn, create_table_voters)
        execute_sql(conn, insert_table_voters)
    else:
        print("Error, no connection.")
    
    # Create tables for the votes database
    votes = r"databases\votes.db"

    # Table that stores the blockchain
    create_table_votes = """ TRUNCATE TABLE votes; CREATE TABLE IF NOT EXISTS votes (
                                id integer PRIMARY KEY,
                                block text
                            ); """
    # Table that stores words that cannot be used as secret words
    create_table_words = """ CREATE TABLE IF NOT EXISTS words (
                                id integer PRIMARY KEY,
                                word text,
                                pollstation text
                            ); """
    # Insert banned words
    insert_table_words = """ INSERT INTO words (id, word, pollstation)
                              VALUES
                                (1, 'TEST', 'all'),
                                (2, 'Charlie', 'all'),
                                (3, 'Voter', 'all'),
                                (4, 'Sam', 'all'),
                                (5, 'Bailey', 'all'),
                                (6, 'Example', 'all');
                            """
    conn = connect_to_database(votes)

    if conn is not None:
        execute_sql(conn, create_table_votes)
        execute_sql(conn, create_table_words)
        execute_sql(conn, insert_table_words)
    else:
        print("Error, no connection.")
    
    conn.close()

# App route for index, an introduction welcome page for survey testing
@app.route("/")
def home():
    return render_template("1_index.html")

# App route for frequently asked questions about the tool and blockchain
@app.route("/faqs")
def info():
    return render_template("2_faqs.html")

# 
@app.route("/checkeligibility")
def checkeligibility():
    voters = r"databases\voters.db"
    conn = connect_to_database(voters)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voters;")
    test_voters = cursor.fetchall()
    conn.close
    return render_template("3_checkeligibility.html", test_voters = test_voters)

# Verify if the person is eligible to vote
@app.route("/verifyeligibility", methods=['GET', 'POST'])
def verifyeligibility():
    voters = r"databases\voters.db"
    conn = connect_to_database(voters)
    cursor = conn.cursor()
    pollnumber = request.form['tester']
    cursor.execute(" SELECT IsEligible FROM voters WHERE pollstation || CAST(pollnumber as text) = (?);", (pollnumber,))
    result = cursor.fetchone()
    conn.close
    if result[0] == 1: # Checks if person is eligible to vote
        return redirect(url_for('verifyid', pollnumber = pollnumber))
    else:
        return redirect("error.html")
    
    

# Placeholder for identification process in full version of the artefact
@app.route("/verifyid/<pollnumber>")
def verifyid(pollnumber):
    voters = r"databases\voters.db"
    conn = connect_to_database(voters)
    cursor = conn.cursor()
    cursor.execute(" SELECT name, pollstation FROM voters WHERE pollstation || CAST(pollnumber as text) = (?);", (pollnumber,))
    result = cursor.fetchone()
    conn.close

    return render_template("5_verifyid.html", name = result[0], pollstation = result[1])


@app.route("/vote/<pollstation>")
def vote(pollstation):
    # add stoppage when putting in a bad secret word
    # add "are you sure? pop up"
    return render_template("6_vote.html", pollstation = pollstation)

# Voting Submission
@app.route('/submit_vote/<pollstation>', methods=['GET', 'POST'])
def submit_vote(pollstation):
    votes = r"databases\votes.db"
    conn = connect_to_database(votes)
    cursor = conn.cursor()
    cursor.execute("SELECT block FROM votes v JOIN (SELECT MAX(id) id FROM votes) max ON max.id = v.id ")
    previous_block = cursor.fetchall()
    for row in previous_block:
        previous_block = json.loads(row[0])
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    secretword = request.form['sword']
    candidate = request.form['candidates']
    block = blockchain.create_block(proof, pollstation, secretword, candidate, previous_hash)
    block = str(json.dumps(block))
    cursor.execute("INSERT INTO votes (block) VALUES (?)",(block,))
    conn.close
    return render_template("7_complete.html")

@app.route("/verify")
def verify():
    # add self verification logic, submit poll station and secret word
    return render_template("8_verify.html")

if __name__ == '__main__':
    main()
    
    
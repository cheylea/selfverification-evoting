import sqlite3
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from blockchain import Blockchain
from datetime import datetime, timedelta

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
    cursor.execute(" SELECT name FROM voters WHERE pollstation || CAST(pollnumber as text) = (?);", (pollnumber,))
    result = cursor.fetchone()
    conn.close
    return render_template("5_verifyid.html", name = result[0], pollnumber = pollnumber)


@app.route("/enterword/<pollnumber>")
def enterword(pollnumber):
    return render_template("6_enterword.html", pollnumber = pollnumber)

@app.route("/enterworderror/<pollnumber>")
def enterworderror(pollnumber):
    errormessage = 'The word you have entered cannot be used. Please select another word.'
    return render_template("6_enterword.html", pollnumber = pollnumber, errormessage = errormessage)

@app.route("/enterwordcheck/<pollnumber>", methods=['GET', 'POST'])
def enterwordcheck(pollnumber):
    votes = r"databases\votes.db"
    conn = connect_to_database(votes)
    cursor = conn.cursor()
    secretword = request.form['sword'].upper()
    pollstation = pollnumber[:3]
    cursor.execute("SELECT COUNT(*) FROM words w WHERE pollstation IN ('all', (?)) AND word = (?);", (pollstation, secretword,))
    wordcount = cursor.fetchone()
    if wordcount[0] == 0:
        return redirect(url_for('vote', pollnumber = pollnumber, secretword = secretword))
    else:
        return redirect(url_for('enterworderror', pollnumber = pollnumber))

@app.route("/vote/<pollnumber>/<secretword>")
def vote(pollnumber, secretword):
    return render_template("7_vote.html", pollnumber = pollnumber, secretword = secretword)

# Voting Submission
@app.route('/submitvote/<pollnumber>/<secretword>', methods=['GET', 'POST'])
def submitvote(pollnumber, secretword):
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
    candidate = request.form['candidates']
    pollstation = ''.join(filter(str.isalpha, pollnumber))
    block = blockchain.create_block(proof, pollstation, secretword, candidate, previous_hash)
    block = str(json.dumps(block))
    cursor.execute("INSERT INTO votes (block) VALUES (?)", (block,))
    conn.commit()
    cursor.execute("INSERT INTO words (word, pollstation) VALUES (?, ?)", (secretword, pollstation,))
    conn.commit()
    # In full version the person would be marked as ineligible to vote once vote is committed
    conn.close
    return render_template("8_complete.html")

@app.route("/verify")
def verify():
    # add self verification logic, submit poll station and secret word
    return render_template("9_verify.html")

@app.route("/fetchvote/", methods=['GET', 'POST'])
def fetchvote():
    secretword = request.form['sword'].upper()
    pollstation = request.form['pollstation'].upper()
    voter = pollstation + secretword
    sqlstring = "SELECT block FROM votes v WHERE block LIKE '%" + voter + "%';"

    votes = r"databases\votes.db"
    conn = connect_to_database(votes)
    cursor = conn.cursor()
    cursor.execute(sqlstring)
    voteblock = cursor.fetchall()
    for row in voteblock:
        voteblock = json.loads(row[0])
    candidate = voteblock['candidate']
    timestamp = voteblock['timestamp']
    currenttime = datetime.now()
    timelimit = (datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=5))
    print(timelimit)
    if currenttime >= timelimit:
        errormessage = 'Time to verify vote has expired.'
        candidate = 'Unable to view candidate.'
        return render_template("10_seevote.html", candidate = candidate, errormessage = errormessage)
    else:
        errormessage = ''
        candidate = 'You voted for ' + candidate + '.'
        return render_template("10_seevote.html", candidate = candidate, errormessage = errormessage)

if __name__ == '__main__':
    main()
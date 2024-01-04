# General requirements
from datetime import datetime, timedelta
import os
import base64

# Setup Flask app
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, send_from_directory
from flask_cors import CORS
app = Flask(__name__, instance_relative_config=True)
CORS(app, resources={r"/storephoto": {"origins": "http://127.0.0.1:5000/"}})

# Setup blockchain and encryption
import json
from blockchain import Blockchain
from cryptography.fernet import Fernet
from instance.config import encryption_key
blockchain = Blockchain()
app.config.from_pyfile('config.py')
key = encryption_key

# Setup for SQL databases
import sqlite3
from socket import gethostname
from testdetails import myname, myaddress, mypostcode

# Setup for Identification
from identification import Identification
id = Identification()
UPLOAD_FOLDER = 'uploads' # Define a folder to store uploaded images
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
Full Electronic Voting Tool System with biometric and text identification using driving
licences.
"""

### Functions for databases ###

def connect_to_database(database_file):
    """Connect to a sqlite database

    Key arguments
    database_file -- location of sqlite database file
    """
    conn = sqlite3.connect(database_file, isolation_level=None)
    conn.row_factory = sqlite3.Row
    print("Connection successful!")
    return conn

def execute_sql(conn, sql):
    """Execute SQL to a sqlite database

    Key arguments
    conn -- sqlite connection
    sql -- string of sqlite code
    """
    c = conn.cursor()
    c.execute(sql)

def execute_sql_fetch_one(conn, sql):
    """Execute SQL to a sqlite database
    and fetch answer (one answer only)

    Key arguments
    conn -- sqlite connection
    sql -- select string of sqlite code
    """
    c = conn.cursor()
    c.execute(sql)
    result = c.fetchone()
    return result

def execute_sql_fetch_all(conn, sql):
    """Execute SQL to a sqlite database
    and fetch all answers (multiple answers only)

    Key arguments
    conn -- sqlite connection
    sql -- select string of sqlite code
    """
    c = conn.cursor()
    c.execute(sql)
    result = c.fetchall()
    return result

### Encryption Functions ###
def encrypt(key, message: bytes):
    """Encrypt the provided variable

    Key arguments
    key -- key to encrypt with
    message -- the value to be encrypted
    """
    message = message.encode()
    return Fernet(key).encrypt(message)

def decrypt(key, token: bytes):
    """Decrypt the provided variable

    Key arguments
    key -- key to encrypt with
    message -- the value to be encrypted
    """
    message  = Fernet(key).decrypt(token)
    return message.decode('utf-8')

### Main Application ###
def main():
    """Function that initialises the programme and sets
    up the starting databases

    """

    # Create table for the voters database
    voters = r"databases_test\voters.db"

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
                                (3, 'ABC', 3, 'Bailey Voter (Test)', '3 Example Street', 'ZZ01 000', 1),
                                (4, 'ABC', 4, '""" + myname + """', '""" + myaddress + """', '""" + mypostcode + """', 1);
                              """
    
    # Make connection to voters database file
    conn = connect_to_database(voters)
    if conn is not None:
        # Execute required sql
        execute_sql(conn, drop_table_voters)
        execute_sql(conn, create_table_voters)
        execute_sql(conn, insert_table_voters)
        print("Voter database complete.")
        
    else:
        print("Error, no connection.")
    
    # Create tables for the votes database
    votes = r"databases_test\votes.db"

    # Table that stores the blockchain
    drop_table_votes = """DROP TABLE IF EXISTS votes; """
    create_table_votes = """ CREATE TABLE IF NOT EXISTS votes (
                                id integer PRIMARY KEY,
                                block text
                            ); """
    # Table that stores words that cannot be used as secret words
    drop_table_words = """DROP TABLE IF EXISTS words; """
    create_table_words = """ CREATE TABLE IF NOT EXISTS words (
                                id integer PRIMARY KEY,
                                word text,
                                pollstation text
                            ); """
    # Insert banned words
    insert_table_words = """ INSERT INTO words (id, word, pollstation)
                              VALUES
                                (1, 'TEST', 'all'),
                                (2, 'CHARLIE', 'all'),
                                (3, 'VOTER', 'all'),
                                (4, 'SAM', 'all'),
                                (5, 'BAILEY', 'all'),
                                (6, 'EXAMPLE', 'all');
                            """
    
    # Table that stores basic information about test candidates
    drop_table_candidates = """DROP TABLE IF EXISTS candidates; """
    create_table_candidates = """ CREATE TABLE IF NOT EXISTS candidates (
                                id integer PRIMARY KEY,
                                candidatename text,
                                candidateparty text
                            ); """
    
    # Insert test candidates
    insert_table_candidates = """ INSERT INTO candidates (id, candidatename, candidateparty)
                              VALUES
                                (1, 'Amanda Candidate', 'Circle Party'),
                                (2, 'Benjamin Candidate', 'Triangle Party'),
                                (3, 'Chloe Candidate', 'Square Party'),
                                (4, 'David Candidate', 'Pentagon Party'),
                                (5, 'Emma Candidate', 'Hexagon Party'),
                                (6, 'Frederick Candidate', 'Octogon Party');
                              """
    
    # Make connection to voters database file
    conn = connect_to_database(votes)
    if conn is not None:
        # Execute required sql
        execute_sql(conn, drop_table_votes)
        execute_sql(conn, create_table_votes)
        execute_sql(conn, drop_table_words)
        execute_sql(conn, create_table_words)
        execute_sql(conn, insert_table_words)
        execute_sql(conn, drop_table_candidates)
        execute_sql(conn, create_table_candidates)
        execute_sql(conn, insert_table_candidates)
        print("Votes database complete.")
    else:
        print("Error, no connection.")

    # Add first block to the database so it has a starting point
    firstblock = blockchain.create_block(proof=1, pollstation='none', secretword='none', candidate='none', previous_hash='0')
    firstblock = str(json.dumps(firstblock))
    insert_first_block = "INSERT INTO votes (block) VALUES ('" + firstblock + "');"
    execute_sql(conn, insert_first_block)
    conn.close()

# App route for index, an introduction welcome page for survey testing
@app.route("/")
def home():
    return render_template("1_index.html")

# App route for frequently asked questions about the tool and blockchain
@app.route("/faqs")
def info():
    return render_template("2_faqs.html")

# Placeholder for providing your poll number or name and address to check eligibility (must come before ID check)
@app.route("/checkeligibility")
def checkeligibility():
    # Connect to voters and get full list
    voters = r"databases_test\voters.db"
    select_all_voters = "SELECT * FROM voters;"
    conn = connect_to_database(voters)
    result = execute_sql_fetch_all(conn, select_all_voters)
    conn.close
    return render_template("3_checkeligibility.html", test_voters = result)

# Verify if the person is eligible to vote
@app.route("/verifyeligibility", methods=['GET', 'POST'])
def verifyeligibility():
    # Connect to voters and get eligibility check for person
    voters = r"databases_test\voters.db"
    pollnumber = request.form['tester']
    select_eligibility = "SELECT IsEligible FROM voters WHERE pollstation || CAST(pollnumber as text) = '" + pollnumber + "';"
    conn = connect_to_database(voters)
    result = execute_sql_fetch_one(conn, select_eligibility)
    conn.close

    pollnumber = encrypt(key, pollnumber) # encrypt for url
    if result[0] == 1: 
        # If person is eligible, proceed
        return redirect(url_for('verifyid', pollnumber = pollnumber))
    else:
        # If person is not eligible, redirect
        # For this version of the tool this is an error page as all test credentials should be eligible
        return redirect("error.html")

# Placeholder for identification process in full version of the artefact
@app.route("/verifyid/<pollnumber>")
def verifyid(pollnumber):
    # Connect to voters and their details for screen display
    voters = r"databases_test\voters.db"
    pollnumber = decrypt(key, pollnumber) # decrypt for database
    select_voter_details = "SELECT name FROM voters WHERE pollstation || CAST(pollnumber as text) = '" + pollnumber + "';"
    conn = connect_to_database(voters)
    result = execute_sql_fetch_one(conn, select_voter_details)
    conn.close

    pollnumber = encrypt(key, pollnumber) # encrypt for url
    return render_template("5_verifyid.html", name = result[0], pollnumber = pollnumber.decode('utf-8'))

# Screen to take photo of driving licence
@app.route("/idphoto/<pollnumber>")
def idphoto(pollnumber):
    return render_template("5a_idphoto.html", pollnumber = pollnumber)

# Store ID photo
@app.route('/storephoto/<pollnumber>', methods=['POST'])
def storephoto(pollnumber):
    imagedata = request.form['imagedata']

    pollnumber = decrypt(key, pollnumber) # decrypt
    pollnumber = encrypt(key, pollnumber) # encrypt

    # Store photo with the encrypted pollnumber
    imagepath = 'idphoto/' + pollnumber.decode('utf-8') + '_idphoto.png'
    imagename = pollnumber.decode('utf-8') + '_idphoto.png'
    with open(imagepath, 'wb') as f:
        f.write(base64.b64decode(imagedata.split(',')[0]))
        
    return redirect(url_for('checkid', pollnumber = pollnumber.decode('utf-8'), imagename = imagename))

# Check Photo
@app.route("/checkid/<pollnumber>/<imagename>", methods=['GET'])
def checkid(pollnumber, imagename):

    # Connect to voters and their get details to compare to ID
    voters = r"databases_test\voters.db"
    pollnumber = decrypt(key, pollnumber) # decrypt for database
    select_voter_name = "SELECT name FROM voters WHERE pollstation || CAST(pollnumber as text) = '" + pollnumber + "';"
    select_voter_address = "SELECT address FROM voters WHERE pollstation || CAST(pollnumber as text) = '" + pollnumber + "';"
    select_voter_postcode = "SELECT postcode FROM voters WHERE pollstation || CAST(pollnumber as text) = '" + pollnumber + "';"
    conn = connect_to_database(voters)
    name = execute_sql_fetch_one(conn, select_voter_name)
    address = execute_sql_fetch_one(conn, select_voter_address)
    postcode = execute_sql_fetch_one(conn, select_voter_postcode)
    conn.close
    pollnumber = encrypt(key, pollnumber) # encrypt for url

    name = name[0]
    address = address[0] + postcode[0]

    # Check identity
    # First check the text on the id card
    imagepath = 'idphoto/' + imagename

    text_result = id.check_identification_text(imagepath, name, address)
    print(text_result)
    if text_result[0] > 0.5 and text_result[1] > 0.5:
        # If passes text check, then moves to photo check
        face_result = id.check_identification_face(imagepath)
        if face_result == "true":
            # If person passes the ID check, then they proceed
            print("passed")
            os.remove(imagepath)
            return jsonify({'status': 'success'})
        elif face_result == "error, face not found":
            print("face not found")
            os.remove(imagepath)
            return jsonify({'status': 'fail'})
        else:
            # If the face check has failed redirect to failure screen
            print("failed face check")
            os.remove(imagepath)
            return jsonify({'status': 'fail'})
    elif text_result[0] == -1: # error, text not found
        # If passes text check, then moves to photo check
        print("text not found")
        os.remove(imagepath)
        return jsonify({'status': 'fail'})
    else:
        print("failed text check")
        os.remove(imagepath)
        return jsonify({'status': 'fail'})

# Screen for passed ID check
@app.route("/passedidcheck/<pollnumber>")
def passedidcheck(pollnumber):
    return render_template("5b_idphoto_pass.html", pollnumber = pollnumber)

# Screen for failed ID check
@app.route("/failedidcheck/<pollnumber>")
def failedidcheck(pollnumber):
    return render_template("5c_idphoto_fail.html", pollnumber = pollnumber)

# Screen to enter secret word
@app.route("/enterword/<pollnumber>")
def enterword(pollnumber):
    return render_template("6_enterword.html", pollnumber = pollnumber)

# Submission route when entering a secret word
@app.route("/enterwordcheck/<pollnumber>", methods=['GET', 'POST'])
def enterwordcheck(pollnumber):
    #  Connect to votes database to check if secret word has been used
    votes = r"databases_test\votes.db"
    secretword = request.form['sword'].upper()
    pollnumber = pollnumber.encode()
    pollnumber = decrypt(key, pollnumber) # decrypt for database
    pollstation = pollnumber[:3] # extract poll station from poll number
    count_matching_words = "SELECT COUNT(*) FROM words w WHERE pollstation IN ('all', '"+ pollstation +"') AND word = '" + secretword + "';"
    conn = connect_to_database(votes)
    result = execute_sql_fetch_one(conn, count_matching_words)
    conn.close

    pollnumber = encrypt(key, pollnumber) # encrypt for url
    secretword = encrypt(key, secretword) # encrypt for url
    if result[0] == 0:
        # If word has not been used, proceed to vote page
        return redirect(url_for('vote', pollnumber = pollnumber, secretword = secretword))
    else:
        # If word has been used before, error and redirect to page indicating to try again
        return redirect(url_for('enterworderror', pollnumber = pollnumber))

# Screen to enter secret word when previous word cannot be used with error message
@app.route("/enterworderror/<pollnumber>")
def enterworderror(pollnumber):
    errormessage = 'The word you have entered cannot be used. Please select another word.'
    return render_template("6_enterword.html", pollnumber = pollnumber, errormessage = errormessage)

# Screen to vote
@app.route("/vote/<pollnumber>/<secretword>")
def vote(pollnumber, secretword):
    # Connect to voters database to get list of candidates to vote for
    voters = r"databases_test\votes.db"
    select_all_candidates = "SELECT * FROM candidates;"
    conn = connect_to_database(voters)
    result = execute_sql_fetch_all(conn, select_all_candidates)
    conn.close
    return render_template("7_vote.html", candidates = result, pollnumber = pollnumber, secretword = secretword)

# Submission route when submitting vote
@app.route('/submitvote/<pollnumber>/<secretword>', methods=['GET', 'POST'])
def submitvote(pollnumber, secretword):
    # Connect to votes database to get last block
    votes = r"databases_test\votes.db"
    select_last_block = "SELECT block FROM votes v JOIN (SELECT MAX(id) id FROM votes) max ON max.id = v.id"
    conn = connect_to_database(votes)
    previous_block = execute_sql_fetch_all(conn, select_last_block)

    # Loads the different parts of the blockchain block
    for row in previous_block:
        previous_block = json.loads(row[0])
    previous_proof = previous_block['proof']

    # Get required block variables
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    candidate = request.form['candidates']
    pollnumber = decrypt(key, pollnumber.encode())
    secretword = decrypt(key, secretword)
    pollstation = ''.join(filter(str.isalpha, pollnumber))

    # Mine new block
    block = blockchain.create_block(proof, pollstation, secretword, candidate, previous_hash)
    block = str(json.dumps(block))

    # Insert block and used word into votes database
    insert_new_block = "INSERT INTO votes (block) VALUES ('" + block + "');"
    insert_used_word = "INSERT INTO words (word, pollstation) VALUES ('" + secretword + "', '" + pollstation + "');"
    execute_sql(conn, insert_new_block)
    execute_sql(conn, insert_used_word)
    conn.commit()
    # In full version the person would be marked as ineligible to vote once vote is committed
    conn.close
    return render_template("8_complete.html")

# Screen to request pollstation and secret word to verify vote
@app.route("/verify")
def verify():
    return render_template("9_verify.html")

# Submission route when requesting verification
@app.route("/fetchvote/", methods=['GET', 'POST'])
def fetchvote():
    # Connect to votes database to get who person voted for
    secretword = request.form['sword'].upper()
    pollstation = request.form['pollstation'].upper()
    voter = pollstation + secretword
    votes = r"databases_test\votes.db"
    select_vote = "SELECT block FROM votes v WHERE JSON_EXTRACT(block, '$.voter') = '" + voter + "';"
    conn = connect_to_database(votes)
    voteblock = execute_sql_fetch_all(conn, select_vote)
    conn.close()

    # If vote is found
    if voteblock:
        # Loads the different parts of the blockchain block
        for row in voteblock:
            voteblock = json.loads(row[0])

        # Calculate if vote is in expiration period
        candidate = voteblock['candidate']
        timestamp = voteblock['timestamp']
        currenttime = datetime.now()
        timelimit = (datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=5))

        if currenttime >= timelimit:
            # If too much time has passed, the user is notified this has expired
            errormessage = 'Time to verify vote has expired.'
            candidate = 'Unable to view candidate.'
            return render_template("10_seevote.html", candidate = candidate, errormessage = errormessage)
        else:
            # If still within the time frame, user is shown their vote
            errormessage = ''
            if len(candidate) == 0:
                candidate = 'You registered your vote as a non vote.'
            else:
                candidate = 'You voted for ' + candidate + '.'
            return render_template("10_seevote.html", candidate = candidate, errormessage = errormessage)

    # If vote cannot be found
    else:
        errormessage = 'Word and polling station did not find a match.'
        candidate = 'Unable to view candidate.'
        return render_template("10_seevote.html", candidate = candidate, errormessage = errormessage)

# Initialise
if __name__ == '__main__':
    main()
    # If statement to prevent run when hosting in PythonAnywhere
    if 'liveconsole' not in gethostname():
        app.run(debug=True)
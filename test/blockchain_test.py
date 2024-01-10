# Python Programme to test Blockchain class
import os
import inspect
import sys
cdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(cdir)
sys.path.insert(0, parentdir)

# Setup blockchain and encryption
import json
from blockchain import Blockchain
from cryptography.fernet import Fernet
from instance.config import encryption_key
blockchain = Blockchain()
key = encryption_key

# Setup random word generation
import random
import string

candidates = ["Test Candidate 1", "Test Candidate 2", "Test Candidate 3", "Test Candidate 4", "Test Candidate 5", "Test Candidate 6"]

# Functions sourced from: https://pynative.com/python-generate-random-string/
def get_random_string(length):
    """Generated a random string
    of uppercase letters

    Key arguments
    length -- how long you want the string to be
    """
    # Choose from all uppercase letter
    letters = string.ascii_uppercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str



def blockchain_test_block():
    """Creates a block in the existing
    chain that will randomly experience
    "interferencd" leading to the chain 
    being altered.

    Key arguments
    none
    """
    previous_block = blockchain.return_previous_block()
    previous_proof = previous_block['proof']

    # Get required block variables
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    pollstation = "ABC"
    secretword = get_random_string(10)
    candidate = candidates[random.randint(1, 5)]

    # Introduce random possibility of replacement block
    if random.random() < 0.01:
        candidate = candidates[0] # For just this test, can tell when the candidate was changed
        previous_hash = "HACKED" + get_random_string(58)

    # Mine new block
    block = blockchain.create_block(proof, pollstation, secretword, candidate, previous_hash)
    block = str(json.dumps(block))


def test_blockchain(chain_length):
    """Creates a blockchain using
    the test block method which could
    be either valid or invalid and
    returns its assessment

    Key arguments
    none
    """
    i = 1
    # Create test blockchain to desired length
    while i < chain_length:
        blockchain_test_block()
        i += 1
    test_blockchain = blockchain.chain
    # Test if the chain is valid
    if blockchain.chain_valid(test_blockchain) == True:
        result = "Chain valid"
    else:
        result = "Chain not valid"
    # Return result
    final_result = [result, test_blockchain]
    # Write result to file
    with open("test/results/blockchain_test_chain.txt","a") as blockchain_test_chain:
        blockchain_test_chain.write("%s\n" % final_result)

# U N C O M M E N T   T O   R E F R E S H   R E S U L T S
# Run a set number of test blockchains and check their validity
#with open("test/blockchain_test_chain.txt","w") as blockchain_test_chain:
#    i = 1
#    while i <= 200:
#        blockchain.__init__() # Initialise to refresh chain
#        test_blockchain(20) # Create test chains of 20
#        print("Test " + str(i) + " complete.")
#        i += 1

# Read positive and negative results from the file
blockchain_results = []
with open("test/results/blockchain_test_chain.txt","r") as bc_results:
    for line in bc_results:
        result = line[:-1] # Remove new line character
        result = result.strip('][').split(', ')
        blockchain_results.append(result)

# Create empty list to store results
results = []

# Get the count of True Positives, False Positives, True Negatives and False Negatives
blockchain_true_positives = sum(1 for r in blockchain_results if r[0] == "'Chain valid'" and "HACKED" not in str(r[1:]))
blockchain_false_positives = sum(1 for r in blockchain_results if r[0] == "'Chain valid'" and "HACKED" in str(r[1:]))

blockchain_true_negatives = sum(1 for r in blockchain_results if r[0] == "'Chain not valid'" and "HACKED" in str(r[1:]))
blockchain_false_negatives = sum(1 for r in blockchain_results if r[0] == "'Chain not valid'" and "HACKED" not in str(r[1:]))

# Use the counts to calculate the sensitivity, specificity and accuracy
blockchain_sensitivity = blockchain_true_positives / (blockchain_true_positives + blockchain_false_negatives) * 100
blockchain_specificity = blockchain_true_negatives / (blockchain_false_positives + blockchain_true_negatives) * 100
blockchain_accuracy = (blockchain_true_positives + blockchain_true_negatives) / (blockchain_true_positives + blockchain_false_positives + blockchain_true_negatives + blockchain_false_negatives) * 100

# Add result to list of results
results.append(["All Results        ", blockchain_sensitivity, blockchain_specificity, blockchain_accuracy, blockchain_true_positives, blockchain_false_positives, blockchain_true_negatives, blockchain_false_negatives])

# Print Results
print(results)

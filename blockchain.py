# Python program to create Blockchain
"""
Source: https://www.geeksforgeeks.org/create-simple-blockchain-using-python/
"""
 
# Imports
import datetime # for timestamp
import hashlib # hash calculation for block fingerprints
import json # to store data in blockchain
 
class Blockchain:
 
    def __init__(self):
        """Create first block and set its hash to "0"
        """
        self.chain = []
        self.create_block(proof=1, pollstation='none', secretword='none', candidate='none', previous_hash='0')
 
    def create_block(self, proof, pollstation, secretword, candidate, previous_hash):
        """Create a block to add to the chain

        Key arguments
        proof --
        pollstation --
        secretword --
        candidate --
        previous_hash --
        """
        voter = pollstation + secretword
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'voter': voter,
                 'candidate': candidate,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
 
    def return_previous_block(self):
        """Display previous block
        """
        return self.chain[-1]
 
    def proof_of_work(self, previous_proof):
        """Proof of work to mine block

        Key arguments
        previous_proof --
        """
        new_proof = 1
        check_proof = False
 
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
 
        return new_proof
 
    def hash(self, block):
        """Has calculation for block

        Key arguments
        block --
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
 
    def chain_valid(self, chain):
        """Validate chain

        Key arguments
        chain --
        """
        previous_block = chain[0]
        block_index = 1
 
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
 
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
 
            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1
 
        return True
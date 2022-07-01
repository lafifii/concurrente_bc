from crypt import methods
from hashlib import sha256
import hashlib
import json
import time
import copy
from urllib import response
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory
from numpy import block
import requests
from urllib3 import proxy_from_url

app = Flask(__name__)
PoW = 4

class Block:
    def __init__(self, index, transactions, proof, previous_hash):
        self.index = index 
        self.timestamp = time.time()
        self.transactions = transactions
        self.proof = proof 
        self.previous_hash = previous_hash

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current = []

        self.new_block(previous_hash=1, proof=100)
    
    def newBlock(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'tiimestamp': time.time(),
            'transactions': self.current,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current = []
        self.chain.append(block)

        return block

    def newTransaction(self, sender, recipient, amount):
        self.current.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,

        })

        return self.lastBlock['index'] + 1

    @staticmethod
    def hash(block):
        bst = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(bst).hexdigest()

    @property
    def lastBlock(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof+= 1

        return proof 
    
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        ghash = hashlib.sha256(guess).hexdigest()
        return ghash[:PoW] == PoW*"0"
    

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/minar', methods=['GET'])
def mine():
    lblock = blockchain.lastBlock
    lproof = lblock['proof']
    proof = blockchain.proof_of_work(lproof)

    blockchain.newTransaction(0,node_identifier,1)

    prevhash = blockchain.hash(lblock)
    block = blockchain.newBlock(proof, prevhash)

    response = {
        'mensaje': 'nuevo bloque agregado',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transaccion/nueva', methods=['POST'])
def new_transaction():
    data = request.get_json()
    fields = ['sender', 'recipient', 'amount']
    for f in fields:
        if not data.get(f):
            return "Data invalida", 404
    
    index = blockchain.newTransaction(data['sender'], data['recipient'], data['amount'])
    
    return "Agregando nueva transaccion a bloque " + str(index), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1800)

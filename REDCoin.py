import hashlib
import json
import os
import time
from datetime import datetime
from os import path

usersmaster = {}     # { alias : User }
redchain = {}       #  { nonce : Block }

txpb = 5    # transcations per block

commandsList = ["CreateNewUser", "ViewBalance","ViewPublicKey","ViewPrivateKey","NumberOfUsers","ViewAllAccounts","NewTransaction", "ReviewTransaction", "ReviewUserTransactionHistory", "Quit"]
play = True

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class REDBlock:

    def __init__(self, previousHash):
        self.transactions = {}
        self.hashCode = ""
        self.previousHash = previousHash
        self.nonce = '0'
        self.count = len(self.transactions)
        self.blockInception = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.blockSigned = ""

class Transaction:

    def __init__(self, sender, sender_public_key, receiver, receiver_public_key, amount):
        self.sender = sender
        self.sender_pk = sender_public_key
        self.receiver = receiver
        self.receiver_pk = receiver_public_key
        self.amount = amount
        self.timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.ID = ""

class User:

    def __init__(self, alias):
        self.alias = alias
        self.timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        public_data = alias + self.timestamp
        self.publickey = hashlib.sha256(public_data.encode()).hexdigest()
        private_data = self.timestamp + alias + self.publickey
        self.privatekey = hashlib.sha256(private_data.encode()).hexdigest()
        self.REDCoin = 0.0

def CreateNewUser():

    alias = input("Enter your Alias: ")

    with open("UsersMaster.json", "r+") as f:
        usersmaster = json.load(f)

        if alias in usersmaster.keys():
            print("Alias already taken!")
            alias = input("Enter your Alias: ")
        else:
            user = User(alias)
            usersmaster[alias] = {'publickey':user.publickey, 'privatekey':user.privatekey, 'REDCoin':user.REDCoin }
            f.seek(0)
            json.dump(usersmaster, f, indent = 4)

            print("\nNew User Created!")
            print("Alias: "+user.alias)
            print("Public Key: "+user.publickey)
            print("Private Key: "+user.privatekey)
            print("REDCoin: "+str(user.REDCoin))

def ViewBalance():

    alias = input("What is your Alias: ")

    f = open("UsersMaster.json")
    usersmaster = json.load(f)
    f.close()

    if alias in usersmaster.keys():

        balance = usersmaster[alias]['REDCoin']
        print("RedCoin: "+str(balance))

    else:
        print("Alias not found")


def ViewPublicKey():

    alias = input("What is your Alias: ")

    f = open("UsersMaster.json")
    usersmaster = json.load(f)
    f.close()

    if alias in usersmaster.keys():

        pk = usersmaster[alias]['publickey']
        print("Public Key: "+pk)

    else:
        print("Alias not found")


def ViewPrivateKey():

    alias = input("What is your Alias: ")

    f = open("UsersMaster.json")
    usersmaster = json.load(f)
    f.close()

    if alias in usersmaster.keys():

        vk = usersmaster[alias]['privatekey']
        print("PrivateKey: "+vk)

    else:
        print("Alias not found")


def NumberOfUsers():

    f = open("UsersMaster.json", "r")
    usersmaster = json.load(f)
    f.close()

    print("Number of Users: "+str(len(usersmaster)))


def ViewAllAccounts():

    f = open("UsersMaster.json", "r")
    usersmaster = json.load(f)
    f.close()

    print("Alias:       Balance: ")
    for key, value in usersmaster.items():
        spaces = 13 - len(key)
        space = " "
        for s in range(spaces):
            space = space +" "
        print(key+space+str(value['REDCoin']))


def NewTransaction():

    f = open("UsersMaster.json", "r+")
    usersmaster = json.load(f)

    g = open("REDChain.json", "r+")
    redchain = json.load(g)

    recentBlockID = list(redchain)[-1]    ##maybe this
    recentBlock = redchain[recentBlockID]
    recentCount = recentBlock['count']

    sender = input("Enter your Alias: ")
    if sender in usersmaster.keys():
        senderPrivateKey = input("Enter your Private Key: ")
        if senderPrivateKey == usersmaster[sender]['privatekey']:
            receiver = input("Enter Alias of Recipient: ")
            if receiver in usersmaster.keys():
                amt = input("Enter the Amount: ")
                # Get User Data
                senderBalance = usersmaster[sender]['REDCoin']
                receiverBalance = usersmaster[receiver]['REDCoin']
                senderPublicKey = usersmaster[sender]['publickey']
                receiverPublicKey = usersmaster[receiver]['publickey']
                # Check that the amount is available
                if float(amt) > 0 and float(amt) <= senderBalance:

                    print("Processing..")

                    newTX = Transaction(sender, senderPublicKey, receiver, receiverPublicKey, amt)
                    newTX.timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    hashable = str(newTX.timestamp) + sender+ senderPublicKey + senderPrivateKey + receiver + receiverPublicKey + amt
                    newTX.ID = hashlib.sha256(hashable.encode()).hexdigest()
                    # time.sleep(5)

                    if recentCount < txpb:

                            print("Adding transaction to current block..")
                            # Add Transaction To Current Block
                            redchain[recentBlockID]['transactions'][newTX.ID] = {"sender":newTX.sender, "sender_public_key":newTX.sender_pk, "receiver":newTX.receiver, "receiver_public_key":newTX.receiver_pk, "amount":newTX.amount, "timestamp":newTX.timestamp }
                            # Update Block Count
                            redchain[recentBlockID]['count'] = len(redchain[recentBlockID]['transactions'])
                            print("Block Count: "+str(redchain[recentBlockID]['count']))

                    elif recentCount == txpb:

                        nonce = int(recentBlock['nonce'])
                        previousHash = recentBlock['previousHash']
                        hashthis = "" + previousHash

                        print("Concatenating transaction ids..")
                        # create a string containing all the tx id's
                        for tx in recentBlock['transactions']:
                            hashthis += tx

                        # concatenate nonce to data string
                        hash_this = hashthis + str(nonce)
                        # Find a nonce and sign block with hashcode
                        signHash = hashlib.sha256(hash_this.encode()).hexdigest()
                        print("Finding a nonce and signHash...")

                        while(signHash[0] != '0'):
                            nonce = nonce + 1
                            hashthis_ = hashthis + str(nonce)
                            signHash = hashlib.sha256(hashthis_.encode()).hexdigest()
                            continue

                        # Sign recent block
                        recentBlock['hashCode'] = signHash
                        recentBlock['nonce'] = str(nonce)
                        recentBlock['blockSigned'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                        print("Block Signed!")
                        print("HashCode: "+signHash)
                        print("Nonce: "+str(nonce))

                        # Create a new block with old hash code
                        newBlock = REDBlock(signHash)

                        # Create a BlockID for the new block
                        shashasha = newBlock.blockInception + newBlock.previousHash
                        newBlockID = hashlib.sha256(shashasha.encode()).hexdigest()

                        # Add Transaction Data to Block and Add Block to Chain
                        redchain[newBlockID] = { "transactions": {
                            newTX.ID : {
                                "sender":newTX.sender,
                                "sender_public_key":newTX.sender_pk,
                                "receiver":newTX.receiver,
                                "receiver_public_key":newTX.receiver_pk,
                                "amount":newTX.amount,
                                "timestamp":newTX.timestamp
                            }, }, "blockInception": newBlock.blockInception, "blockSigned": "not signed yet",
                            "hashCode": "not signed", "previousHash": newBlock.previousHash, "nonce": "0", "count": 1 }

                    # Process Transaction
                    usersmaster[newTX.receiver]['REDCoin'] = receiverBalance + float(newTX.amount)
                    usersmaster[newTX.sender]['REDCoin'] = senderBalance - float(newTX.amount)

                    # Write to files
                    f.seek(0)
                    json.dump(usersmaster, f, indent = 4)
                    f.close()

                    g.seek(0)
                    json.dump(redchain, g, indent = 4)
                    g.close()

                    time.sleep(3)
                    print("Transaction Confirmed!")
                    print("TxID: "+newTX.ID)

                else:
                    print("Insufficient REDCoin..")
            else:
                print("Alias not found..")
        else:
            print("Incorrect Private Key..")
    else:
        print("Alias not found..")


def ReviewTransaction():

    with open("REDChain.json", "r") as f:
        redchain = json.load(f)

        txID = input("What is the Transaction ID? ")

        #counts how many blocks have been searched
        counter = 0

        for blockID in redchain.keys():

            counter = counter + 1

            if txID in redchain[blockID]['transactions'].keys():

                if redchain[blockID]['hashCode'] != "not signed":

                    sender = redchain[blockID]['transactions'][txID]['sender']
                    receiver = redchain[blockID]['transactions'][txID]['receiver']
                    amt = redchain[blockID]['transactions'][txID]['amount']
                    time = redchain[blockID]['transactions'][txID]['timestamp']
                    hashcode = redchain[blockID]['hashCode']
                    nonce = redchain[blockID]['nonce']

                    print('Sender: '+sender+"\t\tReceiver: "+receiver)
                    print('REDCoin: '+amt+"\t\tTime: "+time)
                    print("HashCode: "+hashcode)
                    print('Nonce: '+nonce);
                    print("Transaction ID: "+txID)
                    return

                else:
                    print("The block for this transaction has not yet been signed..")
                    return

        # if all the blocks have been searched and txid not found..
        if counter >= len(redchain):

            print("Transaction ID not found..")

def ReviewUserTransactionHistory():

    with open("REDChain.json", "r") as f:
        redchain = json.load(f)

        alias = input("What is your Alias? ")

        resultCount = 0

        for blockID in redchain.keys():

            for txID in redchain[blockID]['transactions']:

                if alias in redchain[blockID]['transactions'][txID].values():

                    s = redchain[blockID]['transactions'][txID]['sender']
                    r = redchain[blockID]['transactions'][txID]['receiver']
                    a = redchain[blockID]['transactions'][txID]['amount']
                    t = redchain[blockID]['transactions'][txID]['timestamp']

                    print("Time: "+t+", Sender: "+s+", Receiver: "+r+", REDCoin: "+str(a)+", \nBlockID: "+blockID+", \ntxID: "+txID)
                    print(" ")
                    resultCount += 1

        if resultCount == 0:

            print("Alias not found.. ")

def ViewBlock():

    with open("REDChain.json", "r") as f:
        redchain = json.load(f)

        response = input("Look up using 1. BlockID or 2. HashCode? ")

        if response == 'BlockID' or response == '1':

            blockID = input("What is the BlockID? ")

            if blockID in redchain.keys():

                print("BlockID: "+blockID)
                print("BlockInception: "+redchain[blockID]['blockInception'])
                print("BlockSigned: "+redchain[blockID]['blockSigned'])
                print("HashCode: "+redchain[blockID]['hashCode'])
                print("Nonce: "+redchain[blockID]['nonce'])
                print("Count: "+redchain[blockID]['count'])

                for txID in redchain[blockID]['transactions']:

                    s = redchain[blockID]['transactions'][txID]['sender']
                    r = redchain[blockID]['transactions'][txID]['receiver']
                    a = redchain[blockID]['transactions'][txID]['amount']
                    t = redchain[blockID]['transactions'][txID]['timestamp']

                    print("Time: "+t+", Sender: "+s+", Receiver: "+r+", REDCoin: "+str(a)+", \ntxID: "+txID)
                    print(" ")

        elif response == 'HashCode' or response == '2':

            hashcode = input("What is the HashCode? ")

            for blockID in redchain.keys():

                if hashcode == redchain[blockID]['hashCode']:

                    print("BlockID: "+blockID)
                    print("BlockInception: "+redchain[blockID]['blockInception'])
                    print("BlockSigned: "+redchain[blockID]['blockSigned'])
                    print("HashCode: "+redchain[blockID]['hashCode'])
                    print("Nonce: "+redchain[blockID]['nonce'])
                    print("Count: "+str(redchain[blockID]['count']))

                    for txID in redchain[blockID]['transactions']:

                        s = redchain[blockID]['transactions'][txID]['sender']
                        r = redchain[blockID]['transactions'][txID]['receiver']
                        a = redchain[blockID]['transactions'][txID]['amount']
                        t = redchain[blockID]['transactions'][txID]['timestamp']

                        print("Time: "+t+", Sender: "+s+", Receiver: "+r+", REDCoin: "+str(a)+", \ntxID: "+txID)
                        print(" ")

# now, to clear the screen
cls()

#populate usersMaster from redchain

print("Welcome to REDCoin! Choose from the following")
while(play):
    print("\nAvailable Commands:")

    for index, cmd in enumerate(commandsList, start=1):
        print("{}: {}".format(index, cmd))

    selection = input()

    if selection == 'CreateNewUser' or selection == '1':

        cls()
        CreateNewUser()

    elif selection == 'ViewBalance' or selection == '2':

        cls()
        ViewBalance()

    elif selection == 'ViewPublicKey' or selection == '3':

        cls()
        ViewPublicKey()

    elif selection =='ViewPrivateKey' or selection == '4':

        cls()
        ViewPrivateKey()

    elif selection == "NumberOfUsers" or selection == '5':

        cls()
        NumberOfUsers()

    elif selection == "ViewAllAccounts" or selection == '6':

        cls()
        ViewAllAccounts()

    elif selection == "NewTransaction" or selection == '7':

        cls()
        NewTransaction()

    elif selection == "ReviewTransaction" or selection == '8':

        cls()
        ReviewTransaction()

    elif selection == 'ReviewUserTransactionHistory' or selection == '9':

        cls()
        ReviewUserTransactionHistory()

    elif selection ==  "Quit" or selection == '10':

        play = False
        cls()
        print("Goodbye..")

    elif selection == "ViewBlock":

        cls()
        ViewBlock()

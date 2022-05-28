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

    def __init__(self, previousNonce):
        self.transactions = {}
        self.previousNonce = previousNonce
        self.nonce = ""
        self.count = len(self.transactions)

class Transaction:

    def __init__(self, sender, sender_public_key, receiver, receiver_public_key, amount):
        self.sender = sender
        self.sender_pk = sender_public_key
        self.receiver = receiver
        self.receiver_pk = receiver_public_key
        self.amount = amount
        self.timestamp = datetime.now()
        self.ID = ""

class User:

    def __init__(self, alias):
        self.alias = alias
        self.timestamp = datetime.now()
        public_data = alias + self.timestamp.strftime("%m/%d/%Y, %H:%M:%S")
        self.publickey = hashlib.sha256(public_data.encode()).hexdigest()
        private_data = self.timestamp.strftime("%m/%d/%Y, %H:%M:%S") + alias + self.publickey
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

    with open("UsersMaster.json", "r+") as f:
        usersmaster = json.load(f)

    with open("REDChain.json", "r+") as g:
        redchain = json.load(g)

    recentNonce = list(redchain)[-1]
    recentBlock = redchain[recentNonce]
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
                    newTX.timestamp = str(datetime.now())
                    hashable = str(newTX.timestamp) + sender+ senderPublicKey + senderPrivateKey + receiver + receiverPublicKey + amt
                    newTX.ID = hashlib.sha256(hashable.encode()).hexdigest()
                    time.sleep(5)
                    print("Submiting Transaction to REDChain..")

                    if recentCount < txpb:

                            # Add Transaction To Current Block
                            redchain[recentNonce]['transactions'][newTX.ID] = {"sender":newTX.sender, "sender_public_key":newTX.sender_pk, "receiver":newTX.receiver, "receiver_public_key":newTX.receiver_pk, "amount":newTX.amount, "timestamp":newTX.timestamp }
                            # Update Block Count
                            redchain[recentNonce]['count'] = len(redchain[recentNonce]['transactions'])

                    elif recentCount == txpb:

                        hashthis = ""
                        for tx in recentBlock['transactions']:
                            hashthis += tx

                        newBlock = REDBlock(recentNonce)
                        # Create a new block hash code
                        newBlock.nonce = hashlib.sha256(hashthis.encode()).hexdigest()
                        # Add Block To Chain
                        redchain[newBlock.nonce] = { "transactions": {}, "previousNonce": newBlock.previousNonce, "nonce": newBlock.nonce , "count": newBlock.count }
                        # Add Transaction To Current Block
                        redchain[newBlock.nonce]['transactions'][newTX.ID] = {"sender":newTX.sender, "sender_public_key":newTX.sender_pk, "receiver":newTX.receiver, "receiver_public_key":newTX.receiver_pk, "amount":newTX.amount, "timestamp":newTX.timestamp }
                        # Update Block Count
                        redchain[newBlock.nonce]['count'] = len(redchain[newBlock.nonce]['transactions'])

                    # Process Transaction
                    usersmaster[newTX.receiver]['REDCoin'] = receiverBalance + float(newTX.amount)
                    usersmaster[newTX.sender]['REDCoin'] = senderBalance - float(newTX.amount)

                    # Write to files
                    with open("UsersMaster.json", "w") as f:        #do i need this open() ?
                        json.dump(usersmaster, f, indent = 4)
                    with open("REDChain.json", "w") as g:
                        json.dump(redchain, g, indent = 4)

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

        for nonce in redchain.keys():

            if txID in redchain[nonce]['transactions'].keys():

                sender = redchain[nonce]['transactions'][txID]['sender']
                receiver = redchain[nonce]['transactions'][txID]['receiver']
                amt = redchain[nonce]['transactions'][txID]['amount']
                time = redchain[nonce]['transactions'][txID]['timestamp']

                print('Sender: '+sender+"\t\tReciever: "+receiver)
                print('REDCoin: '+amt+"\t\tTime: "+time)
                print("Block Nonce: "+nonce)
                print("Transaction ID: "+txID)

def ReviewUserTransactionHistory():

    with open("REDChain.json", "r") as f:
        redchain = json.load(f)

        alias = input("What is your Alias? ")

        resultCount = 0

        for nonce in redchain.keys():

            for txID in redchain[nonce]['transactions']:

                if alias in redchain[nonce]['transactions'][txID].values():

                    s = redchain[nonce]['transactions'][txID]['sender']
                    r = redchain[nonce]['transactions'][txID]['receiver']
                    a = redchain[nonce]['transactions'][txID]['amount']
                    t = redchain[nonce]['transactions'][txID]['timestamp']

                    print("Time: "+t+", Sender: "+s+", Receiver: "+r+", REDCoin: "+str(a)+", \nNonce: "+nonce+", txID: "+txID)
                    print(" ")
                    resultCount += 1

        if resultCount == 0:

            print("Alias not found")

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

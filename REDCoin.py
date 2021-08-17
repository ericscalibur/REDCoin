import hashlib
import json
from datetime import datetime
from os import path

usersmaster = {}     # { alias : User }
redchain = {}       #  { nonce : Block }

txpb = 5    # transcations per block

commandsList = ["CreateNewUser", "ViewBalance","ViewPublicKey","ViewPrivateKey","NumberOfUsers","ViewAllAccounts","NewTransaction", "ReviewTransaction", "ReviewUserTransactionHistory", "Quit"]
play = True

class REDBlock:

	def __init__(self, previousNonce):
		self.transactions = {}
		self.previousNonce = previousNonce
		self.nonce = hashlib.sha256(previousNonce.encode()).hexdigest()
		self.count = len(self.transactions)

class Transaction:

	def __init__(self, sender, receiver, amount):
		self.sender = sender
		self.receiver = receiver
		self.amount = amount
		self.timestamp = datetime
		self.ID = ""

class User:

	def __init__(self, alias):
		self.alias = alias
		self.publickey = hashlib.sha256(alias.encode()).hexdigest()

		data = alias + self.publickey
		self.privatekey = hashlib.sha256(data.encode()).hexdigest()
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
	return

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
	return

def ViewPrivateKey():

	alias = input("What is your Alias: ")

	f = open("UsersMaster.json")
	usersmaster = json.load(f)
	f.close()

	if alias in usersmaster.keys():

		vk = usersmaster[alias]['privatekey']
		print("PublicKey: "+vk)

	else:
		print("Alias not found")
	return

def NumberOfUsers():

	f = open("UsersMaster.json")
	data = json.load(f)
	f.close()

	print("Number of Users: "+str(len(data)))
	return

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
	return

def NewTransaction():

	with open("UsersMaster.json", "r") as f:
		usersmaster = json.load(f)

	with open("REDChain.json", "r") as g:
		redchain = json.load(g)

	recentNonce = list(redchain)[-1]
	recentBlock = redchain[recentNonce]
	recentCount = recentBlock['count']

	sender = input("Enter your Alias: ")
	if sender in usersmaster.keys():
		pk = input("Enter your Private Key: ")
		if pk == usersmaster[sender]['privatekey']:
			receiver = input("Enter Alias of Recipient: ")
			if receiver in usersmaster.keys():
				amt = input("Enter the Amount: ")
				if float(amt) > 0 and float(amt) < usersmaster[sender]['REDCoin']:

					newTX = Transaction(sender, receiver, amt)
					newTX.timestamp = str(datetime.now())
					hashable = ""+str(newTX.timestamp) + sender + receiver
					newTX.ID = hashlib.sha256(hashable.encode()).hexdigest()

					if recentCount < 5:

						AddTransactionToCurrentBlock(recentNonce, newTX)
						print("Transaction Confirmed!")

					elif recentCount == 5:

						newBlock = REDBlock(recentNonce)
						newBlock.nonce = hashlib.sha256(recentNonce.encode()).hexdigest()
						AddBlockToChain(newBlock)

						AddTransactionToCurrentBlock(newBlock.nonce, newTX)
						print("Transaction Confirmed!")

				else:
					print("Insufficient REDCoin")
			else:
				print("Alias not found")
		else:
			print("Incorrect Private Key")
	else:
		print("Alias not found")
	return

def AddTransactionToCurrentBlock(nonce, tx):

	with open("REDChain.json", "r") as f:
		redchain = json.load(f)

	redchain[nonce]['transactions'][tx.ID] = {"sender":tx.sender, "receiver":tx.receiver, "amount":tx.amount, "timestamp":tx.timestamp }
	redchain[nonce]['count'] = len(redchain[nonce]['transactions'])

	with open("REDChain.json", "w") as h:
		h.seek(0)
		json.dump(redchain, h, indent = 4)

	ComputeTransaction(tx)

	return

def AddBlockToChain(block):

	with open("REDChain.json", "r") as f:
		redchain = json.load(f)

	redchain[block.nonce] = { "transactions": {}, "previousNonce": block.previousNonce, "nonce": block.nonce , "count": block.count }

	with open("REDChain.json", "w") as g:
		json.dump(redchain, g, indent = 4)

def ComputeTransaction(tx):

	with open("UsersMaster.json", "r") as f2:
		usersmaster = json.load(f2)

	senderBalance = usersmaster[tx.sender]['REDCoin']
	receiverBalance = usersmaster[tx.receiver]['REDCoin']
	usersmaster[tx.receiver]['REDCoin'] = receiverBalance + float(tx.amount)
	usersmaster[tx.sender]['REDCoin'] = senderBalance - float(tx.amount)

	with open("UsersMaster.json", "w") as f3:
		json.dump(usersmaster, f3, indent=4)

def ReviewTransaction():

	with open("REDChain.json", "r") as f:
		redchain = json.load(f)

	nonce = input("What is the Block Nonce? ")

	if nonce in redchain.keys():

		txID = input("What is the Transaction ID? ")

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

				print("Time: "+t+", Sender: "+s+", Receiver: "+r+", REDCoin: "+a)

				resultCount += 1

	if resultCount == 0:

		print("Alias not found")

print("Welcome to REDCoin! Choose from the following")
while(play):
	print("\nAvailable Commands:")

	for index, cmd in enumerate(commandsList, start=1):
		print("{}: {}".format(index, cmd))

	selection = input()

	if selection == 'CreateNewUser' or selection == '1':

		CreateNewUser()

	elif selection == 'ViewBalance' or selection == '2':

		ViewBalance()

	elif selection == 'ViewPublicKey' or selection == '3':

		ViewPublicKey()

	elif selection =='ViewPrivateKey' or selection == '4':

		ViewPrivateKey()

	elif selection == "NumberOfUsers" or selection == '5':

		NumberOfUsers()

	elif selection == "ViewAllAccounts" or selection == '6':

		ViewAllAccounts()

	elif selection == "NewTransaction" or selection == '7':

		NewTransaction()

	elif selection == "ReviewTransaction" or selection == '8':

		ReviewTransaction()

	elif selection == 'ReviewUserTransactionHistory' or selection == '9':

		ReviewUserTransactionHistory()

	elif selection ==  "Quit" or selection == '10':

		play = False
		print("Goodbye")

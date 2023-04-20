#!torv3_auth

import sys
import os
import base64
import nacl.signing
import nacl.encoding
import re
#import tkinter as tk
#from tkinter import filedialog

# set variables
auth_type = "descriptor"
keytype = "x25519"
hiddenservicedir = ""

# create a graphical interface
#root = tk.Tk()
#root.withdraw()

#create a loop ended by user input
run_again = "y"
while run_again != "n":

	# get input from user
	hiddenservice = re.sub(r'\W+', '', input("Enter the hidden service you want to connect to: "))
	print("Hidden service: " + hiddenservice)

	# get the key from the user# check if /var/lib/tor exists
	if os.path.isdir("/var/lib/tor"):
		print("/var/lib/tor exists")
		# check if /var/lib/tor/hiddenservice exists
		if os.path.isdir("/var/lib/tor/" + hiddenservice):
			print("/var/lib/tor/" + hiddenservice + " exists")
			hiddenservicedir = "/var/lib/tor/" + hiddenservice
		else:
			print("/var/lib/tor/" + hiddenservice + " does not exist")
	else:
		print("/var/lib/tor does not exist")

	username = re.sub(r'\W+', '', input("Enter your username: "))
	print("Username: " + username)

	# get hostname from file /var/lib/tor/hiddenservice/hostname
	onion_hostname = open(hiddenservicedir + "/hostname", "r").read()
	onion_hostname = onion_hostname[:-7]
	print("Onion hostname: " + onion_hostname)
	
	signing_key = nacl.signing.SigningKey.generate()
	verify_key = signing_key.verify_key
	verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
	verify_key_base64 = verify_key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')
	verify_key = verify_key_base64[:-1]

	# get private key
	private_key = signing_key.encode(encoder=nacl.encoding.Base64Encoder).decode('utf-8')
	private_key = private_key[:-1]
	
	# create a file in hiddenservicedir/authorized_clients named username.auth containing auth_type:keytype:signing_key
	auth_file = open(hiddenservicedir + "/authorized_clients/" + username + ".auth", "w")
	auth_file.write(auth_type + ":" + keytype + ":" + verify_key_base64)
	auth_file.close()

	auth_string = onion_hostname + ":" + auth_type + ":" + keytype + ":" + private_key
	print("Auth string: " + auth_string)


	# create a file containing python script
	python_file = open("client_config.py", "w")
	python_file.write("#!/usr/bin/python3.11\n")
	python_file.write("import sys\n")
	python_file.write("import os\n")

	# create a function
	python_file.write("def set_clientonionauthdir():\n")
	python_file.write("\tif os.path.isfile(\"/etc/tor/torrc\"):\n")
	python_file.write("\t\ttor_conf = open(\"/etc/tor/torrc\", \"r\")\n")
	python_file.write("\t\ttor_conf_content = tor_conf.read()\n")
	python_file.write("\t\tif \"ClientOnionAuthDir\" in tor_conf_content:\n")
	python_file.write("\t\t\tprint(\"ClientOnionAuthDir already set in /etc/tor\")\n")
	python_file.write("\t\telse:\n") 
	python_file.write("\t\t\tprint(\"ClientOnionAuthDir does not exist\")\n")
	python_file.write("\t\t\tclientonionauthdir = input(\"Enter the directory you want to use for ClientOnionAuthDir: \")\n")
	python_file.write("\t\t\ttor_conf = open(\"/etc/tor/torrc\", \"a\")\n")
	python_file.write("\t\t\ttor_conf.write(\"ClientOnionAuthDir \" + clientonionauthdir)\n")
	python_file.write("\t\t\ttor_conf.close()\n")
	python_file.write("\telse:\n")
	python_file.write("\t\tprint(\"/etc/tor/torrc does not exist\")\n")

	# create a function
	python_file.write("def create_auth_file():\n")
	python_file.write("\tclientonionauthdir = open(\"/etc/tor/torrc\", \"r\")\n")
	python_file.write("\tclientonionauthdir_content = clientonionauthdir.read()\n")
	python_file.write("\tclientonionauthdir_content = clientonionauthdir_content.split()\n")
	python_file.write("\tclientonionauthdir = clientonionauthdir_content[1]\n")
	python_file.write("\tauth_file = open(clientonionauthdir + \"/\" + username + \".auth_private\", \"w\")\n")
	python_file.write("\tauth_file.write(auth_string)\n")
	python_file.write("\tauth_file.close()\n")
	
	# call function
	python_file.write("set_clientonionauthdir()\n")

	# call function
	python_file.write("create_auth_file()\n")
	
	python_file.close()

# ask user if they would like to run the script again
	run_again = input("Would you like to run the script again? (y/n): ")
	if run_again == "y":
		print("Running script again")
	else:
		print("Exiting script")
		sys.exit()

#close the loop

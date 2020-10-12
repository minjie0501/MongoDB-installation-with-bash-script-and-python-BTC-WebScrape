#! /usr/bin/bash

echo "Setting up mongoDB"

wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -

echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

sudo apt-get update

sudo apt-get install -y mongodb-org

sudo systemctl start mongod

sudo systemctl --no-pager status mongod

#mongo --host <HOSTNAME> --port <PORT>
mongo<<EOF
use admin
db.createUser( { user: "superuser", pwd: "p@ss", roles: [ "readWrite", "dbAdmin" ]})
EOF

echo -e "\n"
echo "${bold}You have installed mongodb and created a user called 'superuser' with readWrite role"

#Make sure to have the python script and the bash script in the same directory
python3 WebScrapeBlockChain_PerMinute_UpdatedRealTime.py

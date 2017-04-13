# public_transport

You will need to create some extra files

credentials.txt
if you asked De Lijn for access to their data

dblogin.py

where you put your database login details:

import postgresql

db = postgresql.open('pq://username:password@url:port/dbinstance')

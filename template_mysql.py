import pymysql
import getpass
from sshtunnel import SSHTunnel
from altonline_app import AltOnline
group_name = "ht25_2_1dl301_group_74"
group_password = "pasSWd_74"

def program(mydb):
	mycursor = mydb.cursor()
	mycursor.execute("SHOW TABLES")
	for x in mycursor:
		print(x)

	mycursor.close()

def db_connect(host, port):
	mydb = pymysql.connect(
		database=group_name,
		user=group_name,
		password=group_password, 
		host=host, 
		port=port
	)
	program(mydb)
	app = AltOnline()
	#app.browse_dep(mydb)
	app.change_disc(mydb)
	mydb.close()
	
if __name__ == '__main__':
	#ssh_username = input("Enter your Studium username: ")
	#ssh_password = getpass.getpass("Enter your Studium password A: ")
	ssh_username = "sooi7076"
	ssh_password = "qozbu0-mUtber-gokhoq"

	tunnel = SSHTunnel(ssh_username, ssh_password, 'fries.it.uu.se', 22)
	tunnel.start(local_host='127.0.0.1', local_port=3306, remote_host='127.0.0.1', remote_port=3306)

	# Now the tunnel is ready, connect to DB
	db_connect(tunnel.local_host, tunnel.local_port)

	# Stop the tunnel
	tunnel.stop()
import os
import psycopg2
import urlparse

DATABASE_URL = "postgres://jstgsgfleazuvu:nJGYg0dT6AYMNbqdBkV3bIf-Q8@ec2-184-73-165-195.compute-1.amazonaws.com:5432/dbaklh7r4800dg"
#Connecting to database
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(DATABASE_URL)



def opendb():
    return psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

def closedb(conn):
    conn.commit()
    conn.close()


userconn = opendb()
userdb = userconn.cursor()
##userdb.execute('''CREATE TABLE Users
##             (twitter_handle TEXT, twitter_id TEXT, instamojo_auth TEXT)''')
##userdb.execute("INSERT INTO Users VALUES ('InstamojoBot','3183114434','bade10ebfbac041b362a82611d0d194f')")
userdb.execute('SELECT * FROM Users')
users = userdb.fetchall()
####userdb.execute("DELETE from Users where twitter_handle='InstamojoBot'")
for user in users:
    print str(user)
closedb(userconn)

print
print

tweetsconn = opendb()
tweetsdb = tweetsconn.cursor()
##tweetsdb.execute('''CREATE TABLE Tweets
##             (twitter_handle TEXT, tweet TEXT, instamojo_url TEXT)''')
tweetsdb.execute('SELECT * FROM Tweets')
tweets = tweetsdb.fetchall()
for tweet in tweets:
    print str(tweet)
closedb(tweetsconn)


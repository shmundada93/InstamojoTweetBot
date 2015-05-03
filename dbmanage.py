import sqlite3

def opendb(db):
    return sqlite3.connect(db)

def closedb(conn):
    conn.commit()
    conn.close()


userdb = opendb("users.db")
##userdb.execute('''CREATE TABLE Users
##             (twitter_handle, twitter_id, instamojo_auth)''')
##userdb.execute("INSERT INTO Users VALUES ('InstamojoBot','3183114434','bade10ebfbac041b362a82611d0d194f')")
users = userdb.execute('SELECT * FROM Users')
##userdb.execute("DELETE from Users where twitter_handle='InstamojoBot'")
for user in users:
    print str(user)
closedb(userdb)

print
print

tweetsdb = opendb("tweets.db")
##tweetsdb.execute('''CREATE TABLE Tweets
##             (twitter_handle, tweet , instamojo_url)''')
tweets = tweetsdb.execute('SELECT * FROM Tweets')
for tweet in tweets:
    print str(tweet)
closedb(tweetsdb)


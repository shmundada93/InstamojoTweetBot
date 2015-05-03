import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
import sqlite3
from instamojo import Instamojo
import re
 
# Twitter Consumer keys and access tokens, used for OAuth
consumer_key = 'nZEzUToqKZcMIWu4nSNXnq6Kq'
consumer_secret = 'xZpwdeiE4FnhQ5E4SE7O3KKa3FCzNWiPfDGRvrIPyHZKvpo4ZH'
access_token = '3183114434-w4opn1VCE4DONH3aTybI0BjMVcdfphNrlbBVP9R'
access_token_secret = 'bz5RRCPpg1qCsRehFCzgoeqlKtKq45rSvyZ9fMGuLCYwb'

#Database Open/Close methods
def opendb(db):
    return sqlite3.connect(db)

def closedb(conn):
    conn.commit()
    conn.close()
    
#Tweet pattern
pattern = r'#sell (.*) which is (.*) and costs (\d+) (\w+)'

class StdOutListener(tweepy.streaming.StreamListener):
    ''' Handles data received from the stream. '''
 
    def on_status(self, status):
        
        text = status.text.encode('ascii','ignore')

        if "#sell " in text:
            twitter_id = str(status.author.id_str)
            twitter_handle = str(status.author.screen_name)
            try:
                m = re.match(pattern, text)
                params =  m.groups()
                instamojo_auth = user_details[twitter_id]["instamojo_auth"]
                
                api = Instamojo(api_key='4dcb3d45a65808a290e7b79336b4c5be',
                            auth_token=instamojo_auth)

                # Create a Instamojo Link.
                response = api.link_create(title=params[0],
                                   description=params[1],
                                   base_price=params[2],
                                   currency=params[3])
                
                # URL of the created link
                url =  str(response['link']['url'])

                #Printing to console
                print twitter_handle
                print text
                print url
                
                # Saving details to Tweets database
                c = opendb('tweets.db')
                c.execute("INSERT INTO Tweets VALUES ('%s','%s','%s')"%(twitter_handle,text,url))
                closedb(c)
                print "Database Updated"
                
            except:
                pass
        return True
 
    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True # To continue listening
 
    def on_timeout(self):
        print('Timeout...')
        return True # To continue listening

#Select twitter_ids to follow
userdb = opendb("users.db")
users = userdb.execute('SELECT * FROM Users')
user_details = {}
twitter_ids = []
for user in users:
    twitter_ids.append(str(user[1]))
    user_details[str(user[1])] = {"twitter_handle":str(user[0]),"instamojo_auth":str(user[2])}
closedb(userdb)


#Initializing stream 
listener = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
stream = Stream(auth, listener)
stream.filter(follow=twitter_ids)

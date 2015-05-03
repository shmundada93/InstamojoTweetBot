import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
import sqlite3
from instamojo import Instamojo
import re
import os
import psycopg2
import urlparse
 
# Twitter Consumer keys and access tokens, used for OAuth
consumer_key = 'nZEzUToqKZcMIWu4nSNXnq6Kq'
consumer_secret = 'xZpwdeiE4FnhQ5E4SE7O3KKa3FCzNWiPfDGRvrIPyHZKvpo4ZH'
access_token = '3183114434-w4opn1VCE4DONH3aTybI0BjMVcdfphNrlbBVP9R'
access_token_secret = 'bz5RRCPpg1qCsRehFCzgoeqlKtKq45rSvyZ9fMGuLCYwb'

#Connecting to database
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse("postgres://jstgsgfleazuvu:nJGYg0dT6AYMNbqdBkV3bIf-Q8@ec2-184-73-165-195.compute-1.amazonaws.com:5432/dbaklh7r4800dg")

#Database Open/Close methods

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
                conn = opendb()
                c = conn.cursor()
                c.execute("INSERT INTO Tweets VALUES ('%s','%s','%s')"%(twitter_handle,text,url))
                closedb(conn)
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
userconn = opendb()
userdb = userconn.cursor()
userdb.execute('SELECT * FROM Users')
users = userdb.fetchall()
user_details = {}
twitter_ids = []
for user in users:
    twitter_ids.append(str(user[1]))
    user_details[str(user[1])] = {"twitter_handle":str(user[0]),"instamojo_auth":str(user[2])}
closedb(userconn)


#Initializing stream 
listener = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
stream = Stream(auth, listener)
stream.filter(follow=twitter_ids)

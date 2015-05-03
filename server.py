import os
import sqlite3
import heroku
from flask import Flask
from flask import request,redirect,flash
from instamojo import Instamojo
from tweepy import OAuthHandler
import tweepy

cloud = heroku.from_key('f7842503-7b2e-43c3-9a4d-2401b7c34387')
herokuapp = cloud.apps['instamojotweet']

# Twitter Consumer keys and access tokens, used for OAuth
consumer_key = 'nZEzUToqKZcMIWu4nSNXnq6Kq'
consumer_secret = 'xZpwdeiE4FnhQ5E4SE7O3KKa3FCzNWiPfDGRvrIPyHZKvpo4ZH'
access_token = '3183114434-w4opn1VCE4DONH3aTybI0BjMVcdfphNrlbBVP9R'
access_token_secret = 'bz5RRCPpg1qCsRehFCzgoeqlKtKq45rSvyZ9fMGuLCYwb'

def opendb(db):
    return sqlite3.connect(db)

def closedb(conn):
    conn.commit()
    conn.close()


app = Flask(__name__)

@app.route("/")
def Tweets():
    c = opendb('tweets.db')
    tweets = '<a href="/signup"> Signup for InstamojoTweetLink Service</a>' + "<br>"
    for tweet in c.execute('SELECT * FROM Tweets'):
        tweets = tweets + "<br>" + str(tweet[0]) + "<br>" + str(tweet[1]) + "<br>" + str(tweet[2]) + "<br>" + "<hr>"
    closedb(c)
    return tweets

@app.route("/signup")
def Signup():
    page = """<a href="/"> Home </a>
    <form action="/add" method=post>
      <br>
      <dt>Username:
      <dd><input type=text name=username>
      <dt>Password:
      <dd><input type=password name=password>
      <dt>Twitter Handle:
      <dd><input type=text name=twitter_handle>
      <dd><input type=submit value=Login>
    </dl>
    </form>"""
    return page

@app.route("/add", methods = ['POST'])
def add_user():
    api = Instamojo(api_key='4dcb3d45a65808a290e7b79336b4c5be',
                auth_token='bade10ebfbac041b362a82611d0d194f')
    try:
        token = api.auth(request.form['username'],request.form['password'])
    except:
        token = 'bade10ebfbac041b362a82611d0d194f'
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    twitter_id = str(api.get_user(request.form['username']).id_str)
    c = opendb('users.db')
    users = c.execute('SELECT * FROM Users')
    flag = True
    for user in users:
        if str(user[1]) == twitter_id:
            flag = False
    if flag:
        c.execute("INSERT INTO Users VALUES ('%s','%s','%s')"%(request.form['twitter_handle'],twitter_id,token))
    closedb(c)
    herokuapp.processes['worker'].restart()
    return 'Thanks. User created : <a href="/"> Home </a>'
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=True)

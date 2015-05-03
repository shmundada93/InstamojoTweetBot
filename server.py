import os
import psycopg2
import urlparse
import heroku
from flask import Flask
from flask import request,redirect,flash
from instamojo import Instamojo
from tweepy import OAuthHandler
import tweepy

cloud = heroku.from_key('f7842503-7b2e-43c3-9a4d-2401b7c34387')
herokuapp = cloud.apps['instamojobot']

# Twitter Consumer keys and access tokens, used for OAuth
consumer_key = 'nZEzUToqKZcMIWu4nSNXnq6Kq'
consumer_secret = 'xZpwdeiE4FnhQ5E4SE7O3KKa3FCzNWiPfDGRvrIPyHZKvpo4ZH'
access_token = '3183114434-w4opn1VCE4DONH3aTybI0BjMVcdfphNrlbBVP9R'
access_token_secret = 'bz5RRCPpg1qCsRehFCzgoeqlKtKq45rSvyZ9fMGuLCYwb'

#Connecting to database
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse("postgres://jstgsgfleazuvu:nJGYg0dT6AYMNbqdBkV3bIf-Q8@ec2-184-73-165-195.compute-1.amazonaws.com:5432/dbaklh7r4800dg")



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


app = Flask(__name__)

@app.route("/")
def Tweets():
    conn = opendb()
    c = conn.cursor()
    c.execute('SELECT * FROM Tweets')
    tweets = c.fetchall()
    page = '<a href="/signup"> Signup for InstamojoTweetLink Service</a>' + "<br>"
    for tweet in tweets:
        page = page + "<br>" + str(tweet[0]) + "<br>" + str(tweet[1]) + "<br>" + str(tweet[2]) + "<br>" + "<hr>"
    closedb(conn)
    return page

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
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        twitter_id = str(api.get_user(request.form['username']).id_str)
        conn = opendb()
        c = conn.cursor()
        c.execute('SELECT * FROM Users')
        users = c.fetchall()
        flag = True
        for user in users:
            if str(user[1]) == twitter_id:
                flag = False
        if flag:
            c.execute("INSERT INTO Users VALUES ('%s','%s','%s')"%(request.form['twitter_handle'],twitter_id,token))
        closedb(conn)
        herokuapp.processes['worker'][0].restart()
        return 'Thanks. User created : <a href="/"> Home </a>'
    except:
        return 'Sorry. Some Error : <a href="/"> Home </a>'
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=True)

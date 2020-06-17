import os,flask_session,requests


from flask import Flask, render_template, request, session,jsonify
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                  # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                    # database are kept separate


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
@app.route("/")
def index():
    headline='testando antes de comemcar o app'
    return render_template("index.html", headline=headline)

@app.route("/login")
def login():

        return render_template("login.html")

@app.route("/register")
def register():

     return render_template("register.html")

@app.route("/register2",methods=['POST'])
def register2():
    channels = db.execute("SELECT * FROM channel").fetchall()
    db.commit()
    username=request.form['username']
    psw= request.form['psw']
    user_id = db.execute("INSERT INTO users(username,psw) VALUES(:username,:psw) RETURNING id",{"username":username,'psw':psw}).fetchone()
    db.commit()
    session['username'] = username
    session['id'] =user_id

    return render_template("homepage.html" ,username=session['username'],id=session['id'],channels=channels)

@app.route("/login2",methods=['POST'])
def login2():
    username= request.form['username']
    psw= request.form['psw']

    check=db.execute("SELECT * FROM users WHERE username=:username AND psw=:psw",{"username":username,"psw":psw}).fetchone()
    db.commit()
    if check:
        channels = db.execute("SELECT * FROM channel").fetchall()
        db.commit()
        session['username'] = username
        session['id'] =check.id
        return render_template('homepage.html', username=session['username'],id=session['id'],channels=channels)
    else:
        return render_template('login.html')


@app.route("/homepage")
def homepage():
    channels= db.execute("SELECT * FROM channel").fetchall()
    db.commit()
    return render_template("homepage.html",username=session['username'],id=session['id'],channels=channels)

@app.route("/createchannel")
def createchannel():
    return render_template('createchannel.html',username=session['username'],id=session['id'])

@app.route("/createchannel2" ,methods={'post'})
def createchannel2():
    name = request.form['channel_name']
    check=db.execute("SELECT * FROM channel WHERE name=:name",{"name":name}).fetchone()
    if check:
        return render_template('createchannel.html',username=session['username'],id=session['id'])

    db.execute("INSERT INTO channel(name) VALUES(:name)",{"name":name})
    db.commit()
    return render_template("homepage.html",msg='channel created')
@app.route("/logout/")
def logout():
    session['username'] = ''
    session['id'] = ''
    return render_template('login.html')
@socketio.on('msg_giff')
def msg(data):

    url=data["url"]
    username=session['username']
    user_id=session['id']
    channel_id=data["channel_id"]


    id =  db.execute('INSERT INTO text(text,url,user_id) VALUES(:text,:url,:user_id) RETURNING id',{"text":'',"url":url,"user_id":user_id}).fetchone()
    db.execute('INSERT INTO channel_text(channel_id,text_id) VALUES(:channel_id,:text_id)',{"channel_id":channel_id,"text_id":id.id})
    db.commit()
    emit(channel_id, {'text':'','url':url,'username':username}, broadcast=True)
@socketio.on('msg')
def msg(data):
    text=data["text"]
    url=data["url"]
    username=session['username']
    user_id=session['id']
    channel_id=data["channel_id"]

    print(text, url, user_id)
    if text=='':
        return


    id =  db.execute('INSERT INTO text(text,url,user_id) VALUES(:text,:url,:user_id) RETURNING id',{"text":text,"url":url,"user_id":user_id}).fetchone()
    db.execute('INSERT INTO channel_text(channel_id,text_id) VALUES(:channel_id,:text_id)',{"channel_id":channel_id,"text_id":id.id})
    db.commit()
    emit(channel_id, {'text':text,'username':username}, broadcast=True)

@app.route("/selectmsgs/<int:channel_id>", methods=["GET"])
def select(channel_id):

    msg=db.execute("SELECT t.text, t.created_at ,t.user_id, t.url, u.username FROM text AS t JOIN users AS u ON t.user_id=u.id JOIN channel_text AS ct ON t.id=ct.text_id WHERE ct.channel_id=:channel_id LIMIT 100",{"channel_id":channel_id}).fetchall()
    db.commit
    r= requests.get('https://api.giphy.com/v1/stickers/random?api_key=48NW50Y7uuRCv01SltBUCCJiTcCMuCtu&tag=funny')
    if r.status_code ==200:
        r=r.json()

        return jsonify({"msgs": [dict(row) for row in msg],"giff":r})

    return jsonify({"msgs":[dict(row) for row in msg]})


#  postgres://uzxrgrlgjuoora:098f316c7d5d5c4a1c113a7260577dc0081b648329892ef0957eab627835975c@ec2-54-247-125-38.eu-west-1.compute.amazonaws.com:5432/d1thovrbh565q5
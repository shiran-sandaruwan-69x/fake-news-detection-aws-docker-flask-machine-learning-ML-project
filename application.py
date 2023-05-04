from flask import Flask,render_template,url_for,request,flash,session,redirect, url_for
import joblib
import re
import string
import pandas as pd
from search import search
from flask_sqlalchemy import SQLAlchemy
import os

application = Flask(__name__)
Model = joblib.load('model.pkl')

application.secret_key="super-secret-key"

db_path=os.path.join(os.path.dirname(__file__), 'application.db')

db_url = os.environ["DB_URL"]

application.config['SQLALCHEMY_DATABASE_URI'] =db_url #f'mysql+pymysql://admin:Sadaruwan#1234@database-2.cywe51zuss6h.us-east-1.rds.amazonaws.com:3306/sample_db'
db=SQLAlchemy(application)



class Student(db.Model):
	Sno=db.Column(db.Integer,primary_key=True)
	Name=db.Column(db.String(80),nullable=False)
	Dob=db.Column(db.String(80))
	Email=db.Column(db.String(80),nullable=False)
	Username=db.Column(db.String(80),nullable=False)
	Password=db.Column(db.String(80),nullable=False)

db.create_all()    
	
# Login page
@application.route('/',methods=['GET','POST'])
def login():
	return render_template('login.html')
	session.pop('user')

# Registered page
@application.route('/register',methods=['GET','POST'])
def register():
	return render_template('register.html')

		
#all login conditions 
@application.route('/validations',methods=['GET','POST'])
def validations():
	ex=""
	flag=0
	ex=Student().query.all()


	if request.method=='POST':
		# from login page
		user1=request.form.get('username')
		password1=request.form.get('password')
		
	
		for i in ex:
			if i.Username==user1 and i.Password==password1:
				n=i.Name
				d=i.Dob
				e=i.Email
				session['user']=user1
				flag=1
				break
			elif i.Username==user1 and i.Password!=password1:
				flag=2
				break
    #return render_template("home.html",name=n,dob=d,email=e,username=user1)
	if flag==1:
		return render_template("index.html")

	elif flag==2:
		flash("Incorrect password.Try again.....")
		return render_template("login.html")
	else: 
		flash("User is not registered...please signup")
		return render_template("login.html")


#all registration
@application.route('/registeration',methods=['GET','POST'])

def registeration():
	if (request.method=='POST'):
		name2=request.form.get('name')
		date2=request.form.get('dob')
		email2=request.form.get('email')
		username2=request.form.get('username')
		password2=request.form.get('password')


		ex=""
		flag=0
		ex=Student().query.all()
		for i in ex:
			if i.Username==username2:
				flag=1
				break
			elif i.Email==email2:
				flag=2
				break


		if flag==1:
			flash('Username is already in use')
			return render_template('register.html')
		elif flag==2:
			flash('Email is already in use')
			return render_template('register.html')
		else:
			entry=Student(Name=name2,Dob=date2,Email=email2,Username=username2,Password=password2)
			db.session.add(entry)
			db.session.commit()
			flash('User successfully registered')
			return render_template('login.html')

        

@application.route('/FakeNews')
def index():
    return render_template("index.html")

def wordpre(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) # remove special chars
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

@application.route('/FakeNews',methods=['POST'])
def pre():
    if request.method == 'POST':
        txt = request.form['txt']
        txt = wordpre(txt)
        txt = pd.Series(txt)
        # pd.Series(txt) wenne me dee
        # d = {'a': 1, 'b': 2, 'c': 3}
        # ser = pd.Series(data=d, index=['a', 'b', 'c'])
        # ser
        # a   1
        # b   2
        # c   3
        result = Model.predict(txt)
        return render_template("index.html", result = result)
    return '' 

@application.route("/search", methods=["POST", "GET"])
def searchr():
	if request.method == "POST":
		query = request.form["query"]
		results = search(query)
		session["results"] = results
		session["query"] = query
		return redirect(url_for("searchr"))
	return render_template("search.html", results=session["results"], query=session["query"])    

if __name__ == "__main__":
    application.run(host="0.0.0.0",port=8000,debug=True)
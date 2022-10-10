
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import boto3
import json
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
configFile = open('AppConfig.json')
configData = json.load(configFile)

app = Flask(__name__)
app.config['MYSQL_HOST'] = configData['SQL_HOST']
app.config['MYSQL_USER'] = configData['SQL_USER']
app.config['MYSQL_PASSWORD'] = configData['SQL_PASSWORD']
app.config['MYSQL_DB'] = configData['SQL_DB']
app.config['UPLOAD_FOLDER'] = configData['UPLOAD_FOLDER']
app.secret_key = configData['SECRET_KEY']

mySqlConnection = MySQL(app)

s3_client = boto3.resource(
	's3',
	aws_access_key_id=configData['AWS_ACCESS_KEY_ID'],
	aws_secret_access_key=configData['AWS_SECRET_ACCESS_KEY'],
	region_name=configData['REGION_NAME']
	)


@app.route('/Auth/Register', methods=['GET', 'POST'])
def Register():

 if request.method == 'POST' and 'email' in request.form and 'username' in request.form and 'password' in request.form:
    
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    cursor = mySqlConnection.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("Select * from users where email LIKE %s", [email])
    user = cursor.fetchone()

    if user:
       flash("user already exist", "Danger")
    else:
       query = "insert into users(username,email,password) values(%s,%s,%s)"
       values = (username, email, generate_password_hash(password))
       cursor.execute(query, values)
       mySqlConnection.connection.commit()

       return redirect(url_for('Login'))

 return render_template('Register.html', title="File Uploader - Register")


@app.route('/Auth/Login', methods=['GET', 'POST'])
def Login():

 if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
    email = request.form['email']
    password = request.form['password']
    print(password, email)
    cursor = mySqlConnection.connection.cursor(MySQLdb.cursors.DictCursor)
    user = cursor.execute(
        "Select * from users where users.email =  %s", [email])
    error = None
    user = cursor.fetchall()[0]
    print(user)
    if user is None:
       error = 'username or password error'
    elif check_password_hash(user['password'], password) == False:
       error = 'username or password error'
    else:
       session.clear()
       session['userid'] = user['username']
       session['email'] = user['email']
       return redirect(url_for('FileUploader'))

    flash(error)

 return render_template('Login.html', title="File Uploader - Login")


@app.route('/Auth/Logout')
def logout():
    session.clear()
    redirect(url_for('Login'))



@app.route('/User/FileUploader', methods=['GET', 'POST'])
def FileUploader():

   if request.method == 'POST':
      emailstemp = [request.form['email1'], request.form['email2'],
         request.form['email3'], request.form['email4'], request.form['email5']]
      f = request.files['file']
      temp = {"recipients": emailstemp, "sender": session.get('email')}
      with open("./ccfinal/emails.json","w") as jsonfile:
         json.dump(temp,jsonfile)

      filefullname = f.filename
      fileExtension = filefullname.split(".")[-1]
      filename = filefullname.split(".")[:-1][0]
      key = str(uuid.uuid4())+"."+fileExtension
      filepath = os.path.join(app.config['UPLOAD_FOLDER'], key)
      emailfilepath = os.path.join(app.config['UPLOAD_FOLDER'], "emails.json")

      f.save(filepath)
      s3_client.meta.client.upload_file(filepath,configData['BUCKET_NAME'],key)				  
         
      s3_client.meta.client.upload_file(emailfilepath,configData['BUCKET_EMAIL'],"emails.json")

   return render_template('UploadFiles.html',title="File Uploader - Upload")       

@app.route('/User/Files', methods=['GET'])
def GetFiles():
    userid=session.get('userid')

    if userid is not None:
        cursor = mySqlConnection.connection.cursor(MySQLdb.cursors.DictCursor)
        files=cursor.execute("Select * from files where userid = %s",[userid]).fetchall()
        jlist=None
        for index,file in files:                  
            if index==0:
               jitem={"url":file['fileurl']}
               jlist=json.loads(jitem)
            else:
               jitem={"url":file['fileurl']}
               jlist.update(jitem)
        resp=jlist
        resp.status_code=200
        return resp      
    else:
        redirect(url_for('Login'))
     


if __name__=='__name__':
   app.run(host="127.0.0.1",port="5000",debug = True)
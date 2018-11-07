from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re


app = Flask(__name__)
app.secret_key = 'lololol'
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route("/")
def index():
  
    
    return render_template('index.html')

@app.route("/register_account", methods=["POST"])
def validate_and_create_email():
  mysql = connectToMySQL('login_registration')
  emails = mysql.query_db('SELECT email FROM user')
  isValid = True
  first_name = request.form['first_name']
  last_name = request.form['last_name']
  email = request.form['email']
  print(emails)
  
  if len(request.form['password']) > 0 and request.form['password'] == request.form['vpassword']:
      pw_hash = bcrypt.generate_password_hash(request.form['password'])
      
      
  else:
      flash("Please provide a password")

  if len(first_name) < 2:
    isValid = False
    flash(u"Please enter a valid First Name", "fail")

  if len(last_name) < 2:
    isValid = False
    flash(u"Please enter a valid Last Name", "fail")

  if not EMAIL_REGEX.match(email):
      isValid = False
      flash(u"Invalid Email Address", 'fail')
  
  for db_email in emails:
      print(db_email)
      if db_email['email'] == email:
          isValid = False
          flash('email already exists in database')
  

  if isValid == True:
      
      query = 'INSERT INTO user (first_name, last_name, email, password_hash) VALUES (%(fn)s, %(ln)s, %(e)s, %(ph)s)'
      data = {
        'fn': first_name,
        'ln': last_name,
        'e': email,
        'ph': pw_hash
        }
      mysql = connectToMySQL('login_registration')  
      new_email_id = mysql.query_db(query, data)
      flash(u"User successfully created", 'success')
     
  return redirect('/')

@app.route('/login', methods=["POST"])
def check_credentials_and_log_in():
    
    login_email = request.form['email']
    login_password = request.form['password']
    mysql = connectToMySQL('login_registration')
    users = mysql.query_db('SELECT id, email FROM user')
    
    
    for user in users:
        print(user)
        if user['email'] == login_email:
            print('matched **************')
            user_id = int(user['id'])
            
            mysql = connectToMySQL('login_registration')
            login_password_hash_and_email = mysql.query_db(f'select password_hash, email from user WHERE id = {user_id}')
                   
            if bcrypt.check_password_hash(login_password_hash_and_email[0]['password_hash'], login_password):
                session['logged_in_user'] = login_password_hash_and_email[0]['email']

                flash(u'Login Successful', 'success')
                return redirect('/success')
        else:
          flash(u'Improper credentials', 'fail')
          
    return redirect('/')
    

    

@app.route("/success")
def show_success_page():
    session.pop('_flashes', None)
    mysql = connectToMySQL('login_registration')
    data = {'id': session['logged_in_user']}
    user = mysql.query_db('SELECT first_name, last_name FROM user WHERE email = %(id)s', data)

    

    return render_template('success.html', user = user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ =='__main__':
    app.run(debug=True)

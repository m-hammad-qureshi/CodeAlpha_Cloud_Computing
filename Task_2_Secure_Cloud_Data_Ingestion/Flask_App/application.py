""" To run the flask app use this command in terminal "flask --app main run", "python main.py run", but this will not refresh the app along with the changes you made. To refresh it with your code updating use debug mode like this "flask --app main run --debug" here main is your file name in my case the file name is main. Or you can just pass the debug=True like this app.run(debug=True) at code line 229. """

""" 
Hashing using the Python bcrypt module is a one-way process used for secure verification. 
Once a password is encrypted into a hash, it can never be decrypted back into its original form. 

Cryptography (using Fernet AES-256) is a two-way process. It allows us to encrypt sensitive data 
at rest before saving it to the database, and safely decrypt it back to human-readable form when needed.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, text
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# Load environment variables from the local .env file
load_dotenv()   

# Encryption key for the email and phone.
raw_key = os.getenv("ENCRYPTION_KEY")     

if raw_key:
    encoded_key = raw_key.encode('utf-8')
    cipher = Fernet(encoded_key)
else:
    raise ValueError("Encryption key not found in the .env file.")


"""
This function encrypts sensitive user data (like emails or phone numbers) before it is stored. 
It encodes human-readable string data into bytes, encrypts it using AES-256 via Fernet, 
and returns it as a decoded string compatible with database text fields.
"""

def encrypted_data(plain_text):
    if not plain_text:
        return None
    plain_text_byte = plain_text.encode('utf-8')
    encrypted_text = cipher.encrypt(plain_text_byte)
    return encrypted_text.decode('utf-8')

"""
This function decrypts encrypted database text fields back into their original forms. 
It handles checking data types, safely passing them through the cryptographic cipher, 
and converting the output bytes back into a standard Python string.
"""

def decrypted_data(cipher_text):
    if not cipher_text:
        return None
    if isinstance(cipher_text, str):
        cipher_text_byte = cipher_text.encode('utf-8')
    else:
        cipher_text_byte = cipher_text

    decrypted_text = cipher.decrypt(cipher_text_byte)
    return decrypted_text.decode('utf-8')


base_url = os.getenv("DATABASE_URL")
def db_insert():
    """ 
    AWS Cloud Deployment Code Block (Commented out for standalone Local/Offline Testing):
    ---------------------------------------------------------------------------------
    db_name = base_url.split('/')[-1]
    root_url = base_url.rsplit('/', 1)[0] + '/information_schema'
    root_engine = create_engine(root_url)
    
    with root_engine.connect() as root_conn:
        root_conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name};"))
        root_conn.commit()
    root_engine.dispose()
    """
    
    target_engine = create_engine(base_url, echo= True)    
    with target_engine.connect() as conn:
        conn.execute(text('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username VARCHAR(100) NOT NULL, 
                            email VARCHAR(250) NOT NULL, 
                            phone VARCHAR(250) NOT NULL,
                            password VARCHAR(250) NOT NULL);'''))
        conn.commit()
    target_engine.dispose()    

# Execute database system
db_insert()

engine = create_engine(base_url, echo=True)

application = Flask(__name__)

""" 
The __name__ variable acts as a core roadmap helper for Flask. 
It tells the framework where to look for supporting frontend files like the 'templates' 
folder for HTML and static directories for styling. When executing a file directly, 
Python automatically configures this value to '__main__'.
"""

application.secret_key = os.getenv("APP_SESSION_KEY")

""" route is a decorator which tells the flask that which function will trigger, like here passed / in the route is where this app will land first and it will tell what to show the user with the help of this function. """

@application.route('/')
def root():
    return redirect(url_for('login'))

@application.route('/Home')
def home():
    if 'username' in session:
        logged_user = session["username"]
        with engine.connect() as conn:
            data_query = text("select * from users where username = :logged_user")
            data_result = conn.execute(data_query, {
                "logged_user": logged_user
            }).fetchone()
            if data_result:

                # SQLAlchemy _mapping configuration maps specific column strings straight to the application
                id_data = data_result._mapping['id']
                username_data = data_result._mapping['username']
                email_data = data_result._mapping['email']
                phone_data = data_result._mapping['phone']
                hashed_pass = data_result._mapping['password']
                
                # Decrypting data streams on the fly to render clean data securely back onto the Home user dashboard
                
                email_data_decrypted = decrypted_data(email_data) # --> To look the decrypted email
                phone_data_decrypted = decrypted_data(phone_data) # --> To look the decrypted phone

                return render_template('index.html', id = id_data,user = username_data, email = email_data, phone = phone_data, password = hashed_pass)
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))        

@application.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_input = request.form.get('username')
        password_input = request.form.get('password')

        with engine.connect() as conn:
            # Parameterized Query architecture strictly neutralizes SQL Injection vectors
            login_query = text("select * from users where username = :username")
            login_result = conn.execute(login_query, {
                "username": username_input}).fetchone()
        if login_result is None:
            flash("The user is not exist")
            return redirect(url_for('login'))
        else:
            stored_pass = login_result._mapping['password']
            user_pass_byte = password_input.encode('utf-8')
            stored_pass_byte = stored_pass.encode('utf-8')

            # Utilizing bcrypt secure mathematical evaluation checks to match hashes safely
            if bcrypt.checkpw(user_pass_byte, stored_pass_byte):  
                print("Welcome back")
                session["username"] = username_input
                return redirect(url_for('home'))  
            else:
                flash("Invalid password, try again!")
                return redirect(url_for('login'))  

    return render_template('login.html')

@application.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username_input = request.form.get('username')
        email_input = request.form.get('email')
        phone_input = request.form.get('phone')
        password_input = request.form.get('password')
        
        # Two-Way Data Cryptography Encrypts Personal Identifiable Information (PII) data fields at rest
        email_encrypted = encrypted_data(email_input) # --> Encrypting the email using encrypted function
        phone_encrypted = encrypted_data(phone_input) # --> Same encryption step for the phone data

        with engine.connect() as conn:
            query = text('select * from users where username = :username')
            result = conn.execute(query,{
                "username": username_input}).fetchone()
            
            if result is not None:
                flash("The username is already taken, try another one!")
                return redirect((url_for('register')))
            
            all_rows = text("select email, phone from users")
            all_rows_result = conn.execute(all_rows).fetchall()

            duplicate_found = False
            
            # Validating decryption values systematically to intercept cloud data redundancy anomalies
            for row in all_rows_result:
                if decrypted_data(row._mapping['email']) == email_input or decrypted_data(row._mapping['phone']) == phone_input:
                    duplicate_found = True
                    break

            if duplicate_found:
                flash("The email or phone is already exist, try new one!")
                return redirect(url_for('register'))    

            print("Adding a new user")
            pass_bytes = password_input.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(pass_bytes, salt)
            stored_password = hashed_password.decode('utf8')

            insert_query = text('''
                            INSERT INTO users(username,email,phone,password) 
                            VALUES
                            (:username,:email,:phone,:password) ''')

            insert_result = conn.execute(insert_query,{
                "username": username_input,
                "email": email_encrypted,
                "phone": phone_encrypted,
                "password": stored_password
            })
            conn.commit()

            return redirect(url_for('login'))

    return render_template('Register.html')


if __name__ == '__main__':
    # application.run(host="0.0.0.0", port=5000)  --> For AWS
    application.run(debug=True)                   # --> for local deployement

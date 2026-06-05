# Task 2: SQL Injection Prevention and Data Encryption System

## 🌟 Project Overview
The main goal of this project is to build a highly secure web application that safely handles user data. It solves two critical security challenges in software development:
1. **Stopping Cyber Attacks (SQL Injection):** Ensuring malicious hackers cannot trick our database into giving away unauthorized access or destroying information.
2. **Protecting Private Data (Encryption & Hashing):** Making sure that sensitive user information (like passwords, emails, and phone numbers) is scrambled and unreadable if anyone ever gains unauthorized access to the storage system.

This system is completely versatile. It runs perfectly on a local computer completely offline for testing, and it is fully configured for a secure enterprise deployment on the Amazon Web Services (AWS) cloud.

---

## 📂 Project Repository Layout
To keep the project clean and organized, the files are structured exactly as follows inside the **`Task 2`** main folder:

* 📁 **`Task_2_Folder/`** *(Main Root Directory)*
  * 📄 **`README.md`** — *This file. An overall professional overview explaining the entire project.*
  * 📄 **`SQL_Injection_Prevention_Tests.md`** — *A document showing the specific test payloads used to prove the application's defense system works.*
  * 📁 **`Flask_App_Folder/`** *(The working application directory)*
    * 📄 **`application.py`** — *The main Python script that drives the backend, handles web routing, and processes data security.*
    * 📄 **`requirements.txt`** — *The list of essential dependencies and libraries needed to run the app.*
    * 📄 **`.env`** — *The local configuration file used to store secret keys safely without revealing them publicly.*
    * 📁 **`templates/`** — *Houses the frontend user interface screens:*
      * 📄 `login.html` (The sign-in page)
      * 📄 `Register.html` (The account creation page)
      * 📄 `index.html` (The secure user home dashboard)

---

## 🛡️ Core Security Concepts (Explained Simply)

### 1. Stopping SQL Injection with Parameterized Queries
* **The Problem:** In standard web applications, when a user types into a login box, the app builds a database command by gluing the user's text directly onto the query. Hackers exploit this by typing special SQL database commands (like `' OR '1'='1`) into the username box to bypass passwords or delete tables.
* **Our Solution:** We use **Parameterized Queries** (also known as Prepared Statements) using SQLAlchemy Core. In our code, we use a colon placeholder (`:username`). This acts like a secure, designated slot. Even if a hacker inputs a complex malicious database command, the system forces the database engine to treat that input strictly as a piece of plain text (a literal username) rather than an instruction. The database looks for a user whose actual name is that long malicious string. Since it doesn't exist, the attack fails completely and safely.

### 2. Advanced Data Encryption at Rest (AES-256 Fernet)
* **The Concept:** When a new user registers an account, we do not save their private contact information in clear text.
* **Our Solution:** We use **AES-256 Cryptography (Fernet)** to protect sensitive data fields like **emails** and **phone numbers**. This is a **two-way functionality**. When data is entered, it is scrambled into an unreadable, random sequence of characters before hitting the database. When an authorized user successfully logs into their dashboard, the system securely reverses the process (decrypts it) back into human language in the computer's memory just for them.

### 3. One-Way Password Hashing (bcrypt)
* **The Concept:** Unlike emails or phone numbers, a user's password should *never* be reversible. Nobody—not even the database administrator—should ever be able to see a user's actual password.
* **Our Solution:** We use **`bcrypt`** for password protection. This is a **one-way functionality**. It takes the password and converts it into a permanent cryptographic string. It can never be decrypted or un-scrambled back into its original form.
* **How Login Works:** Since the password cannot be decrypted, how does a user log back in? When the user types their plain text password on the login page, our system takes that input, applies the exact same hashing math to it, and checks if the new hash matches the permanent hash stored in the database. If they match, entry is granted!

---

## 💻 Local Testing Architecture (SQLite)
For local testing and offline development, the system is configured to use **SQLite via SQLAlchemy Core**. 
* **Why SQLite?** SQLite is a serverless database that stores all data inside a simple local file within your project folder. It requires zero configuration, zero installations, and runs entirely offline.
* **The Execution:** The code checks your local environment configurations, automatically establishes a local database file, and generates the necessary table structures the exact moment you launch the application for the first time.

---

## ☁️ Secure AWS Cloud Deployment Architecture

Once the local development phase was complete, the application was transitioned into a robust, cloud-hosted architecture using **Amazon Web Services (AWS)**. 

### 1. Web Hosting: AWS Elastic Beanstalk
The Flask web application is deployed using **AWS Elastic Beanstalk**, which manages the infrastructure, load balancing, and scaling automatically. To deploy it:
* A production distribution package was generated as a compressed `.zip` file containing only the essential application folders, the HTML `templates`, and the primary application script named `application.py`.
* The **`requirements.txt`** file was automatically generated inside the terminal by executing the command:
  ```
  pip freeze > requirements.txt

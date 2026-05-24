# My First Cloud Project: Automating a Data Guard Gate with AWS

Hey there! Welcome to my repository for my very first task as a **Cloud Computing Intern at CodeAlpha**. 

For this project, I took a common real-world problem—companies getting messy, duplicate customer data sent to them—and built a completely automated cloud system to fix it. 

Instead of sitting at a computer and checking files manually, this system acts like an intelligent, automated gatekeeper. The second a file lands in the cloud, the system wakes up, checks the data, blocks any duplicates, and cleanly saves the unique information.

---

## 🧭 What This Project Solves (The CodeAlpha Tasks)

CodeAlpha challenged me to meet 5 strict goals, and here is exactly how I built the system to handle them in plain English:

1. **Spot and Label Bad Data:** I set up a temporary "Quarantine Room" (a Staging Table) in the database. When a new file arrives, it sits here first so we can inspect it safely before it touches our real business records.
2. **Double-Check Everything:** I wrote a smart database rule that acts like an ID checker. It scans every incoming name, email, and phone number against the customers we already have on file to see if there is a match.
3. **Lock Out Duplicates:** If someone tries to submit an email or phone number that already exists, our ID checker slaps a big "REJECTED" stamp on it. It sends an alert to our cloud dashboard (Amazon CloudWatch) explaining exactly who got blocked and why.
4. **Save Only Verified Data:** If the data is clean and unique, it gets the green light! The system splits the info up and saves it neatly across our permanent filing cabinets.
5. **Keep Storage Clean and Fast:** I put digital locks on our database tables so that identical information can never sneak in and waste expensive cloud storage space.

---

## ☁️ How the Cloud Automation Works

The entire pipeline runs on AWS and works completely on its own without anyone having to click "Run":

* **Amazon S3 (The Drop Box):** This is where someone uploads a new customer file. 
* **AWS Lambda (The Brains):** This is a serverless Python script. It sleeps until a file drops into S3. The exact millisecond a file arrives, it wakes up, reads the data out of the air, securely passes through our cloud firewalls, and runs our database rules.
* **Amazon RDS MySQL (The Vault):** This is our cloud-hosted database that securely holds our final, clean tables.

---

## 📂 What’s Inside This Repository?

Here is a quick map of where everything is and what it does:

* **`aws_lambda/lambda_function.py`** – The main Python automation script that wakes up when a file is uploaded, reads the data, and talks to the database.
* **`database/schema.sql`** – The structural layout definitions for our database. This creates our 9 clean tables and our temporary holding room.
* **`database/stored_procedures.sql`** – The actual programming logic and rules that run the duplicate checks and sort the clean data into the right spots.

---

## 🛠️ How I Built It
I wrote all the code locally on my computer using **VS Code** and used a separate **Python Virtual Environment (venv)** to keep the project files neat. From there, I connected VS Code directly to my live AWS database to test and deploy everything.

Tackling AWS for the very first time was a great learning experience. It showed me how separate cloud tools, network security, and database rules can all team up to solve a big business problem!

*Huge thanks to the CodeAlpha team for pushing me out of my comfort zone with this task.*

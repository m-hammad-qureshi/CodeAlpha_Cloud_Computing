# SQL Injection Vulnerability Test

This document outlines common SQL Injection (SQLi) attack vectors tested against the application, illustrating how vulnerable systems fail versus how our secure parameterized architecture successfully neutralizes each threat.

---

### Test 1: The "Always True" Bypass
**Payload:** `admin' OR '1'='1` 
**Vulnerability Behavior (Failure Case):** A vulnerable application dynamically constructs SQL queries via raw string concatenation (e.g., `WHERE username = 'admin' OR '1'='1'`). Because the conditional statement `'1'='1'` evaluates to true for every single row in the database table, the system bypasses standard authentication checks entirely and logs the attacker into the first available user account without requiring a valid password.
**Mitigation Strategy (Secure Defense):** Our application utilizes SQLAlchemy's **parameterized queries** (`SELECT * FROM users WHERE username = :username`). Because of this structural binding, the database engine treats the entire injection payload (`admin' OR '1'='1`) strictly as a single, literal username string variable. It searches the database for a user whose literal username value matches the exact string `admin' OR '1'='1`. Since no such user account exists, the query safely evaluates to `None` and triggers the handled `"The user does not exist."` flash notification.

---

### Test 2: The Inline Comment Attack
**Payload:** `admin' --` 
**Vulnerability Behavior (Failure Case):** In an unshielded or poorly structured code environment, string concatenation allows malicious input to alter query logic. The standard SQL comment sequence (`--`) completely comments out the remainder of the database execution line, entirely erasing the secondary password verification step and granting the attacker entry using only a known username.
**Mitigation Strategy (Secure Defense):** Thanks to the parameterized binding structure deployed in the backend code, the `--` characters completely lose their operational SQL meaning. The database engine automatically escapes the characters implicitly, treating the payload as data and executing a literal text search for a string matching `admin' --`.

---

### Test 3: Stacked Query Data Deletion
* **Payload:** `testuser'; DROP TABLE users; --` 
**Vulnerability Behavior (Failure Case):** When raw database queries are dynamically compiled via string concatenation, a semicolon character (`;`) acts as an explicit instruction delimiter marking the complete ending of the first command. This structural vulnerability allows the database engine to immediately execute a completely separate, secondary stacked command (such as `DROP TABLE users;`), instantly destroying backend data storage architectures.
**Mitigation Strategy (Secure Defense):** Our architecture completely walls off and neutralizes stacked query insertion attempts. The parameter binder safely isolates the input data, forcing the database engine to wrap the semicolon wrapper and structural modification commands directly into an immutable string variable value block. Because the engine treats the input strictly as text parameters rather than executable logic, the malicious sequence never gets evaluated or executed as code, keeping database tables completely safe from deletion.

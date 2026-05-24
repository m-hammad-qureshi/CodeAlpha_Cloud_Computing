-- =============================================================================
-- PROCEDURE 1: THE FILTER (classify_validate_data)
-- This checks all the incoming raw data for duplicates before approving it.
-- =============================================================================
DELIMITER $$
CREATE PROCEDURE classify_validate_data()
BEGIN 

-- 1. Look inside the new file itself and check for internal repeated names
WITH duplicate_ids AS (
    SELECT 
        *, ROW_NUMBER() OVER(PARTITION BY customer_name, gender, date_of_birth ORDER BY CASE WHEN email_type = 'Personal' THEN 1 ELSE 2 END) AS rn
    FROM staging
)
UPDATE staging AS st
    JOIN duplicate_ids AS di 
        ON st.id = di.id 
        AND st.customer_name = di.customer_name
        AND st.date_of_birth = di.date_of_birth
        AND st.email = di.email
    SET st.verification_status = 'duplicate entry: internal file repeat'
    WHERE di.rn > 1;

-- 2. Check if the email address is already owned by someone in the production database
UPDATE staging AS st
JOIN email AS e ON e.email = st.email
SET verification_status = 'duplicate entry: email already exists in production';

-- 3. Check if the phone number is already owned by someone in the production database
UPDATE staging AS st
JOIN phone AS p ON p.phone_number = st.phone 
SET verification_status = 'duplicate entry: phone/email already exists in production'
WHERE verification_status = 'duplicate entry: email already exists in production';

-- 4. If an entry passes all the checks without being flagged, mark it as approved
UPDATE staging
SET verification_status = 'verified unique'
WHERE verification_status = 'Pending';

END $$
DELIMITER ;


-- =============================================================================
-- PROCEDURE 2: THE SORTER (update_delete_data)
-- This takes the approved unique records and neatly sorts them into the system.
-- =============================================================================
DELIMITER $$
CREATE PROCEDURE update_delete_data()
BEGIN

-- 1. Save new labels for emails, phones, and addresses if they don't exist yet
INSERT IGNORE INTO contact_type(contact_type)
SELECT email_type FROM staging;

INSERT IGNORE INTO contact_type(contact_type)
SELECT phone_type FROM staging;

INSERT IGNORE INTO contact_type(contact_type)
SELECT address_type FROM staging;

-- 2. Add only the approved new customer names to the master list
INSERT IGNORE INTO customers(customer_name, gender, date_of_birth)
SELECT customer_name, gender, date_of_birth
FROM staging 
WHERE verification_status = 'verified unique';

-- 3. Add approved unique emails to the email vault
INSERT IGNORE INTO email(email, contact_type_id)
SELECT email, ct.contact_type_id
FROM staging AS s
JOIN contact_type AS ct ON s.email_type = ct.contact_type
WHERE verification_status = 'verified unique';

-- 4. Add approved unique phone numbers to the phone vault
INSERT IGNORE INTO phone(phone_number, contact_type_id) 
SELECT phone, ct.contact_type_id
FROM staging AS s
JOIN contact_type AS ct ON s.phone_type = ct.contact_type
WHERE verification_status = 'verified unique';

-- 5. Add approved unique locations to the address vault
INSERT IGNORE INTO address(city, state, country, contact_type_id)
SELECT DISTINCT city, state, country, ct.contact_type_id
FROM staging AS s 
JOIN contact_type AS ct ON s.address_type = ct.contact_type
WHERE verification_status = 'verified unique';

-- 6. Link the customer names to their new unique emails
INSERT IGNORE INTO customer_email(customer_id, email_id, is_primary)
SELECT ct.customer_id, e.email_id, CASE WHEN s.email_type = 'Personal' THEN 'Y' ELSE 'N' END AS is_primary
FROM staging AS s
JOIN customers AS ct ON 
    s.customer_name = ct.customer_name 
    AND s.gender = ct.gender 
    AND s.date_of_birth = ct.date_of_birth
JOIN email AS e ON s.email = e.email;

-- 7. Link the customer names to their new unique phone numbers
INSERT IGNORE INTO customer_phone(customer_id, phone_id, is_primary)
SELECT ct.customer_id, p.phone_id, CASE WHEN s.phone_type = 'Mobile' THEN 'Y' ELSE 'N' END AS is_primary
FROM staging AS s
JOIN customers AS ct ON 
    s.customer_name = ct.customer_name 
    AND s.gender = ct.gender 
    AND s.date_of_birth = ct.date_of_birth
JOIN phone AS p ON s.phone = p.phone_number;

-- 8. Link the customer names to their new unique physical addresses
INSERT IGNORE INTO customer_address(customer_id, address_id, is_primary)
SELECT ct.customer_id, a.address_id, CASE WHEN s.address_type = 'Home' THEN 'Y' ELSE 'N' END AS is_primary
FROM staging AS s
JOIN customers AS ct ON 
    s.customer_name = ct.customer_name 
    AND s.gender = ct.gender 
    AND s.date_of_birth = ct.date_of_birth
JOIN address AS a ON s.city = a.city AND s.state = a.state AND s.country = a.country;

END $$
DELIMITER ;

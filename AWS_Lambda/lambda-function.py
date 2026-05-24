"""
Description:
    An event-driven AWS Lambda function designed to orchestrate serverless data 
    processing pipelines. Triggered automatically by Amazon S3 object creation 
    events, this script streams raw CSV file content directly from S3 memory, 
    populates a relational RDS MySQL staging layer, and executes backend stored 
    procedures to identify, log, and prevent duplicate data injection.

Security & Environment Constraints:
    - Database authentication parameters are injected securely via Lambda Environment Variables.
    - Network ingress control is governed by AWS EC2 Security Groups.
    - Execution utilizes explicit batch transaction controls (Commit/Rollback isolation).
"""

import os
import csv
import boto3
import pymysql

# -----------------------------------------------------------------------------
# START-UP: This wakes up the AWS Cloud connection tool.
# -----------------------------------------------------------------------------
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    print("Received S3 trigger event. Initializing data extraction pipeline.")
    
    # =========================================================================
    # STEP 1: THE ALARM CLOCK (S3 TRIGGER)
    # The exact moment a file is dropped into our storage bucket, an alarm goes 
    # off telling this script exactly which file it needs to go grab.
    # =========================================================================
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        print(f"Targeting Bucket: {bucket_name} | Processing File: {file_key}")
    except KeyError as e:
        print(f"Critical Error: Failed parsing S3 metadata layout. Details: {str(e)}")
        return {'statusCode': 400, 'body': 'Invalid S3 event trigger format.'}
        
    # =========================================================================
    # STEP 2: GRABBING THE KEYS (DATABASE CREDENTIALS)
    # The script securely grabs the secret keys (username and password) out of its
    # pocket so it can unlock and enter the main database storage room later.
    # =========================================================================
    db_host = os.environ.get('DB_HOST')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = 'internship_db'
    
    # =========================================================================
    # STEP 3: READING THE FILE (IN-MEMORY STREAMING)
    # Instead of printing the file onto a slow physical disk, the script reads 
    # the data instantly out of the air to keep the system fast.
    # =========================================================================
    try:
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        csv_file_content = s3_response['Body'].read().decode('utf-8').splitlines()
        print("CSV data stream successfully fetched and decoded from S3.")
    except Exception as e:
        print(f"Critical Error: Failed to extract data stream from S3: {str(e)}")
        return {'statusCode': 500, 'body': 'S3 data extraction failed.'}
        
    # =========================================================================
    # STEP 4: WALKING THROUGH THE SECURITY GATE
    # The script uses the keys from Step 2 to walk past the cloud firewalls and
    # safely connect to the remote database room.
    # =========================================================================
    connection = None
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            autocommit=False, # Wait until everything is perfect before saving!
            connect_timeout=15
        )
        
        with connection.cursor() as cursor:
            # =========================================================================
            # STEP 5: CLEANING THE HOLDING ROOM (TRUNCATE STAGING)
            # Before looking at new data, we sweep out all the old trash left over in 
            # our temporary holding area so things don't get mixed up.
            # =========================================================================
            print("Clearing staging environment...")
            cursor.execute("TRUNCATE TABLE staging;")
            
            # Read the CSV rows row-by-row
            csv_reader = csv.DictReader(csv_file_content)
            row_count = 0
            
            # A template to load the raw data rows into our holding zone
            insert_staging_sql = """
            INSERT INTO staging (
                customer_name, gender, date_of_birth, email, email_type, 
                phone, phone_type, city, state, country, address_type, verification_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending');
            """
            
            print("Streaming raw data into SQL staging buffer...")
            for row in csv_reader:
                cursor.execute(insert_staging_sql, (
                    row['customer_name'], row['gender'], row['date_of_birth'],
                    row['email'], row['email_type'], row['phone'], row['phone_type'],
                    row['city'], row['state'], row['country'], row['address_type']
                ))
                row_count += 1
                
            print(f"Staging complete. Ingested {row_count} raw rows. Launching database logic...")
            
            # =========================================================================
            # STEP 6: THE SECURITY GUARD ID CHECK (VALIDATION PROCEDURE)
            # [CodeAlpha Task: Identify & Classify Redundancy / Prevent Duplicates]
            # A database rule walks down the line of new entries in the holding room 
            # and cross-checks emails/phones to see if they already exist in the system.
            # =========================================================================
            print("Running stored procedure: classify_validate_data()...")
            cursor.callproc('classify_validate_data')
            
            # =========================================================================
            # STEP 7: SORTING INTO FINAL STORAGE CABINETS (DISTRIBUTION PROCEDURE)
            # [CodeAlpha Task: Append Only Unique Data / Avoid Redundancy]
            # If the data passes the guard, it gets the green light! The system splits
            # the clean data and files it across 9 neatly organized final tables.
            # =========================================================================
            print("Running stored procedure: update_delete_data()...")
            cursor.callproc('update_delete_data')
            
            # =========================================================================
            # STEP 8: THE BLACKLIST ACCOUNTING & LOGGING (AUDITING)
            # The script scans our holding room to find anyone flagged as a duplicate. 
            # It prints a loud alert to our dashboard showing exactly who was blocked.
            # =========================================================================
            audit_sql = "SELECT customer_name, email, verification_status FROM staging WHERE verification_status != 'verified unique';"
            cursor.execute(audit_sql)
            rejected_rows = cursor.fetchall()
            
            if rejected_rows:
                print(f"⚠️ DETECTION: {len(rejected_rows)} rows were rejected by the database logic.")
                for rejected in rejected_rows:
                    print(f" -> REJECTED: Customer '{rejected[0]}' ({rejected[1]}) | Reason: {rejected[2]}")
            else:
                print("🎉 CLEAN PASS: 100% of rows were successfully verified and processed!")

            # =========================================================================
            # STEP 9: LOCKING THE VAULT (TRANSACTION COMMIT)
            # If every single check passed and no errors occurred, we lock the vault 
            # and save all the changes permanently to the database.
            # =========================================================================
            connection.commit()
            print("Database transaction successfully committed across all 9 tables.")
            
        return {
            'statusCode': 200,
            'body': f'Successfully automated pipeline logic for {row_count} records.'
        }
        
    except pymysql.MySQLError as db_error:
        # =========================================================================
        # STEP 10: HIT THE EMERGENCY BRAKE (TRANSACTION ROLLBACK)
        # If a single computer glitch or error happens anywhere during this process, 
        # the system automatically undoes all its work so nothing gets messed up.
        # =========================================================================
        if connection:
            connection.rollback()
            print("Database transaction rolled back due to execution failure.")
        print(f"Critical Database Driver Error: {str(db_error)}")
        return {'statusCode': 500, 'body': 'Database pipeline execution failure.'}
        
    finally:
        # Securely close the connection room door when done
        if connection and connection.open:
            connection.close()
            print("Database channel safely closed.")

# =============================================================================
# LOCAL EMULATION ZONE (FOR LOCAL TESTING ONLY)
# This is a mock setup to test the script on your personal computer first.
# =============================================================================
if __name__ == "__main__":
    mock_s3_event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "your-landing-zone-bucket-name"},
                "object": {"key": "customers_day1.csv"}
            }
        }]
    }
    print("--- Local Debug Test Started ---")
    print("Note: To run this locally, ensure your .env variables or local environment variables match your AWS RDS credentials.")
    # lambda_handler(mock_s3_event, None)

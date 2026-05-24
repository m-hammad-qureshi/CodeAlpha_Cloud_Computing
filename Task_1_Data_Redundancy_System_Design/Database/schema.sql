-- =============================================================================
-- START: Set up the main database container
-- =============================================================================
CREATE DATABASE IF NOT EXISTS internship_db;
USE internship_db;

-- TABLE 1: List of customers (Names and birthdays)
CREATE TABLE customers(
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    date_of_birth DATE
);

-- TABLE 2: Labels for contact types (Like 'Home', 'Work', or 'Office')
CREATE TABLE contact_type (
    contact_type_id INT PRIMARY KEY AUTO_INCREMENT,
    contact_type VARCHAR(100) NOT NULL UNIQUE
);

-- TABLE 3: List of unique emails (No duplicates allowed)
CREATE TABLE email(
    email_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    contact_type_id INT NOT NULL,
    CONSTRAINT fk_e_contact_type FOREIGN KEY (contact_type_id) REFERENCES contact_type(contact_type_id)
);

-- TABLE 4: Links customers to their specific emails
CREATE TABLE customer_email(
    customer_email_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    email_id INT NOT NULL UNIQUE,
    is_primary ENUM('Y', 'N') NOT NULL DEFAULT 'N',
    CONSTRAINT fk_ce_customers FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_ce_email FOREIGN KEY (email_id) REFERENCES email(email_id)
);

-- TABLE 5: List of unique phone numbers (No duplicates allowed)
CREATE TABLE phone (
    phone_id INT PRIMARY KEY AUTO_INCREMENT,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    contact_type_id INT NOT NULL,
    CONSTRAINT fk_ph_contact_type FOREIGN KEY (contact_type_id) REFERENCES contact_type(contact_type_id)
);

-- TABLE 6: Links customers to their specific phone numbers
CREATE TABLE customer_phone (
    customer_phone_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    phone_id INT NOT NULL UNIQUE,
    is_primary ENUM('Y', 'N') NOT NULL DEFAULT 'N',
    CONSTRAINT fk_cp_customers FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_cp_phone FOREIGN KEY (phone_id) REFERENCES phone(phone_id)
);

-- TABLE 7: List of unique physical locations (City, State, Country combos)
CREATE TABLE address (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    contact_type_id INT NOT NULL,
    CONSTRAINT fk_a_contact_type FOREIGN KEY (contact_type_id) REFERENCES contact_type(contact_type_id),
    CONSTRAINT uq_address UNIQUE(city, state, country)
);

-- TABLE 8: Links customers to their home or work addresses
CREATE TABLE customer_address (
    customer_address_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    address_id INT NOT NULL,
    is_primary ENUM('Y', 'N') NOT NULL DEFAULT 'N',
    CONSTRAINT fk_ca_customers FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_ca_address FOREIGN KEY (address_id) REFERENCES address(address_id),
    CONSTRAINT uq_customer_address UNIQUE(customer_id, address_id)
);

-- TABLE 9: THE QUARANTINE ROOM (Where raw file data lands first)
-- This is where the AWS system drops new data before checking it for duplicates.
CREATE TABLE IF NOT EXISTS staging (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100),
    gender VARCHAR(20),
    date_of_birth DATE,
    email VARCHAR(50),
    email_type VARCHAR(20),
    phone VARCHAR(20),
    phone_type VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    address_type VARCHAR(20),
    verification_status VARCHAR(100) DEFAULT 'Pending'
);

-- County Pre-Foreclosure System Database Schema
-- Created: 2025

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS email_log;
DROP TABLE IF EXISTS received_files;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS payment_info;
DROP TABLE IF EXISTS counties;

-- Counties Table (Main table)
CREATE TABLE counties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    county_name VARCHAR(255) NOT NULL UNIQUE,
    state VARCHAR(50) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    contact_person VARCHAR(255),
    status ENUM('active', 'inactive') DEFAULT 'active',
    notes TEXT,
    last_request_sent DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_state (state)
);

-- Payment Information Table
CREATE TABLE payment_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    county_id INT NOT NULL,
    payment_instructions TEXT,
    amount DECIMAL(10, 2),
    payment_method VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE CASCADE
);

-- Addresses Table (Stores extracted addresses)
CREATE TABLE addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    address TEXT NOT NULL,
    county_id INT NOT NULL,
    source_file VARCHAR(255),
    source_type ENUM('excel', 'pdf', 'image', 'manual') DEFAULT 'manual',
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE CASCADE,
    INDEX idx_is_sent (is_sent),
    INDEX idx_county_id (county_id),
    INDEX idx_created_at (created_at)
);

-- Email Log Table (Track all outgoing/incoming emails)
CREATE TABLE email_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    county_id INT,
    email_type ENUM('request', 'data_send', 'response') NOT NULL,
    recipient VARCHAR(255),
    subject VARCHAR(500),
    body TEXT,
    status ENUM('sent', 'failed', 'pending') DEFAULT 'pending',
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE SET NULL,
    INDEX idx_county_id (county_id),
    INDEX idx_email_type (email_type),
    INDEX idx_status (status)
);

-- Received Files Table (Track incoming files from counties)
CREATE TABLE received_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    county_id INT,
    filename VARCHAR(255) NOT NULL,
    file_type ENUM('excel', 'pdf', 'image', 'other') NOT NULL,
    file_path VARCHAR(500),
    file_size_kb INT,
    processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    addresses_extracted INT DEFAULT 0,
    error_message TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME NULL,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE CASCADE,
    INDEX idx_county_id (county_id),
    INDEX idx_processing_status (processing_status)
);

-- Insert some sample data for testing
INSERT INTO counties (county_name, state, phone, email, contact_person, status) VALUES
('Los Angeles County', 'California', '(213) 555-0100', 'records@lacounty.gov', 'John Smith', 'active'),
('Cook County', 'Illinois', '(312) 555-0200', 'clerk@cookcounty.gov', 'Jane Doe', 'active'),
('Harris County', 'Texas', '(713) 555-0300', 'info@harriscounty.gov', 'Mike Johnson', 'active'),
('Maricopa County', 'Arizona', '(602) 555-0400', 'records@maricopa.gov', 'Sarah Williams', 'inactive'),
('San Diego County', 'California', '(619) 555-0500', 'clerk@sdcounty.gov', 'Tom Brown', 'active');

-- Insert sample payment info
INSERT INTO payment_info (county_id, payment_instructions, amount, payment_method, notes) VALUES
(1, 'Send check to: LA County Clerk, 12400 E Imperial Hwy, Norwalk, CA 90650', 25.00, 'Check', 'Processing time: 5-7 business days'),
(2, 'Online payment available at cookcounty.gov/payments', 15.00, 'Online', 'Instant processing'),
(3, 'Money order payable to Harris County Clerk', 20.00, 'Money Order', 'Include reference number');

-- Insert sample email logs
INSERT INTO email_log (county_id, email_type, recipient, subject, status, sent_at) VALUES
(1, 'request', 'records@lacounty.gov', 'Pre-Foreclosure Property List Request - Los Angeles County', 'sent', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(2, 'request', 'clerk@cookcounty.gov', 'Pre-Foreclosure Property List Request - Cook County', 'sent', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(3, 'request', 'info@harriscounty.gov', 'Pre-Foreclosure Property List Request - Harris County', 'failed', DATE_SUB(NOW(), INTERVAL 3 DAY));

-- Update last_request_sent based on email_log
UPDATE counties c
SET last_request_sent = (
    SELECT MAX(sent_at)
    FROM email_log
    WHERE county_id = c.id AND email_type = 'request' AND status = 'sent'
);

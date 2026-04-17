-- MySQL Root Password Reset
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'county@123';
FLUSH PRIVILEGES;
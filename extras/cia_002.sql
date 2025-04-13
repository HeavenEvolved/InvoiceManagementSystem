create database cia_002;
-- drop database cia_002;
use cia_002;
-- Master Tables

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name CHAR(20) NOT NULL UNIQUE
);

insert into roles (role_name)
values
	("superadmin"),
    ("customer_admin"),
    ("vendor_admin"),
    ("customer"),
    ("vendor");

-- -- Status Table
CREATE TABLE statuses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status_name ENUM('paid', 'unpaid', 'overdue') NOT NULL UNIQUE
);

insert into statuses (status_name) values ('paid'), ('unpaid'), ('overdue');

CREATE TABLE cart_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status_name ENUM('active', 'converted') NOT NULL UNIQUE
);

insert into cart_status (status_name) values ('active'), ('converted');

-- Transaction Tables

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE CHECK (email LIKE '%_@__%.__%'),
    phone VARCHAR(15) NOT NULL UNIQUE CHECK (phone REGEXP '^[0-9]{10,15}$'),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    role_id INT DEFAULT 4 NOT NULL,
    created_by INT NOT NULL,
    updated_by INT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id)
        REFERENCES roles (id),
    FOREIGN KEY (created_by)
        REFERENCES users (id),
    FOREIGN KEY (updated_by)
        REFERENCES users (id)
);

-- -- Items Table
CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    price DECIMAL(10 , 2 ) NOT NULL,
    stock INT NOT NULL,
    created_by INT NOT NULL,
    updated_by INT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id)
        REFERENCES users (id),
    FOREIGN KEY (created_by)
        REFERENCES users (id),
    FOREIGN KEY (updated_by)
        REFERENCES users (id)
);

-- -- Invoices Table
CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    status_id INT NOT NULL,
    invoice_date DATE NOT NULL,
    total_amount DECIMAL(10 , 2 ) NOT NULL,
    created_by INT NOT NULL,
    updated_by INT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id)
        REFERENCES users (id),
    FOREIGN KEY (status_id)
        REFERENCES statuses (id),
    FOREIGN KEY (created_by)
        REFERENCES users (id),
    FOREIGN KEY (updated_by)
        REFERENCES users (id)
);

-- -- Invoice Items Table
CREATE TABLE invoice_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10 , 2 ) NOT NULL,
    created_by INT NOT NULL,
    updated_by INT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id)
        REFERENCES invoices (id),
    FOREIGN KEY (item_id)
        REFERENCES items (id),
    FOREIGN KEY (created_by)
        REFERENCES users (id),
    FOREIGN KEY (updated_by)
        REFERENCES users (id)
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    status_id INT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES users (id),
    FOREIGN KEY (item_id)
        REFERENCES items (id),
    FOREIGN KEY (status_id)
        REFERENCES cart_status (id)
);

SELECT 
    *
FROM
    roles;
SELECT 
    *
FROM
    invoices;
    
insert into users (username, password_hash, email, phone, first_name, last_name, created_by, updated_by, role_id)
values
("superadmin", "$2b$12$FDOGkd.ea5Ssa4ExVdK1qOyE2OJj3bYtyooo59XiEaI06eA9e.wNe", "superadmin@xyz.com", "1234567890", "Super", "Admin", 1, 1, 1);
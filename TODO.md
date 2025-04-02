# TODO List for Invoice Management System

## 1. Database Setup (MySQL)

- [x] **DB-001**: Create a MySQL database for the system.
- [x] **DB-002**: Design tables for the following entities:

  - **Roles**: Master table for user roles.

    ```sql
    create table roles (
        id int auto_increment primary key,
        role_name enum('superadmin', 'customer admin', 'vendor admin', 'customer', 'vendor') not null unique
    );
    ```

  - **Statuses**: Master table for invoice statuses.

    ```sql
    create table statuses (
        id int auto_increment primary key,
        status_name enum('paid', 'unpaid', 'overdue') not null unique
    );
    ```

  - **Users**: To store user credentials and roles.

    ```sql
    create table users (
        id int auto_increment primary key,
        username varchar(50) not null unique,
        password_hash varchar(255) not null,
        email varchar(100) not null unique check (email like '%_@__%.__%'),
        phone varchar(15) not null unique check (phone regexp '^[0-9]{10,15}$'),
        first_name varchar(50) not null,
        last_name varchar(50) not null,
        is_active boolean not null default true,
        last_login timestamp null,
        role_id int not null,
        created_by int not null,
        updated_by int not null,
        created_on timestamp default current_timestamp,
        updated_on timestamp default current_timestamp on update current_timestamp,
        foreign key (role_id) references roles(id),
        foreign key (created_by) references users(id),
        foreign key (updated_by) references users(id)
    );
    ```

  - **Items**: To store listed items.

    ```sql
    create table items (
        id int auto_increment primary key,
        vendor_id int not null,
        description varchar(255) not null unique,
        price decimal(10, 2) not null,
        stock int not null,
        created_by int not null,
        updated_by int not null,
        created_on timestamp default current_timestamp,
        updated_on timestamp default current_timestamp on update current_timestamp,
        foreign key (vendor_id) references users(id),
        foreign key (created_by) references users(id),
        foreign key (updated_by) references users(id)
    );
    ```

  - **Invoices**: To store invoice details.

    ```sql
    create table invoices (
        id int auto_increment primary key,
        customer_id int not null,
        status_id int not null,
        invoice_date date not null,
        total_amount decimal(10, 2) not null,
        created_by int not null,
        updated_by int not null,
        created_on timestamp default current_timestamp,
        updated_on timestamp default current_timestamp on update current_timestamp,
        foreign key (customer_id) references users(id),
        foreign key (status_id) references statuses(id),
        foreign key (created_by) references users(id),
        foreign key (updated_by) references users(id)
    );
    ```

  - **Invoice_Items**: To store individual items in an invoice.

    ```sql
    create table invoice_items (
        id int auto_increment primary key,
        invoice_id int not null,
        item_id int not null,
        quantity int not null,
        total_price decimal(10, 2) not null,
        created_by int not null,
        updated_by int not null,
        created_on timestamp default current_timestamp,
        updated_on timestamp default current_timestamp on update current_timestamp,
        foreign key (invoice_id) references invoices(id),
        foreign key (item_id) references items(id),
        foreign key (created_by) references users(id),
        foreign key (updated_by) references users(id)
    );
    ```

## 2. Backend Logic (Python)

- [ ] **BE-001**: Set up a Python environment and install necessary libraries (`mysql-connector-python`, `streamlit`, etc.).
- [ ] **BE-002**: Create a database connection utility.

  ```python
  # db_connection.py
  import mysql.connector

  def get_connection():
      return mysql.connector.connect(
          host="localhost",
          user="your_username",
          password="your_password",
          database="invoice_management"
      )
  ```

- [ ] **BE-003**: Implement CRUD operations for each table:
  - Add, update, delete, and fetch users.
  - Add, update, delete, and fetch clients.
  - Add, update, delete, and fetch invoices and their items.
  - Add, update, delete, and fetch roles, statuses, and items.

## 3. Frontend Implementation (Streamlit)

- [ ] **FE-001**: Create a Streamlit app structure.

  ```python
  import streamlit as st

  st.sidebar.title("Invoice Management System")
  menu = st.sidebar.radio("Navigation", ["Dashboard", "Clients", "Invoices"])
  ```

- [ ] **FE-002**: Implement the **Dashboard**:
  - Display summary statistics (e.g., total invoices, total revenue).
  - Use Streamlit charts for visualizations.

- [ ] **FE-003**: Implement the **Clients** section:
  - Form to add/edit client details.
  - Table to display all clients with options to edit or delete.

- [ ] **FE-004**: Implement the **Invoices** section:
  - Form to create/edit invoices and add items.
  - Table to display all invoices with options to view, edit, or delete.

    ```python
    if menu == "Invoices":
        st.title("Invoices")
        # Add logic to display and manage invoices
    ```

## 4. Additional Features

- [ ] **AF-001**: Add user authentication (e.g., login/logout functionality).
- [ ] **AF-002**: Implement search and filter functionality for clients and invoices.
- [ ] **AF-003**: Generate PDF for invoices using a library like `reportlab` or `fpdf`.
- [ ] **AF-004**: Add email functionality to send invoices to clients.

## 5. Testing and Deployment

- [ ] **TD-001**: Write unit tests for backend logic.
- [ ] **TD-002**: Test the Streamlit app for usability and bugs.
- [ ] **TD-003**: Deploy the app using a platform like Heroku or Streamlit Cloud.

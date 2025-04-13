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

  - **Cart**: To manage user carts.

- [x] **DB-003**: Add constraints and relationships between tables.
- [x] **DB-004**: Add sample data for roles and a superadmin user.

## 2. Backend Logic (Python)

- [x] **BE-001**: Set up a Python environment and install necessary libraries (`mysql-connector-python`, `streamlit`, `bcrypt`, etc.).
- [x] **BE-002**: Create a database manager class for executing queries.

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

- [x] **BE-003**: Implement CRUD operations for:
  - Users
  - Items
  - Invoices and their items
  - Cart management
- [x] **BE-004**: Add functionality to generate unique invoice numbers.
- [x] **BE-005**: Add functionality to update stock when invoices are generated.
- [x] **BE-006**: Add password hashing and verification using `bcrypt`.

## 3. Frontend Implementation (Streamlit)

- [x] **FE-001**: Create a Streamlit app structure with sidebar navigation.

  ```python
  import streamlit as st

  st.sidebar.title("Invoice Management System")
  menu = st.sidebar.radio("Navigation", ["Dashboard", "Clients", "Invoices", "Manage Users", "Manage Items", "Manage Cart", "Manage Profile"])
  ```

- [x] **FE-002**: Implement the **Dashboard**:
  - Display a welcome message based on the user role.
  - Display summary statistics (e.g., total invoices, total revenue).
  - Use Streamlit charts for visualizations.

- [x] **FE-003**: Implement the **Manage Users** section:
  - Add, edit, and deactivate users.
  - Display a table of all users.

- [x] **FE-004**: Implement the **Manage Items** section:
  - Add new items with vendor selection (for superadmins).
  - Update stock for existing items.
  - Display a table of all items.

- [x] **FE-005**: Implement the **Manage Invoices** section:
  - Display a table of invoices based on user role.
  - Generate PDF invoices with vendor details for each item.
  - Mark invoices as paid.

- [x] **FE-006**: Implement the **Manage Cart** section:
  - Add items to the cart.
  - Display cart contents with total amount.
  - Generate invoices from the cart.

- [x] **FE-007**: Implement the **Manage Profile** section:
  - Update user profile details.

- [x] **FE-008**: Implement the **Customer Registration** form.

## 4. Additional Features

- [x] **AF-001**: Add user authentication with hashed passwords.
- [x] **AF-002**: Generate PDF invoices using `fpdf`.
- [x] **AF-003**: Add vendor information to invoice PDFs.
- [x] **AF-004**: Add functionality to handle inactive users.

## 5. Testing and Deployment

- [ ] **TD-001**: Test database queries for correctness.
- [ ] **TD-002**: Test Streamlit app for usability and bugs.
- [ ] **TD-003**: Deploy the app using a platform like Streamlit Cloud or Heroku.

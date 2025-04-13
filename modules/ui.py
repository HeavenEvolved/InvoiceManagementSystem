import streamlit as st
import pandas as pd
import os
from utils import pdf_generator

def display_dashboard(db_manager_instance, user_id, user_role):
    st.subheader("Dashboard")
    st.write(f"Welcome to the Dashboard, {user_role.capitalize()}!")
    # Add relevant dashboard content here (e.g., statistics, summaries, etc.)

def display_manage_users(db_manager_instance, user_id, user_role):
    st.subheader("Manage Users")
    if user_role in ["superadmin", "customer_admin", "vendor_admin"]:
        query = """
            SELECT id, username, email, phone, first_name, last_name, role_id, is_active, created_on, updated_on
            FROM users
        """
        users = db_manager_instance.execute_query(query, fetch='all')

        if users:
            user_df = pd.DataFrame(
                users,
                columns=["ID", "Username", "Email", "Phone", "First Name", "Last Name", "Role ID", "Active", "Created On", "Updated On"]
            )
            st.dataframe(user_df, use_container_width=True)
        else:
            st.info("No users found.")

        st.write("---")

        # Add a new user
        st.write("### Add New User")
        with st.form("add_user_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            role_id = st.selectbox("Role", options=[1, 2, 3, 4, 5], format_func=lambda x: ["Superadmin", "Customer Admin", "Vendor Admin", "Customer", "Vendor"][x - 1])
            is_active = st.checkbox("Active", value=True)
            if st.form_submit_button("Add User"):
                import bcrypt
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                add_user_query = """
                    INSERT INTO users (username, password_hash, email, phone, first_name, last_name, role_id, is_active, created_by, updated_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (username, hashed_password, email, phone, first_name, last_name, role_id, is_active, user_id, user_id)
                if db_manager_instance.execute_query(add_user_query, params):
                    st.success(f"User '{username}' added successfully.")
                else:
                    st.error(f"Failed to add user '{username}'.")

        st.write("---")

        # Edit or deactivate a user
        st.write("### Edit or Deactivate User")
        user_options = {f"{user[1]} (ID: {user[0]})": user[0] for user in users}
        selected_user = st.selectbox("Select a User to Edit", options=list(user_options.keys()))

        if selected_user:
            user_id_to_edit = user_options[selected_user]
            user_info_query = "select username, email, phone, first_name, last_name, role_id, is_active from users where id = %s"
            user_info = db_manager_instance.execute_query(user_info_query, (user_id_to_edit,), fetch='one')

            if user_info:
                username, email, phone, first_name, last_name, role_id, is_active = user_info
                with st.form("edit_user_form"):
                    new_email = st.text_input("Email", value=email)
                    new_phone = st.text_input("Phone", value=phone)
                    new_first_name = st.text_input("First Name", value=first_name)
                    new_last_name = st.text_input("Last Name", value=last_name)
                    new_role_id = st.selectbox("Role", options=[1, 2, 3, 4, 5], index=role_id - 1, format_func=lambda x: ["Superadmin", "Customer Admin", "Vendor Admin", "Customer", "Vendor"][x - 1])
                    new_is_active = st.checkbox("Active", value=is_active)
                    if st.form_submit_button("Update User"):
                        update_user_query = """
                            update users
                            set email = %s, phone = %s, first_name = %s, last_name = %s, role_id = %s, is_active = %s, updated_by = %s, updated_on = now()
                            where id = %s
                        """
                        params = (new_email, new_phone, new_first_name, new_last_name, new_role_id, new_is_active, user_id, user_id_to_edit)
                        if db_manager_instance.execute_query(update_user_query, params):
                            st.success(f"User '{username}' updated successfully.")
                        else:
                            st.error(f"Failed to update user '{username}'.")
    else:
        st.error("You do not have permission to access this section.")

def display_manage_invoices(db_manager_instance, user_id, user_role):
    st.subheader("Manage Invoices")
    query = {
        "superadmin": """
            SELECT i.invoice_number, i.customer_id, s.status_name, i.invoice_date, i.total_amount, i.created_by, i.updated_by, i.created_on, i.updated_on
            FROM invoices i
            JOIN statuses s ON i.status_id = s.id
        """,
        "customer_admin": """
            SELECT i.invoice_number, i.customer_id, s.status_name, i.invoice_date, i.total_amount, i.created_by, i.updated_by, i.created_on, i.updated_on
            FROM invoices i
            JOIN statuses s ON i.status_id = s.id
        """,
        "vendor_admin": """
            SELECT i.invoice_number, i.customer_id, s.status_name, i.invoice_date, i.total_amount, i.created_by, i.updated_by, i.created_on, i.updated_on
            FROM invoices i
            JOIN statuses s ON i.status_id = s.id
        """,
        "customer": """
            SELECT i.invoice_number, i.customer_id, s.status_name, i.invoice_date, i.total_amount, i.created_by, i.updated_by, i.created_on, i.updated_on
            FROM invoices i
            JOIN statuses s ON i.status_id = s.id
            WHERE i.customer_id = %s
        """,
        "vendor": """
            SELECT DISTINCT i.invoice_number, i.customer_id, s.status_name, i.invoice_date, i.total_amount, i.created_by, i.updated_by, i.created_on, i.updated_on
            FROM invoices i
            JOIN statuses s ON i.status_id = s.id
            JOIN invoice_items ii ON i.id = ii.invoice_id
            JOIN items it ON ii.item_id = it.id
            WHERE it.vendor_id = %s
        """
    }.get(user_role)
    params = (user_id,) if user_role in ["customer", "vendor"] else None
    invoices = db_manager_instance.execute_query(query, params, fetch='all')

    if invoices:
        # Update the column names to include "Invoice Number"
        invoice_df = pd.DataFrame(
            invoices,
            columns=["Invoice Number", "Customer ID", "Status", "Invoice Date", "Total Amount", "Created By", "Updated By", "Created On", "Updated On"]
        )
        st.dataframe(invoice_df, use_container_width=True)

        # Create a dropdown to select an invoice
        invoice_options = {f"Invoice #{invoice[0]} - Total: {invoice[4]}": invoice[0] for invoice in invoices}
        selected_invoice_number = st.selectbox("Select an Invoice", options=list(invoice_options.keys()))

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate PDF Invoice"):
                invoice_number = invoice_options[selected_invoice_number]

                # Fetch invoice details and items using invoice_number
                invoice_details_query = """
                    SELECT i.id, i.customer_id, i.invoice_date, i.total_amount, s.status_name, i.invoice_number
                    FROM invoices i
                    JOIN statuses s ON i.status_id = s.id
                    WHERE i.invoice_number = %s
                """
                invoice_details = db_manager_instance.execute_query(invoice_details_query, (invoice_number,), fetch='one')

                invoice_items_query = """
                    SELECT ii.item_id, it.description, CONCAT(u.first_name, ' ', u.last_name) AS vendor_name, 
                           ii.quantity, it.price, ii.total_price
                    FROM invoice_items ii
                    JOIN items it ON ii.item_id = it.id
                    JOIN users u ON it.vendor_id = u.id
                    WHERE ii.invoice_id = (SELECT id FROM invoices WHERE invoice_number = %s)
                """
                invoice_items = db_manager_instance.execute_query(invoice_items_query, (invoice_number,), fetch='all')

                if invoice_details:
                    if invoice_items:
                        # Generate the PDF invoice and save it to the "invoices" folder
                        os.makedirs("invoices", exist_ok=True)
                        pdf_path = f"invoices/Invoice_{invoice_details[0]}_{invoice_details[1]}.pdf"
                        pdf_generator.generate_invoice_pdf(invoice_details, invoice_items, pdf_path)

                        # Notify the user that the PDF has been generated
                        st.success(f"PDF for Invoice #{invoice_number} has been generated and saved as '{pdf_path}'.")
                    else:
                        st.error(f"Failed to fetch items for Invoice #{invoice_number}.")
                else:
                    st.error(f"Failed to fetch details for Invoice #{invoice_number}.")

        with col2:
            if st.button("Pay Invoice"):
                invoice_number = invoice_options[selected_invoice_number]
                # Update the invoice status to "paid"
                pay_invoice_query = """
                    UPDATE invoices
                    SET status_id = (SELECT id FROM statuses WHERE status_name = 'paid'),
                        updated_by = %s,
                        updated_on = NOW()
                    WHERE invoice_number = %s
                """
                try:
                    db_manager_instance.execute_query(pay_invoice_query, params=(user_id, invoice_number), commit=True)
                    # If no exception is raised, assume the query was successful
                    st.success(f"Invoice #{invoice_number} marked as paid successfully!")
                    # Set a query parameter to trigger a delayed rerun
                    st.experimental_set_query_params(rerun="true")
                except Exception as e:
                    # Handle any exceptions that occur during query execution
                    st.error(f"Failed to mark Invoice #{invoice_number} as paid. Error: {str(e)}")
    else:
        st.info("No invoices found.")

def display_manage_items(db_manager_instance, user_id, user_role):
    st.subheader("Manage Items")
    query = "select * from items" if user_role in ["superadmin", "vendor_admin"] else "select * from items where vendor_id = %s"
    params = (user_id,) if user_role == "vendor" else None
    items = db_manager_instance.execute_query(query, params, fetch='all')

    if items:
        # Update the column names to match the number of columns returned by the query
        item_df = pd.DataFrame(
            items,
            columns=["ID", "Vendor ID", "Description", "Price", "Stock", "Created By", "Updated By", "Created On", "Updated On"]
        )
        st.dataframe(item_df, use_container_width=True)
    else:
        st.info("No items found.")

    # Allow vendors and superadmins to add new items
    if user_role in ["superadmin", "vendor", "vendor_admin"]:
        st.write("---")
        st.write("### Add New Item")
        
        # Fetch vendors for the dropdown (only for superadmin)
        vendor_options = {}
        if user_role == "superadmin":
            vendor_query = "SELECT id, CONCAT(first_name, ' ', last_name) AS vendor_name FROM users WHERE role_id = (SELECT id FROM roles WHERE role_name = 'vendor')"
            vendors = db_manager_instance.execute_query(vendor_query, fetch='all')
            vendor_options = {f"{vendor_name} (ID: {vendor_id})": vendor_id for vendor_id, vendor_name in vendors}

        with st.form("add_item_form"):
            description = st.text_input("Description")
            price = st.number_input("Price", min_value=0.01, step=0.01)
            stock = st.number_input("Stock", min_value=0, step=1)
            vendor_id = None
            if user_role == "superadmin":
                selected_vendor = st.selectbox("Select Vendor", options=list(vendor_options.keys()))
                vendor_id = vendor_options[selected_vendor]
            else:
                vendor_id = user_id  # For vendors, the vendor_id is their own user_id

            if st.form_submit_button("Add Item"):
                add_item_query = """
                    INSERT INTO items (vendor_id, description, price, stock, created_by, updated_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (vendor_id, description, price, stock, user_id, user_id)
                if db_manager_instance.execute_query(add_item_query, params):
                    st.success(f"Item '{description}' added successfully.")
                    st.rerun()
                else:
                    st.error(f"Failed to add item '{description}'.")

        st.write("---")
        st.write("### Update Stock for Existing Items")
        item_options = {f"{item[2]} (ID: {item[0]})": item[0] for item in items}
        selected_item = st.selectbox("Select an Item to Update Stock", options=list(item_options.keys()))

        if selected_item:
            item_id = item_options[selected_item]
            current_stock_query = "SELECT stock FROM items WHERE id = %s"
            current_stock = db_manager_instance.execute_query(current_stock_query, (item_id,), fetch='one')[0]

            with st.form("update_stock_form"):
                new_stock = st.number_input("New Stock Amount", min_value=0, value=current_stock, step=1)
                if st.form_submit_button("Update Stock"):
                    update_stock_query = """
                        UPDATE items
                        SET stock = %s, updated_by = %s, updated_on = NOW()
                        WHERE id = %s
                    """
                    params = (new_stock, user_id, item_id)
                    if db_manager_instance.execute_query(update_stock_query, params):
                        st.success(f"Stock for item '{selected_item}' updated successfully.")
                        st.rerun()
                    else:
                        st.error(f"Failed to update stock for item '{selected_item}'.")

def display_manage_cart(db_manager_instance, user_id):
    st.subheader("Manage Cart")

    # Display cart contents at the top
    query = """
        select c.item_id, i.description, c.quantity, i.price
        from cart c
        join items i on c.item_id = i.id
        where c.user_id = %s and c.status_id = (select id from cart_status where status_name = 'active')
    """
    cart = db_manager_instance.execute_query(query, (user_id,), fetch='all')

    if cart:
        st.write("### Cart Contents")
        total_amount = 0
        for index, (item_id, description, quantity, price) in enumerate(cart):
            total = quantity * price
            st.write(f"ID: {item_id}, Description: {description}, Quantity: {quantity}, Price: {price}, Total: {total}")
            total_amount += total
            if st.button(f"Remove {description}", key=f"remove_{item_id}_{index}"):
                db_manager_instance.remove_from_cart(user_id, item_id)
                st.success(f"Removed {description} from the cart.")
                st.rerun()
        st.write(f"**Total Amount:** {total_amount}")

        if st.button("Clear Cart"):
            db_manager_instance.clear_cart(user_id)
            st.success("Cart cleared.")
            st.rerun()

        if st.button("Generate Invoice"):
            invoice_id = db_manager_instance.generate_invoice_from_cart(user_id)
            if invoice_id:
                st.success(f"Invoice #{invoice_id} generated successfully!")
            else:
                st.error("Failed to generate invoice.")
            st.rerun()
    else:
        st.info("Your cart is empty.")

    st.write("---")  # Separator

    # Use a form to browse and add items to the cart
    st.write("### Browse Listings")
    with st.form("browse_items_form"):
        query = """
            select i.id, i.description, i.price, i.stock, u.first_name, u.last_name
            from items i
            join users u on i.vendor_id = u.id
        """
        items = db_manager_instance.execute_query(query, fetch='all')

        if items:
            item_options = {
                f"{desc} - ${price} (Stock: {stock}) [Vendor: {vendor_fname} {vendor_lname}]": (item_id, price, stock)
                for item_id, desc, price, stock, vendor_fname, vendor_lname in items
            }
            selected_item = st.selectbox("Select an Item", options=list(item_options.keys()))
            quantity = st.number_input("Quantity", min_value=1, max_value=item_options[selected_item][2], step=1)

            if st.form_submit_button("Add to Cart"):
                item_id, price, stock = item_options[selected_item]
                db_manager_instance.update_cart(user_id, item_id, quantity)
                st.success(f"Updated cart with {quantity} of '{selected_item.split(' - ')[0]}'.")
                st.rerun()
        else:
            st.info("No items available.")

def display_manage_profile(db_manager_instance, user_id):
    st.subheader("Manage Profile")
    user_info = db_manager_instance.execute_query(
        "select username, email, phone, first_name, last_name, is_active from users where id = %s",
        (user_id,), fetch='one'
    )
    if user_info:
        username, email, phone, first_name, last_name, is_active = user_info
        with st.form("profile_form"):
            new_username = st.text_input("Username", value=username)
            new_email = st.text_input("Email", value=email)
            new_phone = st.text_input("Phone", value=phone)
            new_first_name = st.text_input("First Name", value=first_name)
            new_last_name = st.text_input("Last Name", value=last_name)
            is_active_checkbox = st.checkbox("Active", value=is_active)
            if st.form_submit_button("Update Profile"):
                # Check if the new username already exists
                check_username_query = """
                    select count(*) from users where username = %s and id != %s
                """
                username_exists = db_manager_instance.execute_query(check_username_query, (new_username, user_id), fetch='one')[0]

                if username_exists > 0:
                    st.error("The username is already taken. Please choose a different username.")
                else:
                    update_query = """
                        update users
                        set username = %s, email = %s, phone = %s, first_name = %s, last_name = %s, is_active = %s
                        where id = %s
                    """
                    params = (new_username, new_email, new_phone, new_first_name, new_last_name, is_active_checkbox, user_id)
                    if db_manager_instance.execute_query(update_query, params):
                        st.success("Profile updated successfully!")
                    else:
                        st.error("Failed to update profile.")
        st.write(f"**Username:** {username}")
    else:
        st.error("Failed to fetch profile information.")

def display_customer_registration_form(db_manager_instance):
    st.subheader("Customer Registration")
    with st.form("customer_registration_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        is_active = st.checkbox("Is Active", value=True)
        if st.form_submit_button("Register"):
            import bcrypt
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query = """
                insert into users (username, password_hash, email, phone, first_name, last_name, role_id, is_active, created_by, updated_by)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (username, hashed_password, email, phone, first_name, last_name, 4, is_active, 1, 1)
            if db_manager_instance.execute_query(query, params):
                st.success(f"Customer '{username}' registered successfully.")
            else:
                st.error(f"Failed to register customer '{username}'.")

import mysql.connector
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class DatabaseManager:
    """Manages database connections and queries."""

    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME')
        }

    def connect(self):
        """Establishes a database connection."""
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            st.error(f"Database connection error: {err}")
            return None

    def execute_query(self, query, params=None, fetch=False, commit=True):
        """Executes a database query."""
        connection = self.connect()
        if not connection:
            return None

        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone() if fetch == 'one' else cursor.fetchall() if fetch == 'all' else None
            if commit:
                connection.commit()
            return result
        except mysql.connector.Error as err:
            st.error(f"Database query error: {err}")
            return None
        finally:
            if cursor:
                cursor.close()
            connection.close()

    def add_to_cart(self, user_id, item_id, quantity):
        query = """
            INSERT INTO cart (user_id, item_id, quantity, status_id)
            VALUES (%s, %s, %s, (SELECT id FROM cart_status WHERE status_name = 'active'))
            ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
        """
        return self.execute_query(query, (user_id, item_id, quantity), commit=True)

    def update_cart(self, user_id, item_id, quantity):
        # Check if the item already exists in the active cart
        check_query = """
            select quantity from cart
            where user_id = %s and item_id = %s and status_id = (select id from cart_status where status_name = 'active')
        """
        existing_item = self.execute_query(check_query, (user_id, item_id), fetch='one')

        if existing_item:
            # If the item exists, update its quantity
            update_query = """
                update cart
                set quantity = quantity + %s
                where user_id = %s and item_id = %s and status_id = (select id from cart_status where status_name = 'active')
            """
            return self.execute_query(update_query, (quantity, user_id, item_id), commit=True)
        else:
            # If the item does not exist, use the add_to_cart function
            return self.add_to_cart(user_id, item_id, quantity)

    def get_cart(self, user_id):
        query = """
            select c.item_id, i.description, c.quantity, i.price
            from cart c
            join items i on c.item_id = i.id
            where c.user_id = %s and c.status_id = (select id from cart_status where status_name = 'active')
        """
        return self.execute_query(query, (user_id,), fetch='all')

    def remove_from_cart(self, user_id, item_id):
        query = """
            delete from cart
            where user_id = %s and item_id = %s and status_id = (select id from cart_status where status_name = 'active')
        """
        return self.execute_query(query, (user_id, item_id), commit=True)

    def clear_cart(self, user_id):
        query = """
            delete from cart
            where user_id = %s and status_id = (select id from cart_status where status_name = 'active')
        """
        return self.execute_query(query, (user_id,), commit=True)

    def mark_cart_as_converted(self, user_id):
        query = """
            update cart
            set status_id = (select id from cart_status where status_name = 'converted')
            where user_id = %s and status_id = (select id from cart_status where status_name = 'active')
        """
        return self.execute_query(query, (user_id,), commit=True)

    def generate_invoice_from_cart(self, user_id):
        # Fetch cart items
        cart_query = """
            SELECT c.item_id, c.quantity, i.price
            FROM cart c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = %s AND c.status_id = (SELECT id FROM cart_status WHERE status_name = 'active')
        """
        cart_items = self.execute_query(cart_query, (user_id,), fetch='all')

        if not cart_items:
            return None  # No items in the cart

        # Calculate total amount
        total_amount = sum(quantity * price for _, quantity, price in cart_items)

        # Generate unique invoice number
        invoice_number_query = """
            SELECT COUNT(*) + 1
            FROM invoices
            WHERE YEAR(invoice_date) = YEAR(CURDATE())
        """
        sequential_number = self.execute_query(invoice_number_query, fetch='one')[0]
        invoice_number = f"INV-{str(sequential_number).zfill(6)}-{str(user_id).zfill(4)}"

        # Insert invoice
        invoice_query = """
            INSERT INTO invoices (customer_id, status_id, invoice_date, total_amount, created_by, updated_by, invoice_number)
            VALUES (%s, (SELECT id FROM statuses WHERE status_name = 'unpaid'), CURDATE(), %s, %s, %s, %s)
        """
        invoice_id = None
        connection = self.connect()
        if not connection:
            return None

        try:
            cursor = connection.cursor()
            cursor.execute(invoice_query, (user_id, total_amount, user_id, user_id, invoice_number))
            invoice_id = cursor.lastrowid

            # Insert invoice items
            invoice_items_query = """
                INSERT INTO invoice_items (invoice_id, item_id, quantity, total_price, created_by, updated_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            for item_id, quantity, price in cart_items:
                total_price = quantity * price
                cursor.execute(invoice_items_query, (invoice_id, item_id, quantity, total_price, user_id, user_id))

                # Update stock for each item
                update_stock_query = """
                    UPDATE items
                    SET stock = stock - %s
                    WHERE id = %s
                """
                cursor.execute(update_stock_query, (quantity, item_id))

            # Mark cart items as converted
            mark_cart_query = """
                UPDATE cart
                SET status_id = (SELECT id FROM cart_status WHERE status_name = 'converted')
                WHERE user_id = %s AND status_id = (SELECT id FROM cart_status WHERE status_name = 'active')
            """
            cursor.execute(mark_cart_query, (user_id,))

            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            st.error(f"Failed to generate invoice: {err}")
            return None
        finally:
            cursor.close()
            connection.close()

        return invoice_id

    def pay_invoice(self, invoice_id, user_id):
        query = """
            UPDATE invoices
            SET status_id = (SELECT id FROM statuses WHERE status_name = 'paid'),
                updated_by = %s,
                updated_on = NOW()
            WHERE id = %s
        """
        return self.execute_query(query, (user_id, invoice_id), commit=True)

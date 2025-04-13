import streamlit as st
from modules import ui, db_manager
import bcrypt

db_manager_instance = db_manager.DatabaseManager()

def main():
    """Main entry point for the Invoice Management System."""
    st.title("Invoice Management System")

    if "user_id" in st.session_state:
        user_id, user_role = st.session_state["user_id"], st.session_state["user_role"]
        st.sidebar.title(f"Welcome, {user_role.capitalize()}!")
        page = st.sidebar.radio("Navigation", {
            "superadmin": ["Dashboard", "Manage Users", "Manage Invoices", "Manage Items", "Manage Profile"],
            "customer_admin": ["Dashboard", "Manage Users", "Manage Invoices", "Manage Items", "Manage Profile"],
            "vendor_admin": ["Dashboard", "Manage Users", "Manage Invoices", "Manage Items", "Manage Profile"],
            "vendor": ["Manage Items", "Manage Invoices", "Manage Profile"],
            "customer": ["Manage Cart", "Manage Invoices", "Manage Profile"]
        }.get(user_role, []))

        if page == "Dashboard": ui.display_dashboard(db_manager_instance, user_id, user_role)
        elif page == "Manage Users": ui.display_manage_users(db_manager_instance, user_id, user_role)
        elif page == "Manage Invoices": ui.display_manage_invoices(db_manager_instance, user_id, user_role)
        elif page == "Manage Items": ui.display_manage_items(db_manager_instance, user_id, user_role)
        elif page == "Manage Cart": ui.display_manage_cart(db_manager_instance, user_id)
        elif page == "Manage Profile": ui.display_manage_profile(db_manager_instance, user_id)
        else: st.error("You do not have permission to access this section.")

        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        with st.form("login_form"):
            username, password = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = db_manager_instance.execute_query(
                    "SELECT id, username, password_hash, role_id FROM users WHERE username = %s", (username,), fetch='one'
                )
                if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                    st.session_state.update({"user_id": user[0], "user_role": db_manager_instance.execute_query(
                        "SELECT role_name FROM roles WHERE id = %s", (user[3],), fetch='one')[0]})
                    st.success(f"Logged in as {username}")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        if st.button("Register as Customer"):
            ui.display_customer_registration_form(db_manager_instance)

if __name__ == "__main__":
    main()
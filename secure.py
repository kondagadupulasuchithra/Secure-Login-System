import streamlit as st
import sqlite3
import bcrypt
conn = sqlite3.connect('users.db', check_same_thread= False)
c = conn.cursor()
c.execute('''
           CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL
                )
''')
conn.commit()
def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
def check_password(password, hashed_password):
    """Verifies a pasword against the stored bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, password):
    """Registers a new user safely using parameterized queries."""
    hashed_pw = hash_password(password)
    try:
        c.execute('INSERT INTO users (username, password) VALUES(?, ?)', (username, hashed_pw))
        conn.commit()
        return True, "Registration successful! Please login."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose a different one."

def authenticate_user(username, password):
    """Authenticates user safely."""
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    if result and check_password(password, result[0]):
        return True
    return False

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

st.title("🔐 Secure Login System")
if st.session_state['logged_in']:
    st.success(f"Welcome to the Secure Dashboard, **{st.session_state['username']}**! ")
    st.markdown("---")
    st.subheader("🛡️ Security Features Implemented:")
    st.write("✅ **Password Hashing:** Passwords are encrypted using 'bcryprt.")
    st.write("✅ **SQL Injection Protection:** Database queries use safe parameterized parameters.")
    st.write("✅ **Session Management:** Secure active session state.")

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()

else:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Navigation", menu)
    if choice == "Register":
        st.subheader(" Create a New Account")
        new_user = st.text_input("Choose Username")
        new_password = st.text_input("Coose Password", type= 'password')
        confirm_password = st.text_input("Confirm Password", type= 'password')

        if st.button("Register"):
            if not new_user or not new_password:
                st.warning("Please fill in all fields.")
            elif len(new_password) < 6:
                st.warning("Password must be at least 6 characters long.")
            elif new_password != confirm_password:
                st.error("Password do not match!")
            else:
                success, msg = register_user(new_user, new_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    
    elif choice == "Login":
        st.subheader("User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Login"):
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                if authenticate_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. Please try again.")

import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Initialize Fernet
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# Session State Init
for key in ["stored_data", "failed_attempts", "authorized"]:
    if key not in st.session_state:
        st.session_state[key] = {}

# --- CSS Styling ---
st.markdown("""
<style>
.stApp {
    font-family: 'Segoe UI', sans-serif;
    background: url('https://img.freepik.com/free-photo/two-grey-cardboard-papers-corner-blue-backdrop_23-2147878447.jpg?t=st=1744366199~exp=1744369799~hmac=7225856fcc70194965b5bd71c315b6c8a413d129a69a0de5ae0dfe6e56cb93b3&w=996') no-repeat center center fixed;
    background-size: cover;
    min-height: 100vh;
}
h1 { color: #4A90E2; text-align: center; }
.block-container {
    background-color: rgba(255,255,255,0.9); padding: 2rem; border-radius: 12px;
}
.stButton > button {
    background-color: #4A90E2; color: white; border: none; font-weight: bold;
    border-radius: 8px; padding: 0.5rem 1.2rem; transition: 0.3s;
}
.stButton > button:hover { background-color: #357ae8; }
.stTextInput, .stTextArea {
    background-color: #f0f8ff; /* Light blue background */
    border: 1px solid #4A90E2; /* Blue border */
    border-radius: 5px; /* Rounded corners */
    padding: 10px; /* Padding inside the input */
}
</style>
""", unsafe_allow_html=True)

# --- Utilities ---
def hash_passkey(passkey): return hashlib.sha256(passkey.encode()).hexdigest()
def encrypt_data(text): return cipher.encrypt(text.encode()).decode()
def decrypt_data(encrypted_text): return cipher.decrypt(encrypted_text.encode()).decode()

# --- Title & Menu ---
st.markdown("<h1>🔐 Secure Data Encryption System</h1>", unsafe_allow_html=True)
st.divider()
menu = st.sidebar.radio("📌 Menu", ["🏠 Home", "📥 Store Data", "🔓 Retrieve Data", "🔑 Login", "🧹 Clear All"])

# --- Pages ---
if menu == "🏠 Home":
    st.subheader("🏡 Welcome to Your Secure Vault")
    st.markdown("- 🔐 **Encrypt & Store** data\n- 🔑 **Use a Passkey**\n- 🧠 **Smart Login with admin reset**")


elif menu == "📥 Store Data":
    st.subheader("📦 Store Your Data")
    with st.form("store"):
        label = st.text_input("📝 Label")
        user_data = st.text_area("🔐 Data")
        passkey = st.text_input("🔑 Passkey", type="password")
        if st.form_submit_button("💾 Save"):
            if label and user_data and passkey:
                st.session_state.stored_data[label] = {
                    "encrypted_text": encrypt_data(user_data),
                    "passkey": hash_passkey(passkey)
                }
                st.session_state.failed_attempts[label] = 0
                st.session_state.authorized[label] = True
                st.success("✅ Stored!")
                with st.expander("🔍 Encrypted Text"):
                    st.code(st.session_state.stored_data[label]["encrypted_text"])
            else:
                st.error("⚠️ All fields required.")

elif menu == "🔓 Retrieve Data":
    st.subheader("🔎 Retrieve Encrypted Data")
    with st.form("retrieve"):
        label = st.text_input("🆔 Label")
        passkey = st.text_input("🔑 Passkey", type="password")
        if st.form_submit_button("🔓 Decrypt"):
            data = st.session_state.stored_data.get(label)
            if data and "encrypted_text" in data:
                decrypted_data = decrypt_data(data["encrypted_text"])
                if decrypted_data:
                    st.success("✅ Decrypted!")
                    with st.expander("📜 Data"):
                        st.code(decrypted_data)
                    st.session_state.failed_attempts[label] = 0
                    st.session_state.authorized[label] = True
                else:
                    st.error("❌ Decryption failed.")
            else:
                st.error("⚠️ Label not found or encrypted text missing.")

elif menu == "🔑 Login":
    st.subheader("🔐 Reauthorize")
    with st.form("login"):
        label = st.text_input("🆔 Label")
        master = st.text_input("🔒 Admin Password", type="password")
        if st.form_submit_button("🔓 Reauthorize"):
            if master == "admin123" and label in st.session_state.failed_attempts:
                st.session_state.failed_attempts[label] = 0
                st.session_state.authorized[label] = True
                st.success("✅ Reauthorized!")
            else:
                st.error("❌ Invalid admin password or label.")

elif menu == "🧹 Clear All":
    st.subheader("⚠️ Clear All Session Data")
    if st.button("🧼 Confirm Reset"):
        for key in ["stored_data", "failed_attempts", "authorized"]:
            st.session_state[key].clear()
        st.success("🧽 Cleared!")


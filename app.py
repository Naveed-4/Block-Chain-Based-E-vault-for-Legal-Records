import streamlit as st
import os
import io
from typing import Tuple
import tempfile
import base64
from PIL import Image

from blockchain.evault_controller import EVaultController

# Initialize controller
controller = EVaultController()

# Set page config
st.set_page_config(page_title="E-Vault: Blockchain Legal Records", layout="wide")

# Inject custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("background.css")

# Helper functions
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

def is_image_file(filename):
    return get_file_extension(filename) in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']

def is_pdf_file(filename):
    return get_file_extension(filename) == '.pdf'

def render_document(content, doc_type):
    if doc_type.startswith('image/'):
        try:
            image = Image.open(io.BytesIO(content))
            st.image(image, caption="Document Preview", use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering image: {str(e)}")
    elif doc_type == 'application/pdf':
        # Display PDF download link
        b64 = base64.b64encode(content).decode()
        pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="500" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        # Try to render as text
        try:
            text = content.decode('utf-8')
            st.text_area("Document Content", text, height=300)
        except UnicodeDecodeError:
            st.warning("Cannot display this document type directly. Please download to view.")

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'session_token' not in st.session_state:
    st.session_state.session_token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# Login/register functions
def login(username, password):
    try:
        session_token = controller.login(username, password)
        if session_token:
            user_data = controller.get_user_by_session(session_token)
            st.session_state.logged_in = True
            st.session_state.session_token = session_token
            st.session_state.username = username
            st.session_state.user_id = user_data["user_id"]
            st.session_state.current_page = 'dashboard'
            return True
        else:
            st.error("Invalid username or password")
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def register(username, password, email):
    try:
        controller.register_user(username, password, email)
        st.success("Registration successful! Please login.")
        st.session_state.current_page = 'login'
        return True
    except ValueError as e:
        st.error(f"Registration error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"System error: {str(e)}")
        return False

def logout():
    if st.session_state.session_token:
        controller.logout(st.session_state.session_token)
    st.session_state.logged_in = False
    st.session_state.session_token = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.current_page = 'login'

# Navigation
def set_page(page):
    st.session_state.current_page = page

# Main application flow
def main():
    st.sidebar.title("E-Vault Navigation")
    
    if not st.session_state.logged_in:
        if st.session_state.current_page == 'login':
            render_login_page()
        elif st.session_state.current_page == 'register':
            render_register_page()
    else:
        # Sidebar navigation for logged-in users
        st.sidebar.button("Dashboard", on_click=set_page, args=('dashboard',), key='dashboard')
        st.sidebar.button("Upload Document", on_click=set_page, args=('upload',), key='upload')
        st.sidebar.button("My Documents", on_click=set_page, args=('documents',), key='documents')
        st.sidebar.button("Transfer Document", on_click=set_page, args=('transfer',), key='transfer')
        st.sidebar.button("Blockchain Explorer", on_click=set_page, args=('explorer',), key='explorer')
        st.sidebar.button("Logout", on_click=logout, key='logout')
        
        # Current user info
        st.sidebar.markdown("---")
        st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
        
        # Render current page
        if st.session_state.current_page == 'dashboard':
            render_dashboard()
        elif st.session_state.current_page == 'upload':
            render_upload_page()
        elif st.session_state.current_page == 'documents':
            render_documents_page()
        elif st.session_state.current_page == 'document_view':
            if 'view_document_hash' in st.session_state:
                render_document_view(st.session_state.view_document_hash)
        elif st.session_state.current_page == 'transfer':
            render_transfer_page()
        elif st.session_state.current_page == 'explorer':
            render_blockchain_explorer()

def render_login_page():
    st.title("E-Vault Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            login(username, password)
    
    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Register", key='register_button'):
        st.session_state.current_page = 'register'

def render_register_page():
    st.title("E-Vault Registration")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if password != password_confirm:
                st.error("Passwords do not match")
            else:
                register(username, password, email)
    
    st.markdown("---")
    st.write("Already have an account?")
    if st.button("Login", key='login_button'):
        st.session_state.current_page = 'login'

def render_dashboard():
    st.title("E-Vault Dashboard")
    
    # Display user information
    st.header("Welcome to your Legal E-Vault")
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    
    user_documents = controller.get_user_documents(st.session_state.session_token)
    user_transactions = controller.get_user_transactions(st.session_state.session_token)
    
    with col1:
        st.metric("Documents", len(user_documents))
    
    with col2:
        st.metric("Transactions", len(user_transactions))
    
    with col3:
        st.metric("Blockchain Status", "Valid" if controller.verify_blockchain() else "Invalid")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if user_transactions:
        sorted_transactions = sorted(user_transactions, key=lambda x: x.get("timestamp", 0), reverse=True)
        recent_transactions = sorted_transactions[:5]
        
        for i, tx in enumerate(recent_transactions):
            tx_type = tx.get("type", "unknown")
            timestamp = tx.get("timestamp", "unknown")
            doc_name = tx.get("document_name", "unknown")
            
            if tx_type == "document_upload":
                st.info(f"📄 You uploaded document '{doc_name}'")
            elif tx_type == "document_transfer":
                recipient_id = tx.get("recipient_id", "unknown")
                # Get recipient username
                recipient_data = controller.auth.get_user_by_id(recipient_id)
                recipient_name = recipient_data["username"] if recipient_data else "unknown user"
                st.warning(f"🔄 You transferred document '{doc_name}' to {recipient_name}")
            else:
                st.text(f"📝 Transaction: {tx_type} - {doc_name}")
    else:
        st.write("No recent activity.")

def render_upload_page():
    st.title("Upload Document")
    
    with st.form("upload_form", clear_on_submit=True):
        document_name = st.text_input("Document Name")
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "doc", "docx", "jpg", "jpeg", "png"])
        document_type = st.selectbox("Document Type", ["Contract", "Agreement", "Certificate", "ID", "Other"])
        submitted = st.form_submit_button("Upload to Blockchain")
        
        if submitted and uploaded_file is not None and document_name:
            try:
                # Get file content
                file_content = uploaded_file.getvalue()
                
                # Determine MIME type
                file_ext = get_file_extension(uploaded_file.name)
                mime_type = "application/pdf" if file_ext == ".pdf" else \
                           "image/jpeg" if file_ext in [".jpg", ".jpeg"] else \
                           "image/png" if file_ext == ".png" else \
                           "application/msword" if file_ext in [".doc", ".docx"] else \
                           "text/plain"
                
                # Upload to vault
                document_metadata = controller.upload_document(
                    st.session_state.session_token,
                    document_name,
                    file_content,
                    mime_type
                )
                
                st.success(f"Document '{document_name}' uploaded successfully!")
                st.write(f"Document Hash: {document_metadata['hash']}")
                
                # Redirect to documents page
                st.session_state.current_page = 'documents'
                st.rerun()
                
            except Exception as e:
                st.error(f"Upload error: {str(e)}")

def render_documents_page():
    st.title("My Documents")
    
    try:
        user_documents = controller.get_user_documents(st.session_state.session_token)
        
        if not user_documents:
            st.info("You don't have any documents yet. Upload your first document!")
            if st.button("Upload Document", key='upload_button'):
                st.session_state.current_page = 'upload'
                # st.stop()
                st.rerun()
            return
        
        st.write(f"You have {len(user_documents)} documents in your vault.")
        
        # Convert to list and sort by creation time
        doc_list = list(user_documents.items())
        doc_list.sort(key=lambda x: x[1].get("created_at", 0), reverse=True)
        
        for doc_hash, doc_metadata in doc_list:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{doc_metadata['name']}** ({doc_metadata['type']})")
                st.write(f"Hash: `{doc_hash[:10]}...`")
            
            with col2:
                if st.button("View", key=f"view_{doc_hash}"):
                    st.session_state.view_document_hash = doc_hash
                    st.session_state.current_page = 'document_view'
                    st.rerun()
            
            with col3:
                if st.button("Transfer", key=f"transfer_{doc_hash}"):
                    st.session_state.transfer_document_hash = doc_hash
                    st.session_state.current_page = 'transfer'
                    st.rerun()
            
            st.markdown("---")
    
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")

def render_document_view(document_hash):
    try:
        document_content, document_metadata = controller.get_document(
            st.session_state.session_token,
            document_hash
        )
        
        st.title(f"Document: {document_metadata['name']}")
        
        # Document metadata
        st.subheader("Document Information")
        st.write(f"Type: {document_metadata['type']}")
        st.write(f"Size: {document_metadata['size']} bytes")
        st.write(f"Hash: `{document_hash}`")
        
        # Document content
        st.subheader("Document Content")
        render_document(document_content, document_metadata['type'])
        
        # Document history
        st.subheader("Document History")
        document_history = controller.get_document_history(
            st.session_state.session_token,
            document_hash
        )
        
        if document_history:
            for i, tx in enumerate(sorted(document_history, key=lambda x: x.get("timestamp", 0))):
                tx_type = tx.get("type", "unknown")
                timestamp = tx.get("timestamp", "unknown")
                
                if tx_type == "document_upload":
                    st.info(f"📄 Document uploaded at {timestamp}")
                elif tx_type == "document_transfer":
                    sender_id = tx.get("sender_id", "unknown")
                    recipient_id = tx.get("recipient_id", "unknown")
                    
                    # Get usernames
                    sender_data = controller.auth.get_user_by_id(sender_id)
                    recipient_data = controller.auth.get_user_by_id(recipient_id)
                    
                    sender_name = sender_data["username"] if sender_data else "unknown"
                    recipient_name = recipient_data["username"] if recipient_data else "unknown"
                    
                    st.warning(f"🔄 Transferred from {sender_name} to {recipient_name} at {timestamp}")
                else:
                    st.text(f"📝 {tx_type} at {timestamp}")
        else:
            st.write("No history available for this document.")
        
        # Download button
        st.download_button(
            label="Download Document",
            data=document_content,
            file_name=document_metadata['name'],
            mime=document_metadata['type']
        )
        
        # Back button
        if st.button("Back to Documents", key='back_to_documents'):
            st.session_state.current_page = 'documents'
            st.rerun()
            
    except Exception as e:
        st.error(f"Error viewing document: {str(e)}")
        if st.button("Back to Documents", key='back_to_documents_error'):
            st.session_state.current_page = 'documents'
            st.rerun()

def render_transfer_page():
    st.title("Transfer Document")
    
    try:
        user_documents = controller.get_user_documents(st.session_state.session_token)
        
        if not user_documents:
            st.info("You don't have any documents to transfer. Upload a document first.")
            if st.button("Upload Document", key='upload_document_transfer'):
                st.session_state.current_page = 'upload'
                st.rerun()
            return
        
        # Get document to transfer
        selected_document_hash = None
        
        if 'transfer_document_hash' in st.session_state:
            selected_document_hash = st.session_state.transfer_document_hash
            st.session_state.transfer_document_hash = None  # Clear it after use
        
        document_options = {}
        for doc_hash, doc_metadata in user_documents.items():
            document_options[f"{doc_metadata['name']} ({doc_hash[:10]}...)"] = doc_hash
        
        selected_document_name = st.selectbox(
            "Select Document to Transfer",
            options=list(document_options.keys()),
            index=0
        )
        
        if selected_document_name:
            selected_document_hash = document_options[selected_document_name]
        
        # Get recipient username
        recipient_username = st.text_input("Recipient Username")
        
        if st.button("Transfer Document", key='transfer_document_button') and selected_document_hash and recipient_username:
            try:
                document_metadata = controller.transfer_document(
                    st.session_state.session_token,
                    selected_document_hash,
                    recipient_username
                )
                
                st.success(f"Document successfully transferred to {recipient_username}!")
                st.session_state.current_page = 'documents'
                st.rerun()
                
            except Exception as e:
                st.error(f"Transfer error: {str(e)}")
        
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")

def render_blockchain_explorer():
    st.title("Blockchain Explorer")
    
    # Verify blockchain integrity
    is_valid = controller.verify_blockchain()
    
    st.subheader("Blockchain Status")
    status_color = "green" if is_valid else "red"
    st.markdown(f"<h3 style='color: {status_color};'>{'✓ Valid' if is_valid else '✗ Invalid'}</h3>", unsafe_allow_html=True)
    
    # Display blocks
    st.subheader("Blockchain Blocks")
    
    for i, block in enumerate(controller.blockchain.chain):
        with st.expander(f"Block #{block.index} - Hash: {block.hash[:15]}..."):
            st.write(f"Timestamp: {block.timestamp}")
            st.write(f"Previous Hash: {block.previous_hash}")
            st.write(f"Nonce: {block.nonce}")
            
            if block.transactions:
                st.write(f"Transactions ({len(block.transactions)}):")
                for j, tx in enumerate(block.transactions):
                    st.json(tx)
            else:
                st.write("No transactions in this block")

# Run the main app
if __name__ == "__main__":
    main()
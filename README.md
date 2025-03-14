# E-Vault: Blockchain-based Legal Records System

A blockchain-based system for storing and transferring legal records with a simple Streamlit UI.

## Features

- **Document Upload**: Upload legal documents securely to the blockchain
- **Document Verification**: Verify document integrity using blockchain hashing
- **Document Transfer**: Transfer document ownership to other users
- **Blockchain Explorer**: View and explore the blockchain structure
- **User Authentication**: Secure login and registration system

## Project Structure

```
legal-evault/
├── app.py                   # Main Streamlit application
├── blockchain/              # Blockchain implementation
│   ├── blockchain.py        # Core blockchain classes
│   ├── persistence.py       # Blockchain storage
│   ├── auth.py              # User authentication
│   └── evault_controller.py # Main controller
├── storage/                 # Document storage
│   └── document_storage.py  # Document storage system
├── requirements.txt         # Project dependencies
└── README.md
```

## Setup Instructions

NOTE: Some of the files arent uploaded here as a directory < 100 files is only accepted. So, here is [link](https://drive.google.com/file/d/1P3qEt8bsrdGy1RZi-Dz1ddp4ecM10dK8/view?usp=sharing) to ask full environment workspace, download zip and extract

1. **Create a virtual environment**:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```
   streamlit run app.py
   ```

## Usage Guide

1. **Registration/Login**:
   - Create a new account or login with existing credentials

2. **Upload Documents**:
   - Navigate to "Upload Document" page
   - Enter document details and select file
   - Submit to store on blockchain

3. **View Documents**:
   - Go to "My Documents" to see all your documents
   - Click "View" to see document content and history

4. **Transfer Documents**:
   - Go to "Transfer Document" page
   - Select document and enter recipient username
   - Transfer ownership securely via blockchain

5. **Explore Blockchain**:
   - See blockchain structure and verify integrity
   - View transactions and block details

## Security Features

- Document encryption using AES
- Password hashing with salt
- Blockchain verification
- Secure document transfer

## Technology Stack

- **Backend**: Python
- **Blockchain**: Custom implementation
- **UI**: Streamlit
- **Storage**: Local encrypted file system
- **Authentication**: Password-based with session tokens

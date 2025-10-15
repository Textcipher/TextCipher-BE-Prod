# TextCipher-BE-Prod: Secure One-Time Encrypted Messaging API (Django/Python)

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Django Rest Framework](https://img.shields.io/badge/Framework-DRF-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-Not%20Specified-red)](./)

## 🔒 About TextCipher: Zero-Trace Confidential Communication

This repository contains the backend source code for **TextCipher**, the premier service for sending **secure, one-time messages**. Our mission is to provide **end-to-end encrypted** communication that leaves **zero trace** after viewing.

The core functionality of TextCipher ensures that sensitive information shared between users is protected by **strong cryptography** and is automatically deleted from the database immediately after the recipient reads it.

### Why Choose TextCipher for Private Messages?

* **View-Once Policy:** The message content is destroyed upon first access.
* **Military-Grade Encryption:** We utilize **Fernet (AES-256)** with a unique key generated for every single message. The key is never stored on the server.
* **Expires Automatically:** Messages not viewed are automatically set to expire after a defined period (default 5 days), ensuring data minimization.
* **Robust Backend:** Built on Django and Django Rest Framework for speed and reliability.

---

## 🚀 Experience The Full Service: Create Your Private Message Now!

This repository is the engine, but **TextCipher's main website** is the place where you can create, share, and view your private, self-destructing notes.

The most effective way to protect your secrets is with TextCipher. Visit the live platform today:

**👉 [TextCipher.com | Create Encrypted Self-Destructing Messages](https://www.textcipher.com)**

*(By linking this project to our main site, we aim to help users discover TextCipher when searching for secure messaging solutions and self-destructing note services.)*

---

## 🛠️ Code Overview: The API Engine

The backend logic is primarily split into the `message` and `contact` apps.

### `message` App Core Logic

This app handles the creation and destruction of confidential notes. The core process:

1.  **Creation (`/messages` POST):** The request content is encrypted using a unique, URL-embedded secret key. The encrypted binary content is saved to the `ContentV2` model.
2.  **Retrieval (`/messages/{unique_id}` GET):** The recipient's token is verified. The message is checked for viewing status and expiry. If valid, the content is decrypted, returned to the user, and the **encrypted content record is immediately deleted**.

### `contact` App Logic

Manages incoming user queries and feedback:

* The `Contact` model stores user messages along with the sender's IP address (for anti-abuse checks) and timestamps.
* The `ContactView` handles the submission of contact forms via a secure REST API endpoint.

---

## 📞 Contact Information

For technical inquiries, bug reports, or partnership opportunities related to this project or **TextCipher.com**, please reach out to the development team:

**Email:** `team@ciphertechglobal.com`
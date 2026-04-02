# 🚀 Smart QR Intelligence

**Machine Vision-Based Secure QR Generator & Scanner Web Application**

---

## 📌 Overview

Smart QR Intelligence is a feature-rich QR-based web application that enables users to **generate, scan, and analyze QR codes** with enhanced security and intelligent detection features.

This project integrates concepts from:

* 🧠 Machine Vision
* 🌐 Web Development
* 🔒 Security Systems
* 🤖 Rule-based Intelligent Logic

---

## ✨ Features

### 🔐 QR Generation

* Generate QR codes for text, URLs, or emails
* Set **expiry time** for QR codes
* Add **password protection**
* Enable **one-time scan QR codes**

---

### 📷 QR Scanning

* Scan QR using **live camera (browser-based using html5-qrcode)**
* Upload image to scan QR (**OpenCV with preprocessing**)
* Instant decoding and result display

---

### 🧠 Smart Detection (Rule-Based AI Logic)

* Automatically classifies QR content using pattern matching:

  * 🌐 URL detection
  * 📧 Email detection
  * 📝 Plain text detection

* Enables dynamic UI behavior based on detected type

---

### ⚠️ Malicious URL Detection

* Detects potentially unsafe or phishing links using keyword analysis:

  * login, verify, update, bank, secure, account, password, confirm

* Displays warning:
  ⚠️ **“Potential phishing or suspicious link detected”**

* Enhances user safety while opening unknown QR links

---

### 🧠 Machine Vision Concepts Used

This project incorporates fundamental image processing techniques:

* 📷 **Grayscale Conversion** – simplifies the image for better detection
* 🧹 **Noise Reduction** – improves clarity using Gaussian Blur
* 🔍 **QR Pattern Detection:**

  * Finder Patterns (corner squares)
  * Alignment Pattern (distortion correction)

These techniques enhance QR detection accuracy in real-world conditions.

---

### 🌍 Scan Tracking & Analytics

* Tracks:

  * IP Address
  * Location (City, Country)
  * Scan timestamp

* Maintains a complete **scan history dashboard**

---

### 🔄 Smart Actions

* Auto **redirect if QR contains URL**
* Display dynamic actions based on QR content

---

### 👤 User System

* User Registration & Login
* Personal QR history
* Secure access to generated QR codes

---

## ⚙️ How It Works

1. User generates a QR code with optional security settings
2. QR stores a secure **token-based URL**
3. When scanned:

   * Image is processed (for uploaded images)
   * QR is decoded
   * Token is verified
   * Security checks applied (expiry, password, one-time use)
   * Malicious URL check performed
4. Content is displayed or redirected based on type
5. Scan details are logged for analytics

---

## 🛠 Tech Stack

### Backend

* Python
* Flask

### Frontend

* HTML5
* CSS3
* Bootstrap

### Machine Vision

* OpenCV

### Database

* SQLite

### Other Libraries

* qrcode
* bcrypt
* requests

---

## 🧩 System Architecture

1. User generates QR → Stored in database
2. QR contains a secure token-based URL
3. On scan:

   * QR is decoded
   * Security checks applied
   * Data processed
   * Type detected
   * Malicious link checked
4. Scan is logged with metadata (IP, location, timestamp)

---

## 🔒 Security Features

* Token-based QR validation
* Expiry-based access control
* Password-protected QR codes
* One-time usable QR codes
* Unauthorized access prevention
* Basic phishing/malicious link detection

---

## 📊 Future Enhancements

* 📈 Scan analytics dashboard (graphs & insights)
* 🤖 ML-based classification model
* ☁️ Cloud database integration
* 📱 Mobile application version

---

## 🚀 Deployment

Deployed on:

* Render (Cloud Platform)

🔗 Live Demo: https://qr-onlinehosted.onrender.com/

---

## 💻 Run Locally

```bash
git clone https://github.com/AARTI756/qr_onlinehosted
cd qr_onlinehosted
python -m venv venv
venv\Scripts\activate   # For Windows
pip install -r requirements.txt
python app.py
```

---

## 👨‍💻 Author

**Aarti Sakpal**

---

## 📄 License

This project is for academic and learning purposes.

---

## ⭐ Project Highlights

✔ Secure QR system
✔ Machine Vision integration
✔ Intelligent detection logic
✔ Real-time scanning & analytics
✔ Basic phishing/malicious link detection
✔ Full-stack implementation

---

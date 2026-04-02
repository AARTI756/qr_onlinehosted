# 🚀 Smart QR Intelligence

**Machine Vision Based Secure QR Generator & Scanner Web Application**

---

## 📌 Overview

Smart QR Intelligence is an advanced QR-based web application built using **Computer Vision and intelligent logic**.
It allows users to **generate, scan, and analyze QR codes** with added security and smart detection features.

This project combines concepts from:

* Machine Vision
* Web Development
* Security Systems
* AI/ML-inspired logic (data type detection & analytics)

---

## ✨ Features

### 🔐 QR Generation

* Generate QR codes for any text, URL, or email
* Set **expiry time** for QR codes
* Add **password protection**
* Enable **one-time scan QR**

---

### 📷 QR Scanning

* Scan QR using **live camera (OpenCV)**
* Upload image to detect QR
* Instant decoding and processing

---

### 🧠 Smart Detection (AI Logic)

* Automatically detects QR content type:

  * 🌐 URL
  * 📧 Email
  * 📝 Text
* Dynamic UI response based on detected type

---

### 🌍 Scan Tracking & Analytics

* Tracks:

  * IP Address
  * Location (City, Country)
  * Scan timestamp
* Maintains complete **scan history dashboard**

---

### 🔄 Smart Actions

* Auto **redirect if QR contains URL**
* Show actionable buttons based on content

---

### 👤 User System

* User Registration & Login
* Personal QR history
* Secure access to generated QR codes

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
2. QR contains secure token-based URL
3. On scan:

   * QR is verified
   * Security checks applied (expiry, password)
   * Data processed
   * Type detected
4. Scan logged with metadata (IP, location, time)

---

## 🔒 Security Features

* Token-based QR validation
* Expiry-based access control
* Password-protected QR codes
* One-time usable QR
* Unauthorized access prevention

---

## 📊 Future Enhancements

* 📈 Scan analytics dashboard (graphs & insights)
* 🤖 ML-based classification model
* ☁️ Cloud database integration
* 📱 Mobile app version

---

## 🚀 Deployment

Deployed using:

* Render (Cloud Platform)

🔗 Live Demo: https://qr-onlinehosted.onrender.com/

---

## 👨‍💻 Author

**Aarti Sakpal**

---

## 📄 License

This project is for academic and learning purposes.

---

## ⭐ Project Highlights

✔ Secure QR system
✔ Machine vision integration
✔ Smart detection logic (AI-inspired)
✔ Real-time scanning & analytics
✔ Full-stack implementation

---

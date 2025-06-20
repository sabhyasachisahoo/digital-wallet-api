
# 💸 Digital Wallet API

A backend RESTful API service simulating a **digital wallet** system. This project includes user authentication, wallet funding, peer payments, product purchase, and balance conversion via a live currency API.

🔗 **Live Deployment**: [https://digital-wallet-api.onrender.com](https://digital-wallet-api.onrender.com)

---

## 🚀 Features

- 🔐 User Registration & Basic Auth using `bcrypt`
- 💰 Fund wallet (add balance)
- 🔁 Transfer funds to other users
- 💹 Currency conversion using `currencyapi.com`
- 📜 View transaction history
- 🛍️ Add and buy products using wallet balance
- ✅ Proper error handling and JSON responses

---

## 📦 Tech Stack

- **Flask** (Web framework)
- **Flask-SQLAlchemy** (ORM)
- **SQLite** (Database)
- **bcrypt** (for secure password hashing)
- **Render.com** (Deployment)
- **currencyapi.com** (External currency conversion API)

---

## 🔐 Authentication

All protected routes require HTTP Basic Auth:

```http
Authorization: Basic base64(username:password)
```

Example using `curl`:
```bash
curl -u raj:secret123 http://localhost:5000/bal
```

---

## 📖 API Endpoints

### 1. 👤 Register User  
`POST /register`

```json
{
  "username": "raj",
  "password": "secret123"
}
```

Returns `201 Created` or `400 User exists`.

---

### 2. 💰 Fund Wallet  
`POST /fund` _(Requires Auth)_

```json
{
  "amt": 1000
}
```

Response:
```json
{
  "balance": 1000
}
```

---

### 3. 💸 Pay Another User  
`POST /pay` _(Requires Auth)_

```json
{
  "to": "priya",
  "amt": 500
}
```

---

### 4. 💹 Check Balance (with optional currency)  
`GET /bal?currency=USD` _(Requires Auth)_

Response:
```json
{
  "balance": 12.3,
  "currency": "USD"
}
```

---

### 5. 📜 Transaction History  
`GET /stmt` _(Requires Auth)_

Returns:
```json
[
  {
    "kind": "credit",
    "amt": 1000,
    "updated_bal": 1000,
    "timestamp": "2025-06-09T09:00:00Z"
  }
]
```

---

### 6. 🛍️ Add Product  
`POST /product` _(Requires Auth)_

```json
{
  "name": "Wireless Mouse",
  "price": 599,
  "description": "Ergonomic USB Mouse"
}
```

---

### 7. 🧾 List All Products  
`GET /product` _(Public)_

Response:
```json
[
  {
    "id": 1,
    "name": "Wireless Mouse",
    "price": 599,
    "description": "Ergonomic USB Mouse"
  }
]
```

---

### 8. 🛒 Buy Product  
`POST /buy` _(Requires Auth)_

```json
{
  "product_id": 1
}
```

Returns:
```json
{
  "message": "Product purchased",
  "balance": 401
}
```

---

## 🛠️ Local Setup Instructions

```bash
git clone https://github.com/sabhyasachisahoo/digital-wallet-api
cd digital-wallet-api
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate (for macOS/Linux)
pip install -r requirements.txt
python app.py
```

---

## 🔬 Run Tests

```bash
pytest
```

---

## ☁️ Deployment on Render

- Render auto-deploys from GitHub
- `Procfile` contains: `web: gunicorn app:app`
- Uses `requirements.txt` and SQLite
- Free tier supported

---

## 📄 Files Overview

| File            | Purpose                             |
|-----------------|-------------------------------------|
| `app.py`        | Main Flask app                      |
| `requirements.txt` | Project dependencies             |
| `Procfile`      | Render start command (`gunicorn`)   |
| `test_app.py`   | Basic API tests (optional)          |
| `README.md`     | 📘 This file                        |

---

## 👤 Author

**Sabhyasachi Sahoo (Raj)**  
📂 GitHub: [@sabhyasachisahoo](https://github.com/sabhyasachisahoo)

---

## 🪪 License

This project is licensed under the [MIT License](LICENSE).

---

## 💬 Questions?

Feel free to open an issue or reach out on GitHub if you have questions or suggestions.

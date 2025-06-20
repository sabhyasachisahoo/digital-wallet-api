from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import base64
import requests
from datetime import datetime, timezone


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wallet.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    kind = db.Column(db.String(10))  # 'debit' or 'credit'
    amt = db.Column(db.Float)
    updated_bal = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.String(255))

def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return jsonify({'error': 'Unauthorized'}), 401
        encoded_credentials = auth.split(' ')[1]
        username, password = base64.b64decode(encoded_credentials).decode().split(':')
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({'error': 'Unauthorized'}), 401
        request.user = user
        return f(*args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'User exists'}), 400
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return '', 201

@app.route('/fund', methods=['POST'])
@authenticate
def fund():
    amt = request.json['amt']
    user = request.user
    user.balance += amt
    db.session.add(Transaction(user_id=user.id, kind='credit', amt=amt, updated_bal=user.balance))
    db.session.commit()
    return jsonify({'balance': user.balance})

@app.route('/pay', methods=['POST'])
@authenticate
def pay():
    data = request.json
    to_user = User.query.filter_by(username=data['to']).first()
    amt = data['amt']
    user = request.user
    if not to_user or user.balance < amt:
        return jsonify({'error': 'Insufficient funds or recipient not found'}), 400
    user.balance -= amt
    to_user.balance += amt
    db.session.add(Transaction(user_id=user.id, kind='debit', amt=amt, updated_bal=user.balance))
    db.session.add(Transaction(user_id=to_user.id, kind='credit', amt=amt, updated_bal=to_user.balance))
    db.session.commit()
    return jsonify({'balance': user.balance})

@app.route('/bal', methods=['GET'])
@authenticate
def balance():
    user = request.user
    currency = request.args.get('currency')
    if currency:
        res = requests.get(f'https://api.currencyapi.com/v3/latest?apikey=cur_live_LEe3Stp7KfGzJa3ebU6E39RE1MH0YHLUM0DkclQP&base_currency=INR')
        rate = res.json()['data'][currency]['value']
        return jsonify({'balance': round(user.balance * rate, 2), 'currency': currency})
    return jsonify({'balance': user.balance})

@app.route('/stmt', methods=['GET'])
@authenticate
def statement():
    user = request.user
    txns = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.timestamp.desc()).all()
    return jsonify([
        {'kind': t.kind, 'amt': t.amt, 'updated_bal': t.updated_bal, 'timestamp': t.timestamp.isoformat()}
        for t in txns
    ])

@app.route('/product', methods=['POST'])
@authenticate
def add_product():
    data = request.json
    p = Product(name=data['name'], price=data['price'], description=data['description'])
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'message': 'Product added'}), 201

@app.route('/product', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description}
        for p in products
    ])

@app.route('/buy', methods=['POST'])
@authenticate
def buy():
    product_id = request.json['product_id']
    product = db.session.get(Product, product_id)  # 🔄 updated here
    user = request.user
    if not product or user.balance < product.price:
        return jsonify({'error': 'Insufficient balance or invalid product'}), 400
    user.balance -= product.price
    db.session.add(Transaction(user_id=user.id, kind='debit', amt=product.price, updated_bal=user.balance))
    db.session.commit()
    return jsonify({'message': 'Product purchased', 'balance': user.balance})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

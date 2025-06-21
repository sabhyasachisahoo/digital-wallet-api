from flask import Blueprint, request, jsonify
from ..models import User, Transaction
from .. import db
from ..auth import authenticate
import bcrypt
import requests

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'User exists'}), 400
    hashed_pw = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return '', 201

@user_bp.route('/fund', methods=['POST'])
@authenticate
def fund():
    amt = request.json['amt']
    user = request.user
    user.balance += amt
    db.session.add(Transaction(user_id=user.id, kind='credit', amt=amt, updated_bal=user.balance))
    db.session.commit()
    return jsonify({'balance': user.balance})

@user_bp.route('/pay', methods=['POST'])
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

@user_bp.route('/bal', methods=['GET'])
@authenticate
def balance():
    user = request.user
    currency = request.args.get('currency')
    if currency:
        res = requests.get('https://api.currencyapi.com/v3/latest?apikey=cur_live_LEe3Stp7KfGzJa3ebU6E39RE1MH0YHLUM0DkclQP&base_currency=INR')
        rate = res.json()['data'][currency]['value']
        return jsonify({'balance': round(user.balance * rate, 2), 'currency': currency})
    return jsonify({'balance': user.balance})

@user_bp.route('/stmt', methods=['GET'])
@authenticate
def statement():
    user = request.user
    txns = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.timestamp.desc()).all()
    return jsonify([
        {'kind': t.kind, 'amt': t.amt, 'updated_bal': t.updated_bal, 'timestamp': t.timestamp.isoformat()}
        for t in txns
    ])

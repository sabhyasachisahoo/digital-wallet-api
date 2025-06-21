from flask import Blueprint, request, jsonify
from ..models import Product, Transaction
from .. import db
from ..auth import authenticate

product_bp = Blueprint('product', __name__)

@product_bp.route('/product', methods=['POST'])
@authenticate
def add_product():
    data = request.json
    p = Product(name=data['name'], price=data['price'], description=data['description'])
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'message': 'Product added'}), 201

@product_bp.route('/product', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description}
        for p in products
    ])

@product_bp.route('/buy', methods=['POST'])
@authenticate
def buy():
    product_id = request.json['product_id']
    product = db.session.get(Product, product_id)
    user = request.user
    if not product or user.balance < product.price:
        return jsonify({'error': 'Insufficient balance or invalid product'}), 400
    user.balance -= product.price
    db.session.add(Transaction(user_id=user.id, kind='debit', amt=product.price, updated_bal=user.balance))
    db.session.commit()
    return jsonify({'message': 'Product purchased', 'balance': user.balance})

from flask import request, jsonify
from decimal import Decimal
from models import db, Product, Inventory

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    name = data.get("name")
    sku = data.get("sku")
    price = data.get("price")
    warehouse_id = data.get("warehouse_id")
    initial_quantity = data.get("initial_quantity")

    if not all([name, sku, price, warehouse_id, initial_quantity]):
        return jsonify({"error": "Missing or empty fields"}), 400

    try:
        price = Decimal(str(price))
        initial_quantity = int(initial_quantity)
        if price < 0 or initial_quantity < 0:
            return jsonify({"error": "Price and quantity must be non-negative"}), 400
    except:
        return jsonify({"error": "Invalid price or quantity"}), 400

    existing_product = Product.query.filter_by(sku=sku).first()
    if existing_product:
        return jsonify({"error": "SKU already exists"}), 400

    product = Product(name=name, sku=sku, price=price)

    try:
        db.session.add(product)
        db.session.flush()

        inventory = Inventory(
            product_id=product.id,
            warehouse_id=warehouse_id,
            quantity=initial_quantity
        )
        db.session.add(inventory)
        db.session.commit()

        return jsonify({"message": "Product created", "product_id": product.id}), 201

    except:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

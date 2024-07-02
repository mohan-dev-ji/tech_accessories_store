from flask import Flask, render_template, url_for, flash, redirect, request, session, jsonify
from models import db, Product, CartItem, Order, OrderItem, ShippingDetails
from product_data import products
import uuid
import os
from dotenv import load_dotenv
import stripe
import json
from functools import wraps

load_dotenv()

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'khgfiugh34798gt934guoerbgfouewbrg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_PASSWORD'] = ADMIN_PASSWORD
db.init_app(app)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_orders'))
        else:
            flash('Invalid Password')
    return render_template('admin/login.html')

@app.route('/admin/logout')    
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/orders')
@admin_required
def admin_orders():
    # Get the page number from the URL parameters, default to 1 if not provided
    page = request.args.get('page', 1, type=int)

    # Get all selected status values from the URL parameters
    # This returns a list of all values associated with the 'status' key
    selected_statuses = request.args.getlist('status')

    # Start with a query that selects all orders
    query = Order.query

    # If any statuses were selected in the filter...
    if selected_statuses:
        # ...modify the query to only include orders with those statuses
        query = query.filter(Order.status.in_(selected_statuses))
    else:
        # If no statuses were selected, default to showing all statuses
        selected_statuses = ['paid', 'processing', 'shipped', 'delivered']

    # Execute the query, ordering by creation date (newest first)
    # Paginate the results, showing 20 items per page
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)

     # Render the template, passing in the orders and selected statuses
    return render_template('admin/orders.html', orders=orders, selected_statuses=selected_statuses)

@app.route('/admin/orders/<int:order_id>/update_status', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('new_status')
    if new_status in ['processing', 'shipped', 'paid', 'delivered']:
        order.status = new_status
        db.session.commit()
    return redirect(url_for('admin_orders'))
    

@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/order-confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')

def get_or_create_cart_id():
    if 'cart_id' not in session:
        cart_id = request.cookies.get('cart_id')
        if not cart_id:
            cart_id = str(uuid.uuid4())
        session['cart_id'] = cart_id
    print(f'CART ID IS {session['cart_id']}')
    return session['cart_id']

@app.after_request
def set_cart_id_cookie(response):
    if 'cart_id' in session:
        response.set_cookie('cart_id', session['cart_id'], max_age=30*24*60*60)
    return (response)

@app.route('/')
@app.route('/home')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    cart_id = get_or_create_cart_id()

    cart_item = CartItem.query.filter_by(product_id=product_id, cart_id=cart_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(product_id=product_id, quantity=quantity, cart_id=cart_id)    
        db.session.add(cart_item)

    db.session.commit()    

    message = f'{product.name} added to cart!'
    flash(message, 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'cart_count': get_cart_count(cart_id)})
    else:
        return redirect(url_for('product', product_id=product_id))

@app.route('/cart')
def cart():
    cart_id = get_or_create_cart_id()
    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart<int:item_id>', methods=['POST'])
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    quantity = int(request.form.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'cart_count': get_cart_count()})
    else:
        return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    db.session.delete(cart_item)
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'cart_count': get_cart_count()})
    else:
        return redirect(url_for('cart'))

def get_cart_count(cart_id):
    return CartItem.query.filter_by(cart_id=cart_id).with_entities(db.func.sum(CartItem.quantity)).scalar() or 0

@app.context_processor
def inject_cart_count():
    cart_id = get_or_create_cart_id()
    return dict(cart_count=get_cart_count(cart_id))

def cleanup_old_carts():
    # Old cart items that are over 30 days old
    # thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    # old_cart_items = CartItem.query.filter(CartItem.date_added < thirty_days_ago).all()

    # Delete all cart items
    old_cart_items = CartItem.query.all()
    for item in old_cart_items:
        db.session.delete(item)
    db.session.commit()
    flash('All carts have been clear', 'info')

@app.route('/clear_all_carts', methods=['POST'])
def clear_all_carts():
    cleanup_old_carts()
    return redirect(url_for('cart'))    


@app.route('/checkout', methods=['POST'])
def checkout():
    cart_id = get_or_create_cart_id()
    cart_items = CartItem.query.filter_by(cart_id=cart_id).all()
    
    if not cart_items:
        flash('Your cart is empty. Please add items before checking out.')
        return redirect(url_for('cart'))

    line_items = [{
        'price_data': {
            'currency': 'gbp',
            'product_data': {
                'name': item.product.name,
            },
            'unit_amount': int(item.product.price * 100),
        },
        'quantity': item.quantity,
    } for item in cart_items]

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('checkout_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('checkout_cancel', _external=True),
            shipping_address_collection={
                'allowed_countries': ['US', 'CA', 'GB']
            },
        )
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('cart'))

    return redirect(checkout_session.url, code=303)

@app.route('/checkout/success')
def checkout_success():
    stripe_session_id = request.args.get('session_id')
    if not stripe_session_id:
        flash('No session ID provided', 'error')
        return redirect(url_for('cart'))

    try:
        stripe_session = stripe.checkout.Session.retrieve(
            stripe_session_id,
            expand=['line_items']
                )
        
        print("Stripe Session Object")
        print(json.dumps(stripe_session, indent=2, default=str))

        # Create new oder
        new_order = Order(
            stripe_session_id=stripe_session.id,
            customer_name=stripe_session.customer_details.name,
            customer_email=stripe_session.customer_details.email,
            total_amount=stripe_session.amount_total / 100,
            status='paid'
        )

        # Add order to items
        for item in stripe_session.line_items.data:
            product = Product.query.filter_by(name=item.description).first()
            if product:
                order_item = OrderItem(
                    order=new_order,
                    product_id=product.id,
                    quantity=item.quantity,
                    price_per_unit=item.price.unit_amount / 100
                )
                db.session.add(order_item)

        # Add shipping details
        shipping = ShippingDetails(
            order=new_order,
            address_line1=stripe_session.shipping_details.address.line1,
            address_line2=stripe_session.shipping_details.address.line2,
            city=stripe_session.shipping_details.address.city,
            state=stripe_session.shipping_details.address.state,
            country=stripe_session.shipping_details.address.country,
            postal_code=stripe_session.shipping_details.address.postal_code
        )
        db.session.add(shipping)

        db.session.add(new_order)
        db.session.commit()

        # Send emails here

        cart_id = get_or_create_cart_id()
        CartItem.query.filter_by(cart_id=cart_id).delete()
        db.session.commit()
        flash('Your order has been placed successfully!', 'success')
        return render_template('order_confirmation.html', stripe_session=stripe_session)
    
    except stripe.error.StripeError as e:
        flash(f'An error occurred while processing your payment: {str(e)}', 'error')
        return redirect(url_for('cart'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('cart'))
    
@app.route('/checkout/cancel')
def checkout_cancel():
    flash('Your payment has been cancelled', 'info')
    return redirect(url_for('cart'))

def add_sample_products():
    for product_data in products:
        prodcut = Product(**product_data)
        db.session.add(prodcut)
    db.session.commit()

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()
        if not Product.query.first():
            add_sample_products()
    app.run(debug=True)
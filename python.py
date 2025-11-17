# app.py - COMPLETE FIXED VERSION
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import re
import os
from authlib.integrations.flask_client import OAuth
import secrets
from datetime import datetime, timedelta
import requests
import random
import base64
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Email Configuration (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'iuproixdobnexus@gmail.com'
app.config['MAIL_PASSWORD'] = 'lpog rmne gllt dtit'
app.config['MAIL_DEFAULT_SENDER'] = 'iuproixdobnexus@gmail.com'

mail = Mail(app)

# OTP Configuration
OTP_EXPIRY_MINUTES = 10

# Product upload configuration
UPLOAD_FOLDER_PRODUCTS = 'static/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER_PRODUCTS'] = UPLOAD_FOLDER_PRODUCTS

# Create upload folders if they don't exist
os.makedirs(UPLOAD_FOLDER_PRODUCTS, exist_ok=True)
os.makedirs('uploads', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Google OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='',  # ⚠️ CHANGE THIS
    client_secret='',  # ⚠️ CHANGE THIS
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# PSGC API Helper Functions
def get_psgc_name(endpoint, code):
    """Fetch name from PSGC API based on code"""
    try:
        response = requests.get(f'https://psgc.gitlab.io/api/{endpoint}/{code}/')
        if response.status_code == 200:
            data = response.json()
            return data.get('name', '')
    except:
        pass
    return ''

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='mode7app'
    )
    return conn

# Email validation function
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

# ========== OTP HELPER FUNCTIONS ==========
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp_code, first_name):
    try:
        msg = Message(
            subject='Your OTP Code - Mode7 App',
            recipients=[email],
            html=f'''
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #333; text-align: center;">Email Verification</h2>
                        <p style="color: #666; font-size: 16px;">Hello {first_name},</p>
                        <p style="color: #666; font-size: 16px;">Your OTP code for email verification is:</p>
                        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
                            <h1 style="color: #007bff; font-size: 36px; margin: 0; letter-spacing: 5px;">{otp_code}</h1>
                        </div>
                        <p style="color: #666; font-size: 14px;">This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
                        <p style="color: #666; font-size: 14px;">If you didn't request this code, please ignore this email.</p>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                        <p style="color: #999; font-size: 12px; text-align: center;">Mode7 App - E-commerce Platform</p>
                    </div>
                </body>
            </html>
            '''
        )
        mail.send(msg)
        print(f"✓ OTP email sent to {email}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        return False

# Password reset OTP email

def send_password_reset_otp_email(email, otp_code, first_name):
    try:
        msg = Message(
            subject='Password Reset OTP - Mode7 App',
            recipients=[email],
            html=f'''
            <html>
                <body style=\"font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;\">
                    <div style=\"max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);\">
                        <h2 style=\"color: #333; text-align: center;\">Password Reset</h2>
                        <p style=\"color: #666; font-size: 16px;\">Hello {first_name or ''},</p>
                        <p style=\"color: #666; font-size: 16px;\">Use the OTP below to reset your password:</p>
                        <div style=\"background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;\">
                            <h1 style=\"color: #dc3545; font-size: 36px; margin: 0; letter-spacing: 5px;\">{otp_code}</h1>
                        </div>
                        <p style=\"color: #666; font-size: 14px;\">This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
                        <p style=\"color: #666; font-size: 14px;\">If you did not request a password reset, you can ignore this email.</p>
                        <hr style=\"border: none; border-top: 1px solid #ddd; margin: 20px 0;\">
                        <p style=\"color: #999; font-size: 12px; text-align: center;\">Mode7 App - E-commerce Platform</p>
                    </div>
                </body>
            </html>
            '''
        )
        mail.send(msg)
        print(f"✓ Password reset OTP sent to {email}")
        return True
    except Exception as e:
        print(f"✗ Error sending password reset email: {str(e)}")
        return False

def is_otp_expired(otp_created_at):
    if not otp_created_at:
        return True
    expiry_time = otp_created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
    return datetime.now() > expiry_time

# ========================================
# BASIC ROUTES
# ========================================
@app.route('/')
def landing():
    # Optional filters via query params
    selected_cat = request.args.get('cat')
    search_query = request.args.get('q', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, u.first_name as seller_name, u.last_name as seller_lastname
        FROM products p
        JOIN users u ON p.seller_id = u.id
        WHERE p.status = 'active'
        ORDER BY p.created_at DESC
    ''')
    products = cursor.fetchall()
    cursor.close(); conn.close()

    # Apply category and search filters in Python
    filtered = products
    if selected_cat:
        filtered = [p for p in filtered if p.get('category') == selected_cat]

    if search_query:
        q_lower = search_query.lower()
        def matches(p):
            name = (p.get('name') or '').lower()
            desc = (p.get('description') or '').lower()
            return q_lower in name or q_lower in desc
        filtered = [p for p in filtered if matches(p)]

    filtered_products = filtered if (selected_cat or search_query) else []

    categories = [
        'Suits & Blazers',
        'Casual Shirts & Pants',
        'Outerwear & Jackets',
        'Activewear & Fitness Gear',
        'Shoes & Accessories',
        'Grooming Products',
    ]

    return render_template('landing.html',
                           categories=categories,
                           selected_cat=selected_cat,
                           search_query=search_query,
                           filtered_products=filtered_products,
                           all_products=products)

# ========================================
# BUYER ROUTES
# ========================================
@app.route('/buyer')
def buyer():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if session.get('account_type') != 'buyer':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))
    
    # Optional category filter from query string
    selected_category = request.args.get('category')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, u.first_name as seller_name, u.last_name as seller_lastname
        FROM products p
        JOIN users u ON p.seller_id = u.id
        WHERE p.status = 'active'
        ORDER BY p.created_at DESC
    ''')
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    if selected_category:
        products = [p for p in products if p.get('category') == selected_category]
    
    return render_template('buyer/home.html', products=products, selected_category=selected_category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Load main product data
    cursor.execute('''
        SELECT p.*, u.first_name as seller_name, u.last_name as seller_lastname
        FROM products p
        JOIN users u ON p.seller_id = u.id
        WHERE p.id = %s
    ''', (product_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        flash('Product not found', 'error')
        return redirect(url_for('buyer'))

    # Load additional product images (gallery)
    cursor.execute('''
        SELECT image
        FROM product_images
        WHERE product_id = %s
        ORDER BY id ASC
    ''', (product_id,))
    product_images = cursor.fetchall()

    # Load related products from the same category (if category is set)
    related_products = []
    product_category = product.get('category') if isinstance(product, dict) else product["category"] if product else None
    if product_category:
        cursor.execute('''
            SELECT p.id, p.name, p.price, p.image, p.category
            FROM products p
            WHERE p.status = 'active'
              AND p.category = %s
              AND p.id != %s
            ORDER BY p.created_at DESC
            LIMIT 4
        ''', (product_category, product_id))
        related_products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'buyer/product_detail.html',
        product=product,
        product_images=product_images,
        related_products=related_products
    )

# ========================================
# BUYER & SELLER PROFILE ROUTES
# ========================================
@app.route('/buyer/profile')
def buyer_profile():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT id, first_name, last_name, email, phone, account_type, status,
               region_name, province_name, municipality_name, barangay_name, street, zip_code,
               valid_id, is_google_user, email_verified,
               store_name, product_category, business_permit, orcr_image, vehicle_plate_image,
               created_at
        FROM users WHERE id = %s
    ''', (user_id,))
    user = cursor.fetchone()
    cursor.close(); conn.close()
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('buyer'))
    
    return render_template('buyer/profile.html', user=user)


@app.route('/buyer/profile/edit', methods=['GET', 'POST'])
def buyer_profile_edit():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        street = request.form.get('street', '').strip()
        barangay_name = request.form.get('barangay_name', '').strip()
        municipality_name = request.form.get('municipality_name', '').strip()
        province_name = request.form.get('province_name', '').strip()
        region_name = request.form.get('region_name', '').strip()
        zip_code = request.form.get('zip_code', '').strip()

        if not first_name or not last_name:
            cursor.close(); conn.close()
            flash('First name and last name are required.', 'error')
            return redirect(url_for('buyer_profile_edit'))

        try:
            cursor.execute('''
                UPDATE users
                SET first_name = %s,
                    last_name = %s,
                    phone = %s,
                    street = %s,
                    barangay_name = %s,
                    municipality_name = %s,
                    province_name = %s,
                    region_name = %s,
                    zip_code = %s
                WHERE id = %s
            ''', (first_name, last_name, phone or None, street or None,
                  barangay_name or None, municipality_name or None,
                  province_name or None, region_name or None,
                  zip_code or None, user_id))
            conn.commit()
            cursor.close(); conn.close()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('buyer_profile'))
        except Exception as e:
            conn.rollback()
            cursor.close(); conn.close()
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('buyer_profile_edit'))

    # GET method: load current data
    cursor.execute('''
        SELECT id, first_name, last_name, email, phone, account_type, status,
               region_name, province_name, municipality_name, barangay_name, street, zip_code,
               valid_id, is_google_user, email_verified,
               store_name, product_category, business_permit, orcr_image, vehicle_plate_image,
               created_at
        FROM users WHERE id = %s
    ''', (user_id,))
    user = cursor.fetchone()
    cursor.close(); conn.close()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('buyer'))

    return render_template('buyer/profile_edit.html', user=user)


@app.route('/seller/profile')
def seller_profile():
    if 'user_id' not in session or session.get('account_type') != 'seller':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT id, first_name, last_name, email, phone, account_type, status,
               region_name, province_name, municipality_name, barangay_name, street, zip_code,
               valid_id, is_google_user, email_verified,
               store_name, product_category, business_permit, orcr_image, vehicle_plate_image,
               created_at
        FROM users WHERE id = %s
    ''', (user_id,))
    user = cursor.fetchone()
    cursor.close(); conn.close()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('seller_dashboard'))

    return render_template('seller/profile.html', user=user)


@app.route('/seller/profile/edit', methods=['GET', 'POST'])
def seller_profile_edit():
    if 'user_id' not in session or session.get('account_type') != 'seller':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        store_name = request.form.get('store_name', '').strip()
        business_permit = request.form.get('business_permit', '').strip()

        if not store_name:
            cursor.close(); conn.close()
            flash('Store name is required.', 'error')
            return redirect(url_for('seller_profile_edit'))

        try:
            cursor.execute('''
                UPDATE users
                SET store_name = %s,
                    business_permit = %s
                WHERE id = %s
            ''', (
                store_name,
                business_permit or None,
                user_id
            ))
            conn.commit()
            cursor.close(); conn.close()
            flash('Seller profile updated successfully.', 'success')
            return redirect(url_for('seller_profile'))
        except Exception as e:
            conn.rollback()
            cursor.close(); conn.close()
            flash(f'Error updating seller profile: {str(e)}', 'error')
            return redirect(url_for('seller_profile_edit'))

    # GET: load current data
    cursor.execute('''
        SELECT id, first_name, last_name, email, phone, account_type, status,
               region_name, province_name, municipality_name, barangay_name, street, zip_code,
               valid_id, is_google_user, email_verified,
               store_name, product_category, business_permit, orcr_image, vehicle_plate_image,
               created_at
        FROM users WHERE id = %s
    ''', (user_id,))
    user = cursor.fetchone()
    cursor.close(); conn.close()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('seller_dashboard'))

    return render_template('seller/profile_edit.html', user=user)


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        return jsonify({'success': False, 'message': 'Please login as buyer'}), 403
    
    buyer_id = session['user_id']
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    except:
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT stock, name FROM products WHERE id = %s AND status = "active"', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    if product['stock'] < quantity:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': f'Only {product["stock"]} items available'}), 400
    
    try:
        cursor.execute('SELECT id, quantity FROM cart_items WHERE buyer_id = %s AND product_id = %s', 
                      (buyer_id, product_id))
        existing = cursor.fetchone()
        
        if existing:
            new_quantity = existing['quantity'] + quantity
            if new_quantity > product['stock']:
                return jsonify({'success': False, 
                              'message': f'Cannot add more. Only {product["stock"]} available'}), 400
            
            cursor.execute('UPDATE cart_items SET quantity = %s WHERE id = %s', 
                          (new_quantity, existing['id']))
        else:
            cursor.execute('INSERT INTO cart_items (buyer_id, product_id, quantity) VALUES (%s, %s, %s)',
                          (buyer_id, product_id, quantity))
        
        conn.commit()
        
        cursor.execute('SELECT COUNT(*) as count FROM cart_items WHERE buyer_id = %s', (buyer_id,))
        cart_count = cursor.fetchone()['count']
        
        return jsonify({
            'success': True, 
            'message': f'Added {product["name"]} to cart!',
            'cart_count': cart_count
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/cart')
def view_cart():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Please login as buyer', 'error')
        return redirect(url_for('login'))
    
    buyer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT c.id, c.quantity, 
               p.id as product_id, p.name, p.price, p.stock, p.image, p.seller_id,
               u.first_name as seller_name
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        JOIN users u ON p.seller_id = u.id
        WHERE c.buyer_id = %s AND p.status = 'active'
        ORDER BY c.created_at DESC
    ''', (buyer_id,))
    
    cart_items = cursor.fetchall()
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    seller_ids = {item['seller_id'] for item in cart_items} if cart_items else set()
    seller_count = len(seller_ids)
    
    cursor.close()
    conn.close()
    
    return render_template('buyer/cart.html', cart_items=cart_items, subtotal=subtotal, seller_count=seller_count)

@app.route('/cart/update/<int:cart_item_id>', methods=['POST'])
def update_cart_quantity(cart_item_id):
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    buyer_id = session['user_id']
    data = request.get_json()
    new_quantity = data.get('quantity', 1)
    
    try:
        new_quantity = int(new_quantity)
        if new_quantity <= 0:
            return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    except:
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT c.id, p.stock, p.name
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE c.id = %s AND c.buyer_id = %s
    ''', (cart_item_id, buyer_id))
    
    cart_item = cursor.fetchone()
    
    if not cart_item:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Cart item not found'}), 404
    
    if new_quantity > cart_item['stock']:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 
                       'message': f'Only {cart_item["stock"]} available'}), 400
    
    try:
        cursor.execute('UPDATE cart_items SET quantity = %s WHERE id = %s', 
                      (new_quantity, cart_item_id))
        conn.commit()
        
        cursor.execute('''
            SELECT SUM(p.price * c.quantity) as subtotal
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            WHERE c.buyer_id = %s
        ''', (buyer_id,))
        
        result = cursor.fetchone()
        subtotal = float(result['subtotal']) if result['subtotal'] else 0
        
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'subtotal': subtotal
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    buyer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM cart_items WHERE id = %s AND buyer_id = %s', 
                      (cart_item_id, buyer_id))
        conn.commit()
        flash('Item removed from cart', 'success')
        return redirect(url_for('view_cart'))
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_cart'))
    finally:
        cursor.close()
        conn.close()

@app.route('/checkout')
def checkout():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Please login as buyer', 'error')
        return redirect(url_for('login'))
    
    buyer_id = session['user_id']
    selected_ids = request.args.getlist('selected')  # cart item IDs from cart page
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    base_query = '''
        SELECT c.id, c.quantity, 
               p.id as product_id, p.name, p.price, p.stock, p.image, p.seller_id,
               u.first_name as seller_name
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        JOIN users u ON p.seller_id = u.id
        WHERE c.buyer_id = %s AND p.status = 'active'
    '''
    params = [buyer_id]
    if selected_ids:
        placeholders = ','.join(['%s'] * len(selected_ids))
        base_query += f" AND c.id IN ({placeholders})"
        params.extend(selected_ids)
    base_query += ' ORDER BY c.created_at DESC'
    cursor.execute(base_query, tuple(params))
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('Please select items to checkout.', 'warning')
        cursor.close()
        conn.close()
        return redirect(url_for('view_cart'))
    
    cursor.execute('''
        SELECT street, barangay_name, municipality_name, province_name, region_name, zip_code, phone
        FROM users WHERE id = %s
    ''', (buyer_id,))
    buyer_info = cursor.fetchone()
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    shipping_fee = 50 if cart_items else 0
    total = subtotal + shipping_fee

    # Per-seller breakdown to show transparency in the summary
    seller_totals = {}
    for item in cart_items:
        sid = item['seller_id']
        if sid not in seller_totals:
            seller_totals[sid] = {
                'seller_name': item['seller_name'],
                'total': 0.0,
            }
        seller_totals[sid]['total'] += float(item['price']) * item['quantity']
    seller_breakdown = list(seller_totals.values())
    
    cursor.close()
    conn.close()
    
    return render_template('buyer/checkout.html', 
                          cart_items=cart_items, 
                          buyer_info=buyer_info,
                          subtotal=subtotal,
                          shipping_fee=shipping_fee,
                          total=total,
                          selected_ids=[str(i) for i in selected_ids],
                          seller_breakdown=seller_breakdown)
@app.route('/order/place', methods=['POST'])
def place_order():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    buyer_id = session['user_id']
    delivery_address = request.form.get('delivery_address')
    payment_method = request.form.get('payment_method', 'COD').upper()
    selected_ids = request.form.getlist('selected_ids[]')  # cart_item ids
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # If PayMongo is chosen, we will still create orders as pending and
    # then redirect to a PayMongo payment page based on a separate endpoint.
    try:
        base_query = '''
            SELECT c.id as cart_item_id, c.quantity, p.id as product_id, p.name, p.price, p.stock, p.seller_id
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            WHERE c.buyer_id = %s AND p.status = 'active'
        '''
        params = [buyer_id]
        if selected_ids:
            placeholders = ','.join(['%s'] * len(selected_ids))
            base_query += f" AND c.id IN ({placeholders})"
            params.extend(selected_ids)
        cursor.execute(base_query, tuple(params))
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({'success': False, 'message': 'No selected items to place order'}), 400

        for item in cart_items:
            if item['quantity'] > item['stock']:
                return jsonify({
                    'success': False,
                    'message': f'{item["name"]} only has {item["stock"]} left'
                }), 400

        order_numbers = []
        total_amount = 0
        for item in cart_items:
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
            line_total = float(item['price']) * item['quantity']
            total_amount += line_total
            status = 'pending'
            if payment_method == 'PAYMONGO':
                # Mark as pending_payment so we know this was initiated via online payment
                status = 'pending_payment'

            cursor.execute('''
                INSERT INTO orders (order_number, buyer_id, seller_id, product_id,
                                   quantity, total_price, delivery_address, delivery_lat, delivery_lng, status, stock_deducted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (order_number, buyer_id, item['seller_id'], item['product_id'],
                  item['quantity'], line_total, delivery_address,
                  request.form.get('delivery_lat'), request.form.get('delivery_lng'),
                  status, 0))

            order_numbers.append(order_number)

        # Remove only selected items from cart
        if selected_ids:
            placeholders = ','.join(['%s'] * len(selected_ids))
            cursor.execute(f'DELETE FROM cart_items WHERE buyer_id = %s AND id IN ({placeholders})', tuple([buyer_id] + selected_ids))
        else:
            cursor.execute('DELETE FROM cart_items WHERE buyer_id = %s', (buyer_id,))
        conn.commit()

        # If COD, behave as before
        if payment_method == 'COD':
            flash(f'Order placed successfully! Order numbers: {", ".join(order_numbers)}', 'success')
            return redirect(url_for('buyer_orders'))

        # If PayMongo, redirect to a PayMongo payment initialization route
        # We pass a simple order reference for now (first order number)
        primary_order = order_numbers[0] if order_numbers else None
        flash('Order created. Redirecting you to PayMongo to complete payment.', 'info')
        return redirect(url_for('paymongo_start', order_number=primary_order, amount=int(total_amount * 100)))

    except Exception as e:
        conn.rollback()
        flash(f'Error placing order: {str(e)}', 'error')
        return redirect(url_for('checkout'))
    finally:
        cursor.close()
        conn.close()

@app.route('/buyer/orders')
def buyer_orders():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    buyer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT o.*, p.name as product_name, p.image,
               u.first_name as seller_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON o.seller_id = u.id
        WHERE o.buyer_id = %s
        ORDER BY o.created_at DESC
    ''', (buyer_id,))
    
    orders = cursor.fetchall()

    # Count orders per status for filter badges
    status_counts = {
        'pending': 0,
        'processing': 0,
        'completed': 0,
        'cancelled': 0,
    }
    for o in orders:
        st = (o.get('status') or '').lower() if isinstance(o, dict) else str(o["status"]).lower()
        if st in status_counts:
            status_counts[st] += 1

    cursor.close()
    conn.close()
    
    return render_template('buyer/orders.html', orders=orders, status_counts=status_counts)


# ========================================
# PAYMONGO INTEGRATION (STUB)
# ========================================
@app.route('/paymongo/start')
def paymongo_start():
    """Initialize a PayMongo payment for an existing order using PayMongo Checkout.

    Expects query params:
      - order_number: reference string for the order (we use the first order number)
      - amount: total amount in CENTAVOS (integer), e.g., 15000 for ₱150.00
    """
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    order_number = request.args.get('order_number')
    amount = request.args.get('amount', type=int)

    if not order_number or not amount:
        flash('Missing payment details for PayMongo.', 'error')
        return redirect(url_for('buyer_orders'))

    secret_key = os.environ.get('PAYMONGO_SECRET_KEY')
    if not secret_key:
        flash('PayMongo secret key is not configured on the server.', 'error')
        return redirect(url_for('buyer_orders'))

    # Build basic auth header
    auth_token = base64.b64encode((secret_key + ':').encode()).decode()
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'authorization': f'Basic {auth_token}',
    }

    # Build success/cancel URLs for after payment
    success_url = url_for('buyer_orders', _external=True)
    cancel_url = url_for('buyer_orders', _external=True)

    data = {
        'data': {
            'attributes': {
                'line_items': [
                    {
                        'name': f'Order {order_number}',
                        'amount': amount,  # in centavos
                        'currency': 'PHP',
                        'quantity': 1,
                    }
                ],
                'payment_method_types': ['card', 'gcash', 'paymaya'],
                'description': f'Mode7 order {order_number}',
                # reference so we can match in webhook
                'reference_number': order_number,
                'success_url': success_url,
                'cancel_url': cancel_url,
            }
        }
    }

    try:
        resp = requests.post(
            'https://api.paymongo.com/v1/checkout_sessions',
            headers=headers,
            json=data,
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        checkout_url = payload['data']['attributes']['checkout_url']
    except Exception as e:
        # Do not expose detailed API error to user in production
        print(f'PayMongo API error: {e}')
        flash('Failed to initialize PayMongo payment. Please try again or use COD.', 'error')
        return redirect(url_for('buyer_orders'))

    # Redirect user to PayMongo-hosted payment page
    return redirect(checkout_url)


@app.route('/paymongo/webhook', methods=['POST'])
def paymongo_webhook():
    """Webhook endpoint for PayMongo events.

    NOTE: In production you MUST verify the signature from PayMongo (e.g. via
    `Paymongo-Signature` header). Here we keep it minimal and trust the payload.
    When a checkout session is paid, we update matching orders from
    `pending_payment` -> `pending`.
    """
    try:
        event = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({'error': 'invalid JSON'}), 400

    # Very basic parsing; adjust according to actual PayMongo event structure
    data = (event or {}).get('data', {})
    attributes = data.get('attributes', {})
    event_type = attributes.get('type') or event.get('type')

    # For checkout_sessions, PayMongo may send a type like
    # "checkout_session.payment.paid" or similar. Adjust to your actual payload.
    if event_type and 'paid' in event_type:
        # Try to retrieve our reference_number (order_number) from data
        checkout_data = attributes.get('data', {}) if isinstance(attributes.get('data', {}), dict) else attributes
        reference_number = (
            checkout_data.get('attributes', {}).get('reference_number')
            if isinstance(checkout_data, dict) else None
        ) or attributes.get('reference_number')

        if reference_number:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE order_number = %s AND status = %s",
                    ('pending', reference_number, 'pending_payment'),
                )
                conn.commit()
            finally:
                cursor.close()
                conn.close()

    # Always return 200 so PayMongo considers the webhook delivered
    return '', 200


# ========================================
# BUYER WISHLIST ROUTES
# ========================================
@app.route('/buyer/wishlist')
def buyer_wishlist():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    buyer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Simple wishlist table expected: wishlist(id, buyer_id, product_id)
    try:
        cursor.execute('''
            SELECT p.*
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            WHERE w.buyer_id = %s
            ORDER BY w.created_at DESC
        ''', (buyer_id,))
        wishlist_items = cursor.fetchall()
    except Exception as e:
        wishlist_items = []
        print(f"Wishlist query error: {e}")
        flash('Wishlist feature is not fully configured yet (missing table).', 'error')

    cursor.close()
    conn.close()

    return render_template('buyer/wishlist.html', wishlist_items=wishlist_items)

@app.route('/wishlist/add', methods=['POST'])
def add_to_wishlist():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        return jsonify({'success': False, 'message': 'Please login as buyer'}), 403

    buyer_id = session['user_id']
    data = request.get_json() or {}
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'success': False, 'message': 'Missing product id'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure table exists and avoid duplicates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist (
                id INT AUTO_INCREMENT PRIMARY KEY,
                buyer_id INT NOT NULL,
                product_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uniq_wishlist (buyer_id, product_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        cursor.execute('INSERT IGNORE INTO wishlist (buyer_id, product_id) VALUES (%s, %s)', (buyer_id, product_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': f'Error adding to wishlist: {e}'}), 500

    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Successfully added to wishlist.'}), 200

@app.route('/wishlist/remove', methods=['POST'])
def remove_from_wishlist_api():
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        return jsonify({'success': False, 'message': 'Please login as buyer'}), 403

    buyer_id = session['user_id']
    data = request.get_json() or {}
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'success': False, 'message': 'Missing product id'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM wishlist WHERE buyer_id = %s AND product_id = %s', (buyer_id, product_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': f'Error removing from wishlist: {e}'}), 500

    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Removed from wishlist'}), 200

@app.route('/wishlist/remove/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    if 'user_id' not in session or session.get('account_type') != 'buyer':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    buyer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM wishlist WHERE buyer_id = %s AND product_id = %s', (buyer_id, product_id))
        conn.commit()
        flash('Item removed from wishlist', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error removing from wishlist: {e}', 'error')
    finally:
        cursor.close(); conn.close()

    return redirect(url_for('buyer_wishlist'))

# ========================================
# SELLER ROUTES (Keep existing routes, add these fixes)
# ========================================
@app.route('/seller')
def seller():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if session.get('account_type') != 'seller':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))
    
    return redirect(url_for('seller_dashboard'))

@app.route('/seller/dashboard')
def seller_dashboard():
    if 'user_id' not in session or session.get('account_type') != 'seller':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    seller_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT COUNT(*) as total FROM products WHERE seller_id = %s', (seller_id,))
    total_products = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM orders WHERE seller_id = %s', (seller_id,))
    total_orders = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(total_price) as revenue FROM orders WHERE seller_id = %s AND status = "completed"', (seller_id,))
    total_revenue = cursor.fetchone()['revenue'] or 0
    
    cursor.execute('SELECT COUNT(*) as pending FROM orders WHERE seller_id = %s AND status = "pending"', (seller_id,))
    pending_orders = cursor.fetchone()['pending']

    # Recent orders for dashboard overview
    cursor.execute('''
        SELECT o.order_number, o.status, o.total_price, o.created_at,
               p.name as product_name,
               u.first_name as buyer_first_name,
               u.last_name as buyer_last_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON o.buyer_id = u.id
        WHERE o.seller_id = %s
        ORDER BY o.created_at DESC
        LIMIT 5
    ''', (seller_id,))
    recent_orders = cursor.fetchall()

    # Status distribution for charts
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM orders
        WHERE seller_id = %s
        GROUP BY status
    ''', (seller_id,))
    status_rows = cursor.fetchall()
    status_chart_data = {'pending': 0, 'processing': 0, 'completed': 0, 'cancelled': 0}
    for row in status_rows:
        st = (row.get('status') or '').lower()
        if st in status_chart_data:
            status_chart_data[st] = row['count']

    # Sales last 7 days (completed orders)
    cursor.execute('''
        SELECT DATE(created_at) as day, SUM(total_price) as total
        FROM orders
        WHERE seller_id = %s
          AND status = "completed"
          AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY DATE(created_at)
        ORDER BY day
    ''', (seller_id,))
    sales_rows = cursor.fetchall()
    sales_labels = [row['day'].strftime('%b %d') for row in sales_rows]
    sales_data = [float(row['total']) for row in sales_rows]

    # Revenue by category (completed orders)
    cursor.execute('''
        SELECT COALESCE(p.category, 'Uncategorized') as category,
               SUM(o.total_price) as total
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.seller_id = %s
          AND o.status = "completed"
        GROUP BY p.category
        ORDER BY total DESC
    ''', (seller_id,))
    cat_rows = cursor.fetchall()
    category_labels = [row['category'] for row in cat_rows]
    category_data = [float(row['total']) for row in cat_rows]
    
    cursor.close()
    conn.close()
    
    return render_template('seller/dashboard.html', 
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders,
                         chart_status_data=status_chart_data,
                         chart_sales_labels=sales_labels,
                         chart_sales_data=sales_data,
                         chart_category_labels=category_labels,
                         chart_category_data=category_data)

@app.route('/seller/products')
def seller_products():
    if 'user_id' not in session or session.get('account_type') != 'seller':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    seller_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE seller_id = %s ORDER BY created_at DESC', (seller_id,))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('seller/products.html', products=products)


@app.route('/seller/products/toggle/<int:product_id>', methods=['POST'])
def toggle_product_status(product_id):
    if 'user_id' not in session or session.get('account_type') != 'seller':
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    seller_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id, status FROM products WHERE id = %s AND seller_id = %s', (product_id, seller_id))
        product = cursor.fetchone()
        if not product:
            cursor.close(); conn.close()
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        new_status = 'inactive' if product['status'] == 'active' else 'active'
        cursor.execute('UPDATE products SET status = %s WHERE id = %s AND seller_id = %s',
                       (new_status, product_id, seller_id))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({'success': True, 'message': f'Product status set to {new_status}.'})
    except Exception as e:
        conn.rollback()
        cursor.close(); conn.close()
        return jsonify({'success': False, 'message': f'Error updating status: {e}'}), 500

@app.route('/seller/products/add', methods=['POST'])
def add_product():
    if 'user_id' not in session or session.get('account_type') != 'seller':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    seller_id = session['user_id']
    name = request.form.get('name')
    description = request.form.get('description', '')
    price = request.form.get('price')
    stock = request.form.get('stock')
    category = request.form.get('category')
    
    try:
        price = float(price)
        stock = int(stock)
        if price <= 0:
            flash('Invalid price', 'error')
            return redirect(url_for('seller_products'))
        if stock < 0:
            stock = 0
    except (ValueError, TypeError):
        flash('Invalid price or stock format', 'error')
        return redirect(url_for('seller_products'))
    
    brand = request.form.get('brand', '')
    size = request.form.get('size', '')
    color = request.form.get('color', '')
    weight = request.form.get('weight', '')
    sku = request.form.get('sku', '')
    
    # Handle multiple images
    images = request.files.getlist('images')
    image_filenames = []
    if not images or len([f for f in images if f and f.filename]) == 0:
        flash('At least one product image is required', 'error')
        return redirect(url_for('seller_products'))
    upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_PRODUCTS'])
    os.makedirs(upload_path, exist_ok=True)
    for file in images:
        if not file or not file.filename:
            continue
        if not allowed_file(file.filename):
            flash('Invalid image file. Please upload PNG, JPG, JPEG, GIF or WEBP', 'error')
            return redirect(url_for('seller_products'))
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        image_filenames.append(unique_filename)
        print(f"✓ Image saved: {file_path}")
    cover_image = image_filenames[0]
    
    # Save product and its images (no variants)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert product
        cursor.execute('''
            INSERT INTO products (seller_id, name, description, price, stock, category, 
                                brand, size, color, weight, sku, image, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (seller_id, name, description, price, stock, category, 
              brand, size, color, weight, sku, cover_image, 'active'))
        product_id = cursor.lastrowid
        
        # Insert additional images into product_images (including cover)
        for img in image_filenames:
            cursor.execute('INSERT INTO product_images (product_id, image) VALUES (%s, %s)', (product_id, img))
        
        conn.commit()
        flash('Product added successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding product: {str(e)}', 'error')
        print(f"✗ Database error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('seller_products'))

@app.route('/seller/products/edit/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('account_type') != 'seller':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    seller_id = session['user_id']
    name = request.form.get('name')
    description = request.form.get('description', '')
    price = request.form.get('price')
    stock = request.form.get('stock')
    category = request.form.get('category')
    status = request.form.get('status', 'active')
    
    try:
        price = float(price)
        stock = int(stock)
        if price <= 0:
            flash('Invalid price', 'error')
            return redirect(url_for('seller_products'))
        if stock < 0:
            stock = 0
    except (ValueError, TypeError):
        flash('Invalid price or stock format', 'error')
        return redirect(url_for('seller_products'))
    # Append new images if provided
    new_images = request.files.getlist('new_images')
    new_image_filenames = []
    upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_PRODUCTS'])
    os.makedirs(upload_path, exist_ok=True)
    for file in new_images:
        if not file or not file.filename:
            continue
        if not allowed_file(file.filename):
            flash('Invalid image file in upload', 'error')
            return redirect(url_for('seller_products'))
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        new_image_filenames.append(unique_filename)
        print(f"✓ New image saved: {file_path}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE products 
            SET name=%s, description=%s, price=%s, stock=GREATEST(%s,0), category=%s, status=%s
            WHERE id=%s AND seller_id=%s
        ''', (name, description, price, stock, category, status, product_id, seller_id))
        
        # Save new images to product_images
        for img in new_image_filenames:
            cursor.execute('INSERT INTO product_images (product_id, image) VALUES (%s, %s)', (product_id, img))
        
        conn.commit()
        flash('Product updated successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating product: {str(e)}', 'error')
        print(f"✗ Update error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('seller_products'))

@app.route('/seller/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session or session.get('account_type') != 'seller':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    seller_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('SELECT image FROM products WHERE id = %s AND seller_id = %s', 
                      (product_id, seller_id))
        product = cursor.fetchone()
        
        if product:
            if product['image']:
                image_path = os.path.join(app.root_path, 
                                        app.config['UPLOAD_FOLDER_PRODUCTS'], 
                                        product['image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"✓ Deleted image: {image_path}")
            
            cursor.execute('DELETE FROM products WHERE id = %s AND seller_id = %s', 
                          (product_id, seller_id))
            conn.commit()
            flash('Product deleted successfully!', 'success')
        else:
            flash('Product not found or access denied', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
        print(f"✗ Delete error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('seller_products'))

@app.route('/seller/orders')
def seller_orders():
    if 'user_id' not in session or session.get('account_type') != 'seller':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    seller_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT o.*, 
               p.name as product_name,
               u.first_name, u.last_name, u.email, u.phone
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON o.buyer_id = u.id
        WHERE o.seller_id = %s
        ORDER BY o.created_at DESC
    ''', (seller_id,))
    orders = cursor.fetchall()

    status_counts = {
        'pending': 0,
        'processing': 0,
        'completed': 0,
        'cancelled': 0,
    }
    for o in orders:
        st = (o.get('status') or '').lower()
        if st in status_counts:
            status_counts[st] += 1

    cursor.close()
    conn.close()
    
    return render_template('seller/orders.html', orders=orders, status_counts=status_counts)

@app.route('/seller/orders/update/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if 'user_id' not in session or session.get('account_type') != 'seller':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    seller_id = session['user_id']
    new_status = request.form.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch current order info
    cursor.execute('SELECT product_id, quantity, status, stock_deducted FROM orders WHERE id=%s AND seller_id=%s', (order_id, seller_id))
    order = cursor.fetchone()
    if not order:
        cursor.close(); conn.close()
        flash('Order not found', 'error')
        return redirect(url_for('seller_orders'))
    
    try:
        # If moving to processing (being shipped) and not yet deducted, deduct stock now
        if new_status == 'processing' and (order.get('stock_deducted') in (0, None)):
            cur2 = conn.cursor()
            # Deduct only if enough stock remains, atomically
            cur2.execute('UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s', (order['quantity'], order['product_id'], order['quantity']))
            if cur2.rowcount == 0:
                # Not enough stock to ship
                conn.rollback()
                cur2.close()
                cursor.close(); conn.close()
                flash('Cannot move to processing: insufficient stock to fulfill this order.', 'error')
                return redirect(url_for('seller_orders'))
            # Mark order deducted and update status
            cur2.execute('UPDATE orders SET status=%s, stock_deducted=1 WHERE id=%s AND seller_id=%s', (new_status, order_id, seller_id))
            conn.commit()
            cur2.close()
        else:
            cursor2 = conn.cursor()
            cursor2.execute('UPDATE orders SET status=%s WHERE id=%s AND seller_id=%s', (new_status, order_id, seller_id))
            conn.commit()
            cursor2.close()
    except Exception as e:
        conn.rollback()
        cursor.close(); conn.close()
        flash(f'Failed to update status: {e}', 'error')
        return redirect(url_for('seller_orders'))
    
    cursor.close()
    conn.close()
    
    flash(f'Order status updated to {new_status}!', 'success')
    return redirect(url_for('seller_orders'))

# ========================================
# RIDER ROUTES
# ========================================
@app.route('/rider')
def rider():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if session.get('account_type') != 'rider':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))
    
    return render_template('rider/dashboard.html')

# ========================================
# ADMIN ROUTES
# ========================================
@app.route('/admin')
def admin():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if session.get('account_type') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('landing'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ---- High-level metrics ----
    # Total users
    cursor.execute('SELECT COUNT(*) AS total FROM users')
    total_users = cursor.fetchone()['total'] or 0

    # Users by role
    cursor.execute('SELECT account_type, COUNT(*) AS cnt FROM users GROUP BY account_type')
    role_rows = cursor.fetchall()
    users_by_role = {row['account_type']: row['cnt'] for row in role_rows}

    # Products metrics
    cursor.execute('SELECT COUNT(*) AS total FROM products')
    total_products = cursor.fetchone()['total'] or 0

    cursor.execute("SELECT COUNT(*) AS total FROM products WHERE status = 'active'")
    active_products = cursor.fetchone()['total'] or 0

    # Orders metrics (overall)
    cursor.execute('SELECT COUNT(*) AS total, COALESCE(SUM(total_price),0) AS revenue FROM orders')
    orders_row = cursor.fetchone()
    total_orders = orders_row['total'] or 0
    total_revenue = float(orders_row['revenue'] or 0)

    # Orders status counts (global)
    cursor.execute('SELECT status, COUNT(*) AS cnt FROM orders GROUP BY status')
    status_rows = cursor.fetchall()
    order_status_counts = {
        'pending': 0,
        'processing': 0,
        'completed': 0,
        'cancelled': 0,
    }
    for row in status_rows:
        st = (row.get('status') or '').lower()
        if st in order_status_counts:
            order_status_counts[st] = row['cnt']

    pending_orders_count = order_status_counts.get('pending', 0)

    # Orders metrics (last 7 days)
    last_7_start = datetime.now() - timedelta(days=7)
    cursor.execute(
        'SELECT COUNT(*) AS total, COALESCE(SUM(total_price),0) AS revenue '\
        'FROM orders WHERE created_at >= %s',
        (last_7_start,)
    )
    last7 = cursor.fetchone()
    orders_last_7 = last7['total'] or 0
    revenue_last_7 = float(last7['revenue'] or 0)

    # Daily orders for chart (last 30 days)
    last_30_start = datetime.now() - timedelta(days=30)
    cursor.execute('''
        SELECT DATE(created_at) AS day, COUNT(*) AS total
        FROM orders
        WHERE created_at >= %s
        GROUP BY DATE(created_at)
        ORDER BY day
    ''', (last_30_start,))
    daily_rows = cursor.fetchall()
    daily_order_labels = [row['day'].strftime('%b %d') for row in daily_rows]
    daily_order_counts = [row['total'] for row in daily_rows]

    # Pending users list (existing functionality)
    cursor.execute('''
        SELECT id, first_name, last_name, email, account_type, phone, 
               region_name, province_name, municipality_name, barangay_name, street, zip_code,
               valid_id, created_at, is_google_user, email_verified
        FROM users 
        WHERE status = 'pending' AND email_verified = 1
        ORDER BY created_at DESC
    ''')
    pending_users = cursor.fetchall()

    # Low-stock products (e.g. stock <= 5) for highlight tile and quick link
    cursor.execute('''
        SELECT id, name, stock, seller_id
        FROM products
        WHERE stock IS NOT NULL AND stock <= 5 AND status = 'active'
        ORDER BY stock ASC, created_at DESC
        LIMIT 10
    ''')
    low_stock_products = cursor.fetchall()

    # Recent high-value orders (e.g. top 5 by total_price)
    cursor.execute('''
        SELECT o.order_number, o.total_price, o.status, o.created_at,
               u.first_name AS buyer_first_name, u.last_name AS buyer_last_name
        FROM orders o
        JOIN users u ON o.buyer_id = u.id
        ORDER BY o.total_price DESC
        LIMIT 5
    ''')
    recent_high_value_orders = cursor.fetchall()

    cursor.close()
    conn.close()

    admin_stats = {
        'total_users': total_users,
        'users_by_role': {
            'buyer': users_by_role.get('buyer', 0),
            'seller': users_by_role.get('seller', 0),
            'rider': users_by_role.get('rider', 0),
            'admin': users_by_role.get('admin', 0),
        },
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders_last_7': orders_last_7,
        'revenue_last_7': revenue_last_7,
        'pending_users_count': len(pending_users),
        'order_status_counts': order_status_counts,
        'pending_orders_count': pending_orders_count,
        'daily_order_labels': daily_order_labels,
        'daily_order_counts': daily_order_counts,
        'low_stock_count': len(low_stock_products),
    }
    
    return render_template(
        'admin/dashboard.html',
        pending_users=pending_users,
        admin_stats=admin_stats,
        low_stock_products=low_stock_products,
        recent_high_value_orders=recent_high_value_orders,
        admin_active='dashboard',
    )

@app.route('/admin/approve/<int:user_id>')
def approve_user(user_id):
    if 'user_id' not in session or session.get('account_type') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = %s WHERE id = %s', ('approved', user_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('User approved successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:user_id>')
def reject_user(user_id):
    if 'user_id' not in session or session.get('account_type') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = %s WHERE id = %s', ('rejected', user_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('User rejected', 'info')
    return redirect(url_for('admin'))


# ========================================
# ADMIN - USER MANAGEMENT
# ========================================
@app.route('/admin/users')
def admin_users():
    """Admin view of all users with filters by role, status and search."""
    if 'user_id' not in session or session.get('account_type') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    role = request.args.get('role', '').strip()  # buyer/seller/rider/admin
    status = request.args.get('status', '').strip()  # pending/approved/rejected
    q = request.args.get('q', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
        SELECT id, first_name, last_name, email, account_type, status,
               phone, created_at, email_verified
        FROM users
        WHERE 1=1
    '''
    params = []

    if role:
        query += ' AND account_type = %s'
        params.append(role)
    if status:
        query += ' AND status = %s'
        params.append(status)
    if q:
        like = f"%{q}%"
        query += ' AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)'
        params.extend([like, like, like])

    query += ' ORDER BY created_at DESC'
    cursor.execute(query, tuple(params))
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/users.html',
                           users=users,
                           filter_role=role,
                           filter_status=status,
                           search_query=q)


@app.route('/admin/users/status/<int:user_id>', methods=['POST'])
def admin_update_user_status(user_id):
    """Update a user's status (pending/approved/rejected) from admin panel."""
    if 'user_id' not in session or session.get('account_type') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    new_status = request.form.get('status', '').strip()
    if new_status not in ('pending', 'approved', 'rejected'):
        flash('Invalid status value', 'error')
        return redirect(url_for('admin_users'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = %s WHERE id = %s', (new_status, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'User status updated to {new_status}.', 'success')
    return redirect(url_for('admin_users'))


# ========================================
# ADMIN - PRODUCT MANAGEMENT
# ========================================
@app.route('/admin/products')
def admin_products():
    """Admin view of all products with filters and status toggle."""
    if 'user_id' not in session or session.get('account_type') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    status = request.args.get('status', '').strip()  # active/inactive
    category = request.args.get('category', '').strip()
    q = request.args.get('q', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
        SELECT p.*, u.first_name AS seller_name, u.last_name AS seller_lastname
        FROM products p
        JOIN users u ON p.seller_id = u.id
        WHERE 1=1
    '''
    params = []

    if status:
        query += ' AND p.status = %s'
        params.append(status)
    if category:
        query += ' AND p.category = %s'
        params.append(category)
    if q:
        like = f"%{q}%"
        query += ' AND (p.name LIKE %s OR p.description LIKE %s)'
        params.extend([like, like])

    query += ' ORDER BY p.created_at DESC'
    cursor.execute(query, tuple(params))
    products = cursor.fetchall()

    # Categories list (same as landing)
    categories = [
        'Suits & Blazers',
        'Casual Shirts & Pants',
        'Outerwear & Jackets',
        'Activewear & Fitness Gear',
        'Shoes & Accessories',
        'Grooming Products',
    ]

    cursor.close()
    conn.close()

    return render_template('admin/products.html',
                           products=products,
                           filter_status=status,
                           filter_category=category,
                           search_query=q,
                           categories=categories)


@app.route('/admin/products/status/<int:product_id>', methods=['POST'])
def admin_update_product_status(product_id):
    """Toggle product status between active and inactive from admin panel."""
    if 'user_id' not in session or session.get('account_type') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('login'))

    new_status = request.form.get('status', '').strip()
    if new_status not in ('active', 'inactive'):
        flash('Invalid product status value', 'error')
        return redirect(url_for('admin_products'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET status = %s WHERE id = %s', (new_status, product_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Product status updated to {new_status}.', 'success')
    return redirect(url_for('admin_products'))

# ========================================
# GOOGLE AUTH ROUTES
# ========================================
@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            email = user_info['email']
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if user:
                if not user['email_verified']:
                    cursor.execute('UPDATE users SET email_verified = 1 WHERE id = %s', (user['id'],))
                    conn.commit()
                
                status = user['status']
                account_type = user['account_type']
                
                if status == 'pending':
                    cursor.close()
                    conn.close()
                    flash('Your account is pending admin approval. Please wait.', 'warning')
                    return redirect(url_for('login'))
                elif status == 'rejected':
                    cursor.close()
                    conn.close()
                    flash('Your account has been rejected. Please contact support.', 'error')
                    return redirect(url_for('login'))
                elif status == 'approved':
                    session['user_id'] = user['id']
                    session['email'] = user['email']
                    session['account_type'] = account_type
                    session['first_name'] = user['first_name']
                    cursor.close()
                    conn.close()
                    flash('Login successful!', 'success')
                    
                    if account_type == 'buyer':
                        return redirect(url_for('buyer'))
                    elif account_type == 'seller':
                        return redirect(url_for('seller_dashboard'))
                    elif account_type == 'rider':
                        return redirect(url_for('rider'))
                    elif account_type == 'admin':
                        return redirect(url_for('admin'))
                    else:
                        return redirect(url_for('landing'))
            else:
                session['google_email'] = email
                session['google_first_name'] = first_name
                session['google_last_name'] = last_name
                cursor.close()
                conn.close()
                flash('Please complete your profile to continue', 'info')
                return redirect(url_for('complete_google_signup'))
                
    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/signup/google/complete', methods=['GET', 'POST'])
def complete_google_signup():
    if 'google_email' not in session:
        flash('Invalid access', 'error')
        return redirect(url_for('signup'))
    
    if request.method == 'POST':
        account_type = request.form['account_type']
        phone = request.form['phone']
        
        region_code = request.form.get('region', '')
        province_code = request.form.get('province', '')
        municipality_code = request.form.get('municipality', '')
        barangay_code = request.form.get('barangay', '')
        street = request.form.get('street', '')
        zip_code = request.form.get('zip_code', '')
        
        region_name = get_psgc_name('regions', region_code)
        province_name = get_psgc_name('provinces', province_code)
        municipality_name = get_psgc_name('cities-municipalities', municipality_code)
        barangay_name = get_psgc_name('barangays', barangay_code)
        
        # Optional seller/rider fields
        store_name = request.form.get('store_name', '')
        product_category = request.form.get('product_category', '')
        business_permit = request.files.get('business_permit')
        business_permit_filename = None
        if business_permit and business_permit.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            business_permit_filename = f"{timestamp}_{secure_filename(business_permit.filename)}"
            business_permit_path = os.path.join(uploads_folder, business_permit_filename)
            business_permit.save(business_permit_path)
        
        orcr_image = request.files.get('orcr_image')
        orcr_image_filename = None
        if orcr_image and orcr_image.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            orcr_image_filename = f"{timestamp}_{secure_filename(orcr_image.filename)}"
            orcr_image_path = os.path.join(uploads_folder, orcr_image_filename)
            orcr_image.save(orcr_image_path)
        
        vehicle_plate_image = request.files.get('vehicle_plate_image')
        vehicle_plate_image_filename = None
        if vehicle_plate_image and vehicle_plate_image.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            vehicle_plate_image_filename = f"{timestamp}_{secure_filename(vehicle_plate_image.filename)}"
            vehicle_plate_image_path = os.path.join(uploads_folder, vehicle_plate_image_filename)
            vehicle_plate_image.save(vehicle_plate_image_path)
        
        valid_id = request.files.get('valid_id')
        valid_id_filename = None
        if valid_id and valid_id.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            valid_id_filename = f"{timestamp}_{secure_filename(valid_id.filename)}"
            valid_id_path = os.path.join(uploads_folder, valid_id_filename)
            valid_id.save(valid_id_path)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO users (first_name, last_name, email, password, account_type, phone, 
                             region_code, region_name, province_code, province_name, 
                             municipality_code, municipality_name, barangay_code, barangay_name, 
                             street, zip_code, valid_id, store_name, product_category, business_permit, 
                             orcr_image, vehicle_plate_image, is_google_user, email_verified, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            session['google_first_name'],
            session['google_last_name'],
            session['google_email'],
            'GOOGLE_AUTH',
            account_type,
            phone,
            region_code, region_name,
            province_code, province_name,
            municipality_code, municipality_name,
            barangay_code, barangay_name,
            street, zip_code,
            valid_id_filename,
            store_name if account_type == 'seller' else None,
            product_category if account_type == 'seller' else None,
            business_permit_filename if account_type == 'seller' else None,
            orcr_image_filename if account_type == 'rider' else None,
            vehicle_plate_image_filename if account_type == 'rider' else None,
            1, 1, 'pending'
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        session.pop('google_email', None)
        session.pop('google_first_name', None)
        session.pop('google_last_name', None)
        
        flash('Registration submitted! Your account is pending admin approval.', 'success')
        return redirect(url_for('login'))
    
    return render_template('complete_google_signup.html',
                         email=session['google_email'],
                         first_name=session['google_first_name'],
                         last_name=session['google_last_name'])

# ========================================
# LOGIN & SIGNUP ROUTES
# ========================================
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Please enter your email address', 'error')
            return redirect(url_for('forgot_password'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, first_name, password FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close(); conn.close()
            flash('If that email is registered, an OTP has been sent.', 'info')
            return redirect(url_for('forgot_password'))
        
        # Optional: block Google-only accounts from password reset
        if user['password'] == 'GOOGLE_AUTH':
            cursor.close(); conn.close()
            flash('This account uses Google Sign-In. Use Google to log in.', 'warning')
            return redirect(url_for('login'))
        
        otp_code = generate_otp()
        otp_created_at = datetime.now()
        cursor2 = conn.cursor()
        cursor2.execute('UPDATE users SET otp_code=%s, otp_created_at=%s WHERE id=%s',
                       (otp_code, otp_created_at, user['id']))
        conn.commit()
        cursor2.close(); cursor.close(); conn.close()
        
        send_password_reset_otp_email(email, otp_code, user.get('first_name'))
        session['reset_email'] = email
        flash('OTP sent to your email. Please check your inbox.', 'success')
        return redirect(url_for('reset_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        flash('Invalid access', 'error')
        return redirect(url_for('forgot_password'))
    
    email = session['reset_email']
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not otp or not new_password:
            flash('Please enter OTP and new password', 'error')
            return redirect(url_for('reset_password'))
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('reset_password'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, first_name, otp_code, otp_created_at FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        if not user:
            cursor.close(); conn.close()
            flash('User not found', 'error')
            return redirect(url_for('forgot_password'))
        
        if not user['otp_code'] or otp != user['otp_code']:
            cursor.close(); conn.close()
            flash('Invalid OTP code', 'error')
            return redirect(url_for('reset_password'))
        if is_otp_expired(user['otp_created_at']):
            cursor.close(); conn.close()
            flash('OTP has expired. Please request a new one.', 'error')
            return redirect(url_for('forgot_password'))
        
        cursor2 = conn.cursor()
        cursor2.execute('''
            UPDATE users SET password=%s, otp_code=NULL, otp_created_at=NULL WHERE id=%s
        ''', (new_password, user['id']))
        conn.commit()
        cursor2.close(); cursor.close(); conn.close()
        
        session.pop('reset_email', None)
        flash('Password has been reset. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            if user['password'] == 'GOOGLE_AUTH':
                flash('Please use Google Sign In for this account', 'error')
                return redirect(url_for('login'))
            
            if user['password'] == password:
                if user['account_type'] != 'admin' and not user.get('email_verified', 0):
                    flash('Please verify your email first. Check your inbox for the OTP code.', 'warning')
                    session['verify_email'] = user['email']
                    session['verify_user_id'] = user['id']
                    return redirect(url_for('verify_otp'))
                
                status = user['status']
                
                if status == 'pending':
                    flash('Your account is pending admin approval. Please wait.', 'warning')
                    return redirect(url_for('login'))
                elif status == 'rejected':
                    flash('Your account has been rejected. Please contact support.', 'error')
                    return redirect(url_for('login'))
                elif status == 'approved':
                    session['user_id'] = user['id']
                    session['email'] = user['email']
                    session['account_type'] = user['account_type']
                    session['first_name'] = user['first_name']
                    flash('Login successful!', 'success')
                    
                    account_type = user['account_type']
                    if account_type == 'buyer':
                        return redirect(url_for('buyer'))
                    elif account_type == 'seller':
                        return redirect(url_for('seller_dashboard'))
                    elif account_type == 'rider':
                        return redirect(url_for('rider'))
                    elif account_type == 'admin':
                        return redirect(url_for('admin'))
                    else:
                        return redirect(url_for('landing'))
            else:
                flash('Invalid login credentials', 'error')
                return redirect(url_for('login'))
        else:
            flash('Invalid login credentials', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        account_type = request.form['account_type']
        phone = request.form['phone']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('signup'))

        if not validate_email(email):
            flash('Invalid email address!', 'error')
            return redirect(url_for('signup'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            flash('Email already registered!', 'error')
            return redirect(url_for('signup'))

        region_code = request.form.get('region', '')
        province_code = request.form.get('province', '')
        municipality_code = request.form.get('municipality', '')
        barangay_code = request.form.get('barangay', '')
        street = request.form.get('street', '')
        zip_code = request.form.get('zip_code', '')
        
        region_name = get_psgc_name('regions', region_code)
        province_name = get_psgc_name('provinces', province_code)
        municipality_name = get_psgc_name('cities-municipalities', municipality_code)
        barangay_name = get_psgc_name('barangays', barangay_code)

        # Optional seller/rider fields
        store_name = request.form.get('store_name', '')
        product_category = request.form.get('product_category', '')
        business_permit = request.files.get('business_permit')
        business_permit_filename = None
        if business_permit and business_permit.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            business_permit_filename = f"{timestamp}_{secure_filename(business_permit.filename)}"
            business_permit_path = os.path.join(uploads_folder, business_permit_filename)
            business_permit.save(business_permit_path)

        orcr_image = request.files.get('orcr_image')
        orcr_image_filename = None
        if orcr_image and orcr_image.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            orcr_image_filename = f"{timestamp}_{secure_filename(orcr_image.filename)}"
            orcr_image_path = os.path.join(uploads_folder, orcr_image_filename)
            orcr_image.save(orcr_image_path)

        vehicle_plate_image = request.files.get('vehicle_plate_image')
        vehicle_plate_image_filename = None
        if vehicle_plate_image and vehicle_plate_image.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            vehicle_plate_image_filename = f"{timestamp}_{secure_filename(vehicle_plate_image.filename)}"
            vehicle_plate_image_path = os.path.join(uploads_folder, vehicle_plate_image_filename)
            vehicle_plate_image.save(vehicle_plate_image_path)

        valid_id = request.files.get('valid_id')
        valid_id_filename = None
        if valid_id and valid_id.filename:
            uploads_folder = 'uploads'
            os.makedirs(uploads_folder, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            valid_id_filename = f"{timestamp}_{secure_filename(valid_id.filename)}"
            valid_id_path = os.path.join(uploads_folder, valid_id_filename)
            valid_id.save(valid_id_path)

        # Server-side minimal checks for required docs by account type
        if account_type == 'seller' and (not store_name or not product_category or not business_permit_filename):
            cursor.close(); conn.close()
            flash('Seller accounts require Store Name, Product Category, and Business Permit.', 'error')
            return redirect(url_for('signup'))
        if account_type == 'rider' and (not orcr_image_filename or not vehicle_plate_image_filename):
            cursor.close(); conn.close()
            flash('Rider accounts require ORCR and Vehicle Plate Photo.', 'error')
            return redirect(url_for('signup'))

        otp_code = generate_otp()
        otp_created_at = datetime.now()

        cursor.execute(''' 
            INSERT INTO users (first_name, last_name, email, password, account_type, phone, 
                             region_code, region_name, province_code, province_name, 
                             municipality_code, municipality_name, barangay_code, barangay_name, 
                             street, zip_code, valid_id, store_name, product_category, business_permit,
                             orcr_image, vehicle_plate_image, is_google_user, email_verified, 
                             otp_code, otp_created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            first_name, last_name, email, password, account_type, phone,
            region_code, region_name,
            province_code, province_name,
            municipality_code, municipality_name,
            barangay_code, barangay_name,
            street, zip_code,
            valid_id_filename,
            store_name if account_type == 'seller' else None,
            product_category if account_type == 'seller' else None,
            business_permit_filename if account_type == 'seller' else None,
            orcr_image_filename if account_type == 'rider' else None,
            vehicle_plate_image_filename if account_type == 'rider' else None,
            0, 0, otp_code, otp_created_at, 'pending'
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        if send_otp_email(email, otp_code, first_name):
            session['verify_email'] = email
            session['verify_user_id'] = user_id
            flash('Please check your email for the OTP code to verify your account.', 'info')
            return redirect(url_for('verify_otp'))
        else:
            flash('Account created but error sending verification email. Please contact support.', 'warning')
            return redirect(url_for('login'))

    return render_template('signup.html')

# ========================================
# OTP VERIFICATION ROUTES
# ========================================
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'verify_email' not in session:
        flash('Invalid access', 'error')
        return redirect(url_for('signup'))
    
    email = session['verify_email']
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, first_name, otp_code, otp_created_at, email_verified 
            FROM users 
            WHERE email = %s
        ''', (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            flash('User not found', 'error')
            return redirect(url_for('signup'))
        
        if user['email_verified']:
            cursor.close()
            conn.close()
            session.pop('verify_email', None)
            session.pop('verify_user_id', None)
            flash('Email already verified! Please login.', 'success')
            return redirect(url_for('login'))
        
        if is_otp_expired(user['otp_created_at']):
            cursor.close()
            conn.close()
            flash('OTP has expired. Please request a new one.', 'error')
            return render_template('verify_otp.html', email=email, expired=True)
        
        if entered_otp == user['otp_code']:
            cursor.execute('''
                UPDATE users 
                SET email_verified = 1, otp_code = NULL, otp_created_at = NULL 
                WHERE id = %s
            ''', (user['id'],))
            conn.commit()
            cursor.close()
            conn.close()
            
            session.pop('verify_email', None)
            session.pop('verify_user_id', None)
            
            flash('Email verified successfully! Your account is pending admin approval.', 'success')
            return redirect(url_for('login'))
        else:
            cursor.close()
            conn.close()
            flash('Invalid OTP code. Please try again.', 'error')
            return render_template('verify_otp.html', email=email)
    
    return render_template('verify_otp.html', email=email)

@app.route('/resend-otp')
def resend_otp():
    if 'verify_email' not in session:
        flash('Invalid access', 'error')
        return redirect(url_for('signup'))
    
    email = session['verify_email']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, first_name, email_verified FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        flash('User not found', 'error')
        return redirect(url_for('signup'))
    
    if user['email_verified']:
        cursor.close()
        conn.close()
        flash('Email already verified!', 'info')
        return redirect(url_for('login'))
    
    new_otp = generate_otp()
    new_otp_created_at = datetime.now()
    
    cursor.execute('''
        UPDATE users 
        SET otp_code = %s, otp_created_at = %s 
        WHERE id = %s
    ''', (new_otp, new_otp_created_at, user['id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    if send_otp_email(email, new_otp, user['first_name']):
        flash('New OTP sent to your email!', 'success')
    else:
        flash('Error sending OTP. Please try again.', 'error')
    
    return redirect(url_for('verify_otp'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('landing'))

if __name__ == "__main__":
    app.run(debug=True)
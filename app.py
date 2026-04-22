from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Initialize database
def init_db():
    """Create the gaiyang.db database with Products, Orders, and OrderItems tables"""
    db_path = 'gaiyang.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_category TEXT NOT NULL,
            product_price REAL NOT NULL,
            product_description TEXT,
            product_stock INTEGER DEFAULT 0,
            product_image_url TEXT,
            product_is_available BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            order_customer_name TEXT NOT NULL,
            order_total_price REAL NOT NULL,
            order_status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Create OrderItems joining table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderItems (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_item_order_id INTEGER NOT NULL,
            order_item_product_id INTEGER NOT NULL,
            order_item_quantity INTEGER NOT NULL,
            order_item_price_at_time REAL NOT NULL,
            FOREIGN KEY (order_item_order_id) REFERENCES Orders(order_id),
            FOREIGN KEY (order_item_product_id) REFERENCES Products(product_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

# Initialize database on app startup
init_db()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page - display all products"""
    conn = sqlite3.connect('gaiyang.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Add product
@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    """Add a new product - GET shows form, POST saves to database"""
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_category = request.form.get('product_category')
        product_price = request.form.get('product_price')
        product_stock = request.form.get('product_stock')
        product_image_url = request.form.get('product_image_url')
        product_description = request.form.get('product_description')
        
        # Validate inputs
        if not product_name or not product_category or not product_price or not product_stock:
            return render_template('add_product.html', error='All required fields must be filled!')
        
        try:
            product_price = float(product_price)
            product_stock = int(product_stock)
            conn = sqlite3.connect('gaiyang.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Products (product_name, product_category, product_price, product_stock, product_image_url, product_description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (product_name, product_category, product_price, product_stock, product_image_url, product_description))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except ValueError:
            return render_template('add_product.html', error='Price must be a valid number and Stock must be an integer!')
    
    # GET request - show the form
    return render_template('add_product.html')

# Edit product
@app.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit an existing product - GET shows form, POST updates database"""
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_category = request.form.get('product_category')
        product_price = request.form.get('product_price')
        product_stock = request.form.get('product_stock')
        product_image_url = request.form.get('product_image_url')
        product_description = request.form.get('product_description')
        
        # Validate inputs
        if not product_name or not product_category or not product_price or not product_stock:
            return render_template('edit_product.html', error='All required fields must be filled!', product_id=product_id)
        
        try:
            product_price = float(product_price)
            product_stock = int(product_stock)
            conn = sqlite3.connect('gaiyang.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Products 
                SET product_name = ?, product_category = ?, product_price = ?, product_stock = ?, product_image_url = ?, product_description = ?
                WHERE product_id = ?
            ''', (product_name, product_category, product_price, product_stock, product_image_url, product_description, product_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except ValueError:
            return render_template('edit_product.html', error='Price must be a valid number and Stock must be an integer!', product_id=product_id)
    
    # GET request - fetch product and show form
    conn = sqlite3.connect('gaiyang.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Products WHERE product_id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return redirect(url_for('index'))
    
    return render_template('edit_product.html', product=product)

# Delete product
@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product from database"""
    conn = sqlite3.connect('gaiyang.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Products WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


"""Cupcakes Gourmet – aplicação didática PIT II. Pagamentos são simulados."""
import os
import sqlite3
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-altere-esta-chave'), DATABASE=os.environ.get('DATABASE', str(BASE/'cupcakes.db')), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')

PRODUCTS = [(1,'Chocolate Belga','Cupcake com ganache cremosa de chocolate belga',12.90,'🍫'),(2,'Red Velvet','Massa aveludada e cobertura de cream cheese',14.50,'❤️'),(3,'Baunilha & Morango','Baunilha, recheio de morango e chantilly',13.90,'🍓'),(4,'Doce de Leite','Cupcake com doce de leite e confeitos',13.50,'🧁'),(5,'Limão Siciliano','Massa cítrica e cobertura delicada',13.90,'🍋'),(6,'Cookies & Cream','Chocolate com cobertura de biscoito',15.00,'🍪'),(7,'Coco Cremoso','Massa macia de coco com cobertura cremosa e coco ralado',13.90,'🥥'),(8,'Churros','Massa com canela e cobertura de doce de leite',14.90,'✨')]

def db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE']); g.db.row_factory = sqlite3.Row; g.db.execute('PRAGMA foreign_keys=ON')
    return g.db

@app.teardown_appcontext
def close(_):
    conn=g.pop('db',None)
    if conn: conn.close()

def init_db():
    with app.app_context():
        db().executescript('''
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents>0), emoji TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id), delivery_address TEXT NOT NULL, payment_method TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Recebido', total_cents INTEGER NOT NULL CHECK(total_cents>=0), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id), product_id INTEGER NOT NULL REFERENCES products(id), quantity INTEGER NOT NULL CHECK(quantity>0), unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents>0));
''')
        db().executemany('INSERT OR IGNORE INTO products(id,name,description,price_cents,emoji) VALUES(?,?,?,?,?)',[(i,n,d,round(p*100),e) for i,n,d,p,e in PRODUCTS]); db().commit()

def current_user():
    return db().execute('SELECT id,name,email FROM users WHERE id=?',(session.get('user_id',-1),)).fetchone()

def login_required(fn):
    @wraps(fn)
    def wrapped(*args,**kwargs):
        if not current_user(): flash('Entre na sua conta para continuar.','error'); return redirect(url_for('login'))
        return fn(*args,**kwargs)
    return wrapped

@app.context_processor
def context():
    return {'viewer':current_user(),'cart_count':sum(int(q) for q in session.get('cart',{}).values())}

@app.route('/')
def index():
    return render_template('index.html',products=db().execute('SELECT * FROM products WHERE active=1').fetchall())

@app.route('/cadastro',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').lower().strip(); password=request.form.get('password','')
        if len(name)<2 or '@' not in email or len(password)<8: flash('Informe nome, e-mail válido e senha com ao menos 8 caracteres.','error')
        else:
            try:
                cursor=db().execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',(name,email,generate_password_hash(password)));db().commit();cart=session.get('cart',{}).copy();session.clear();session['user_id']=cursor.lastrowid;session['cart']=cart;flash('Cadastro realizado com sucesso!','success');return redirect(url_for('index'))
            except sqlite3.IntegrityError: flash('Este e-mail já está cadastrado.','error')
    return render_template('auth.html',title='Criar conta',register=True)

@app.route('/entrar',methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=db().execute('SELECT * FROM users WHERE email=?',(request.form.get('email','').lower().strip(),)).fetchone()
        if user and check_password_hash(user['password_hash'],request.form.get('password','')):
            cart=session.get('cart',{});session.clear();session['user_id']=user['id'];session['cart']=cart;return redirect(url_for('index'))
        flash('E-mail ou senha inválidos.','error')
    return render_template('auth.html',title='Entrar',register=False)

@app.post('/sair')
def logout(): session.clear();flash('Você saiu da conta.','success');return redirect(url_for('index'))

@app.post('/carrinho/adicionar/<int:product_id>')
def add_cart(product_id):
    if not db().execute('SELECT id FROM products WHERE id=? AND active=1',(product_id,)).fetchone():return ('Produto não encontrado',404)
    try: qty=int(request.form.get('quantity','1'))
    except ValueError: qty=0
    if not 1<=qty<=30: flash('Informe de 1 a 30 unidades.','error');return redirect(url_for('index'))
    cart=session.get('cart',{});key=str(product_id);cart[key]=min(30,int(cart.get(key,0))+qty);session['cart']=cart;flash('Produto adicionado ao carrinho.','success');return redirect(url_for('cart'))

def cart_data():
    items=[];total=0
    for key,quantity in session.get('cart',{}).items():
        try: pid=int(key);qty=int(quantity)
        except (ValueError,TypeError): continue
        prod=db().execute('SELECT * FROM products WHERE id=? AND active=1',(pid,)).fetchone()
        if prod and qty>0:
            subtotal=prod['price_cents']*qty;items.append({'product':prod,'quantity':qty,'subtotal':subtotal});total+=subtotal
    return items,total

@app.route('/carrinho')
def cart():
    items,total=cart_data();return render_template('cart.html',items=items,total=total)

@app.post('/carrinho/atualizar/<int:product_id>')
def update_cart(product_id):
    try: qty=int(request.form.get('quantity',0))
    except ValueError: qty=-1
    if not 0<=qty<=30: flash('Quantidade inválida.','error');return redirect(url_for('cart'))
    cart=session.get('cart',{});key=str(product_id)
    if qty==0:cart.pop(key,None)
    elif key in cart:cart[key]=qty
    session['cart']=cart;return redirect(url_for('cart'))

@app.route('/finalizar',methods=['GET','POST'])
@login_required
def checkout():
    items,total=cart_data()
    if not items:flash('Adicione produtos antes de finalizar.','error');return redirect(url_for('index'))
    if request.method=='POST':
        address=request.form.get('address','').strip();payment=request.form.get('payment','')
        if len(address)<10 or payment not in ('Pix simulado','Cartão simulado','Dinheiro na entrega'):
            flash('Informe um endereço completo e uma forma de pagamento.','error')
        else:
            cur=db().execute('INSERT INTO orders(user_id,delivery_address,payment_method,total_cents) VALUES(?,?,?,?)',(session['user_id'],address,payment,total));oid=cur.lastrowid
            db().executemany('INSERT INTO order_items(order_id,product_id,quantity,unit_price_cents) VALUES(?,?,?,?)',[(oid,row['product']['id'],row['quantity'],row['product']['price_cents']) for row in items]);db().commit();session['cart']={};flash(f'Pedido #{oid} recebido! Pagamento apenas simulado.','success');return redirect(url_for('orders'))
    return render_template('checkout.html',items=items,total=total)

@app.route('/pedidos')
@login_required
def orders():
    data=db().execute('SELECT * FROM orders WHERE user_id=? ORDER BY id DESC',(session['user_id'],)).fetchall();
    orders_with_items=[]
    for order in data:
        items=db().execute('''SELECT p.name, p.emoji, oi.quantity, oi.unit_price_cents, p.id AS product_id FROM order_items oi JOIN products p ON p.id=oi.product_id WHERE oi.order_id=? ORDER BY oi.id''',(order['id'],)).fetchall()
        orders_with_items.append({'order':order,'items':items})
    return render_template('orders.html',orders=orders_with_items)

@app.template_filter('brl')
def brl(cents):return f'R$ {cents/100:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

@app.get('/saude')
def health():return jsonify(status='ok')

if __name__=='__main__':
    init_db();app.run(debug=os.environ.get('FLASK_DEBUG')=='1',port=int(os.environ.get('PORT','5000')))

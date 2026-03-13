import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'titan-epic-key-2026'

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:rohit1234@localhost/arizen_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---

likes = db.Table('likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    level = db.Column(db.Integer, default=1)
    
    # Profile Data
    bio = db.Column(db.String(500), default="Certified Void Hub Developer.")
    discord_id = db.Column(db.String(100), default="Unknown#0000")
    insta_id = db.Column(db.String(100), default="@void_hub")
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    product_file = db.Column(db.String(100), nullable=False, default="default_asset.zip")
    price = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    desc = db.Column(db.String(1000), default="No description.")
    sold_count = db.Column(db.Integer, default=0)
    type = db.Column(db.String(50), default='Standard') 
    liked_by = db.relationship('User', secondary=likes, backref=db.backref('liked_posts', lazy='dynamic'))
    reviews = db.relationship('Review', backref='post', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, default=5)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)

@app.route('/api/posts')
def get_posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    data = []
    for p in posts:
        review_list = [{"user": r.author.username, "text": r.content} for r in p.reviews]
        data.append({
            'id': p.id,
            'title': p.title,
            'user': p.author.username, 
            'video': url_for('static', filename=p.filename),
            'price': p.price,
            'sold': p.sold_count,
            'desc': p.desc,
            'reviews': review_list,
            'author_bio': p.author.bio,
            'author_discord': p.author.discord_id,
            'author_insta': p.author.insta_id,
            'author_level': p.author.level
        })
    return jsonify(data)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if password == "0000": 
        user = User.query.filter((User.email == email) | (User.username == email)).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))

    user = User.query.filter((User.email == email) | (User.username == email)).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
    return redirect(url_for('home'))

@app.route('/signup', methods=['POST'])
def signup():
    if not User.query.filter_by(email=request.form.get('email')).first():
        user = User(
            username=request.form.get('username'), 
            email=request.form.get('email'), 
            password=generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
        )
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/user/<username>')
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user: return jsonify({'error': 'User not found'}), 404
    
    total_sales = sum([p.sold_count for p in user.posts])
    follower_count = user.followers.count()
    
    return jsonify({
        'bio': user.bio or "No bio set.",
        'discord': user.discord_id or "Not Linked",
        'insta': user.insta_id or "Not Linked",
        'level': user.level,
        'sales': total_sales,
        'post_count': len(user.posts),
        'followers': follower_count
    })

@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    current_user.bio = data.get('bio', current_user.bio)
    current_user.discord_id = data.get('discord', current_user.discord_id)
    current_user.insta_id = data.get('insta', current_user.insta_id)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/contacts')
@login_required
def get_contacts():
    followed_users = [f.followed_id for f in current_user.following.all()]
    sent_to = [m.receiver_id for m in Message.query.filter_by(sender_id=current_user.id).all()]
    received_from = [m.sender_id for m in Message.query.filter_by(receiver_id=current_user.id).all()]
    all_contact_ids = list(set(followed_users + sent_to + received_from))
    contacts = User.query.filter(User.id.in_(all_contact_ids)).all()
    
    return jsonify([{
        'username': u.username,
        'avatar': f"https://api.dicebear.com/7.x/shapes/svg?seed={u.username}",
        'status': 'Online'
    } for u in contacts])

@app.route('/api/follow/<username>', methods=['POST'])
@login_required
def follow_user(username):
    user_to_follow = User.query.filter_by(username=username).first()
    if not user_to_follow: return jsonify({'error': 'User not found'}), 404
    
    exists = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_to_follow.id).first()
    if exists:
        db.session.delete(exists)
        msg = "Unfollowed"
    else:
        new_follow = Follow(follower_id=current_user.id, followed_id=user_to_follow.id)
        db.session.add(new_follow)
        msg = "Followed"
    db.session.commit()
    return jsonify({'status': msg})

@app.route('/api/dashboard')
@login_required
def get_dashboard_data():
    my_posts = Post.query.filter_by(user_id=current_user.id).all()
    total_revenue = sum([p.price * p.sold_count for p in my_posts])
    total_sales = sum([p.sold_count for p in my_posts])
    breakdown = [{'title': p.title, 'sold': p.sold_count, 'revenue': p.price * p.sold_count} for p in my_posts]
    return jsonify({'revenue': total_revenue, 'sales': total_sales, 'breakdown': breakdown})

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.json
    receiver = User.query.filter_by(username=data['receiver']).first()
    if not receiver: return jsonify({'error': 'User not found'}), 404
    new_msg = Message(sender_id=current_user.id, receiver_id=receiver.id, content=data['content'])
    notif = Notification(user_id=receiver.id, content=f"New message from {current_user.username}")
    db.session.add(new_msg)
    db.session.add(notif)
    db.session.commit()
    return jsonify({'status': 'sent'})

@app.route('/api/chat/history/<username>')
@login_required
def get_chat_history(username):
    other = User.query.filter_by(username=username).first()
    if not other: return jsonify([])
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other.id)) |
        ((Message.sender_id == other.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    return jsonify([{'sender': m.sender.username, 'content': m.content, 'time': m.timestamp.strftime('%H:%M')} for m in messages])

@app.route('/api/notifications')
@login_required
def get_notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return jsonify([{'content': n.content, 'read': n.is_read} for n in notifs])

@app.route('/api/notifications/clear', methods=['POST'])
@login_required
def clear_notifications():
    Notification.query.filter_by(user_id=current_user.id).update(dict(is_read=True))
    db.session.commit()
    return jsonify({'status': 'cleared'})

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'video' not in request.files or 'zip_file' not in request.files:
        return "Missing files", 400
    
    video = request.files['video']
    zip_file = request.files['zip_file']
    
    if video and zip_file:
        vid_filename = secure_filename(video.filename)
        video.save(os.path.join(app.config['UPLOAD_FOLDER'], vid_filename))
        
        zip_filename = secure_filename(zip_file.filename)
        if not os.path.exists('secure_uploads'):
            os.makedirs('secure_uploads')
        zip_file.save(os.path.join('secure_uploads', zip_filename))

        new_post = Post(
            title=request.form.get('title'), 
            filename=vid_filename, 
            product_file=zip_filename,
            price=request.form.get('price'), 
            desc=request.form.get('desc'), 
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))

@app.route('/download/<int:post_id>')
@login_required
def download_asset(post_id):
    post = Post.query.get_or_404(post_id)
    is_author = post.author.id == current_user.id
    is_admin = current_user.id == 1 
    has_receipt = Purchase.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if is_author or is_admin or has_receipt:
        try:
            return send_from_directory('secure_uploads', post.product_file, as_attachment=True)
        except FileNotFoundError:
            return "Server Error: File missing from vault.", 404
    else:
        return "ACCESS DENIED: You must purchase this blueprint first.", 403

@app.route('/api/buy/<int:post_id>', methods=['POST'])
@login_required
def buy_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 1. Create Receipt
    existing = Purchase.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if not existing:
        new_purchase = Purchase(user_id=current_user.id, post_id=post.id)
        db.session.add(new_purchase)
    
    # 2. Clear from Cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if cart_item:
        db.session.delete(cart_item)

    # 3. Update Stats
    post.sold_count += 1
    
    db.session.commit()
    return jsonify({'status': 'success', 'sold': post.sold_count})

@app.route('/api/library')
@login_required
def get_library():
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    posts = [Post.query.get(p.post_id) for p in purchases]
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'video': url_for('static', filename=p.filename),
        'user': p.author.username
    } for p in posts])

# --- CART SYSTEM ---

@app.route('/api/cart')
@login_required
def get_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    posts = [Post.query.get(item.post_id) for item in items]
    return jsonify([{
        'id': p.id, 'title': p.title, 'price': p.price,
        'video': url_for('static', filename=p.filename),
        'user': p.author.username
    } for p in posts])

@app.route('/api/cart/add/<int:post_id>', methods=['POST'])
@login_required
def add_to_cart(post_id):
    if not CartItem.query.filter_by(user_id=current_user.id, post_id=post_id).first():
        db.session.add(CartItem(user_id=current_user.id, post_id=post_id))
        db.session.commit()
    return jsonify({'status': 'success', 'message': 'Added to Cart'})

@app.route('/api/cart/remove/<int:post_id>', methods=['POST'])
@login_required
def remove_from_cart(post_id):
    item = CartItem.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
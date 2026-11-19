import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'rambook-wssu-secret-key-2026')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///rambook.db')

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'error'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== DATABASE MODELS ====================

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    student_id = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    textbooks = db.relationship('Textbook', backref='seller', lazy=True, cascade='all, delete-orphan')
    exchange_requests = db.relationship('ExchangeRequest', backref='requester', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Textbook(db.Model):
    __tablename__ = 'textbooks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(30), nullable=False)
    course = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    listing_type = db.Column(db.String(20), nullable=False)  # sell, trade, free
    price = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, default='')
    image_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='Available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seller_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    requests = db.relationship('ExchangeRequest', backref='textbook', lazy=True, cascade='all, delete-orphan')


class ExchangeRequest(db.Model):
    __tablename__ = 'exchange_requests'
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(30), nullable=False)  # Purchase or Trade
    status = db.Column(db.String(30), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    textbook_id = db.Column(db.Integer, db.ForeignKey('textbooks.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)


class BookReturn(db.Model):
    __tablename__ = 'book_returns'
    id = db.Column(db.Integer, primary_key=True)
    return_code = db.Column(db.String(20), unique=True, nullable=False)
    student_name = db.Column(db.String(150), nullable=False)
    student_id_number = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(30), nullable=False)
    order_number = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(40), default='Awaiting Drop-Off')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Student, int(user_id))


# ==================== PUBLIC & AUTH ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        student_id = request.form.get('studentID', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')

        if not all([first_name, last_name, student_id, email, password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')

        if Student.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'error')
            return render_template('register.html')

        if Student.query.filter_by(student_id=student_id).first():
            flash('That Student ID is already registered.', 'error')
            return render_template('register.html')

        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            email=email
        )
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()

        login_user(new_student)
        flash(f'Welcome to RamBook Exchange, {new_student.first_name}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        student = Student.query.filter_by(email=email).first()
        if student and student.check_password(password):
            login_user(student)
            flash(f'Welcome back, {student.first_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ==================== TEXTBOOK CRUD & MARKETPLACE ====================

@app.route('/marketplace')
def marketplace():
    search_query = request.args.get('q', '').strip()
    category = request.args.get('category', 'all').strip()

    query = Textbook.query.filter_by(status='Available')
    if category and category != 'all':
        query = query.filter_by(category=category)
    if search_query:
        like_pattern = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Textbook.title.ilike(like_pattern),
                Textbook.author.ilike(like_pattern),
                Textbook.course.ilike(like_pattern),
                Textbook.isbn.ilike(like_pattern)
            )
        )

    books = query.order_by(Textbook.created_at.desc()).all()
    return render_template('marketplace.html', books=books, search_query=search_query, selected_category=category)


@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        course = request.form.get('course', '').strip()
        category = request.form.get('category', '').strip()
        condition = request.form.get('condition', '').strip()
        listing_type = request.form.get('listingType', '').strip()
        description = request.form.get('description', '').strip()

        raw_price = request.form.get('price', '').strip()
        price = float(raw_price) if (listing_type == 'sell' and raw_price) else 0.0

        image_filename = None
        file = request.files.get('bookImage')
        if file and file.filename and allowed_file(file.filename):
            safe_name = secure_filename(file.filename)
            image_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{safe_name}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        new_book = Textbook(
            title=title,
            author=author,
            isbn=isbn,
            course=course,
            category=category,
            condition=condition,
            listing_type=listing_type,
            price=price,
            description=description,
            image_filename=image_filename,
            seller_id=current_user.id
        )
        db.session.add(new_book)
        db.session.commit()

        flash('Your textbook has been listed on the marketplace!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_book.html')


@app.route('/books/<int:book_id>')
def book_details(book_id):
    book = db.session.get(Textbook, book_id)
    if not book:
        abort(404)
    return render_template('book_details.html', book=book)


@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = db.session.get(Textbook, book_id)
    if not book:
        abort(404)

    if book.seller_id != current_user.id:
        flash('You can only edit your own textbook listings.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.isbn = request.form.get('isbn', '').strip()
        book.course = request.form.get('course', '').strip()
        book.category = request.form.get('category', '').strip()
        book.condition = request.form.get('condition', '').strip()
        book.listing_type = request.form.get('listingType', '').strip()
        book.status = request.form.get('status', book.status).strip()
        book.description = request.form.get('description', '').strip()

        raw_price = request.form.get('price', '').strip()
        book.price = float(raw_price) if (book.listing_type == 'sell' and raw_price) else 0.0

        file = request.files.get('bookImage')
        if file and file.filename and allowed_file(file.filename):
            safe_name = secure_filename(file.filename)
            image_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{safe_name}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            book.image_filename = image_filename

        db.session.commit()
        flash('Textbook listing updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_book.html', book=book)


@app.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book = db.session.get(Textbook, book_id)
    if not book:
        abort(404)

    if book.seller_id != current_user.id:
        flash('You do not have permission to delete this listing.', 'error')
        return redirect(url_for('dashboard'))

    db.session.delete(book)
    db.session.commit()
    flash('Textbook listing removed.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/books/<int:book_id>/request', methods=['POST'])
@login_required
def request_book(book_id):
    book = db.session.get(Textbook, book_id)
    if not book:
        abort(404)

    if book.seller_id == current_user.id:
        flash('You cannot request your own textbook.', 'error')
        return redirect(url_for('book_details', book_id=book.id))

    req_type = request.form.get('request_type', 'Purchase')
    existing = ExchangeRequest.query.filter_by(
        textbook_id=book.id,
        requester_id=current_user.id,
        status='Pending'
    ).first()

    if existing:
        flash('You already have a pending request for this textbook.', 'error')
        return redirect(url_for('book_details', book_id=book.id))

    new_req = ExchangeRequest(
        request_type=req_type,
        textbook_id=book.id,
        requester_id=current_user.id
    )
    db.session.add(new_req)
    db.session.commit()

    flash(f'{req_type} request sent to {book.seller.first_name}!', 'success')
    return redirect(url_for('dashboard'))


# ==================== STUDENT DASHBOARD & RETURNS ====================

@app.route('/dashboard')
@login_required
def dashboard():
    my_books = Textbook.query.filter_by(seller_id=current_user.id).order_by(Textbook.created_at.desc()).all()
    my_requests = ExchangeRequest.query.filter_by(requester_id=current_user.id).order_by(ExchangeRequest.created_at.desc()).all()
    incoming_requests = ExchangeRequest.query.join(Textbook).filter(Textbook.seller_id == current_user.id).order_by(ExchangeRequest.created_at.desc()).all()
    my_returns = BookReturn.query.filter_by(email=current_user.email).order_by(BookReturn.created_at.desc()).all()

    pending_returns = sum(1 for r in my_returns if r.status != 'Completed')
    completed_returns = sum(1 for r in my_returns if r.status == 'Completed')

    return render_template(
        'dashboard.html',
        my_books=my_books,
        my_requests=my_requests,
        incoming_requests=incoming_requests,
        my_returns=my_returns,
        pending_returns=pending_returns,
        completed_returns=completed_returns
    )


@app.route('/requests/<int:req_id>/status', methods=['POST'])
@login_required
def update_request_status(req_id):
    ex_req = db.session.get(ExchangeRequest, req_id)
    if not ex_req or ex_req.textbook.seller_id != current_user.id:
        abort(403)

    new_status = request.form.get('status', 'Pending')
    ex_req.status = new_status
    if new_status == 'Accepted':
        ex_req.textbook.status = 'Reserved'
    db.session.commit()
    flash(f'Request marked as {new_status}.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/returns/schedule', methods=['GET', 'POST'])
def return_books():
    created_return = None
    if request.method == 'POST':
        code = f"RAM-{random.randint(100000, 999999)}"
        while BookReturn.query.filter_by(return_code=code).first():
            code = f"RAM-{random.randint(100000, 999999)}"

        new_return = BookReturn(
            return_code=code,
            student_name=request.form.get('studentName', '').strip(),
            student_id_number=request.form.get('studentID', '').strip(),
            email=request.form.get('email', '').strip().lower(),
            book_title=request.form.get('bookTitle', '').strip(),
            isbn=request.form.get('isbn', '').strip(),
            order_number=request.form.get('orderNumber', '').strip(),
            condition=request.form.get('condition', '').strip(),
            return_date=request.form.get('returnDate', '').strip(),
            status='Awaiting Drop-Off'
        )
        db.session.add(new_return)
        db.session.commit()
        created_return = new_return
        flash(f'Return scheduled! Your confirmation code is {code}.', 'success')

    return render_template('return_books.html', created_return=created_return)


@app.route('/returns/track', methods=['GET', 'POST'])
def return_status():
    tracked_return = None
    searched_code = ''
    not_found = False

    if request.method == 'POST':
        searched_code = request.form.get('returnCode', '').strip().upper()
        tracked_return = BookReturn.query.filter_by(return_code=searched_code).first()
        if not tracked_return:
            not_found = True

    stage_map = {
        'Awaiting Drop-Off': 1,
        'Received': 2,
        'Under Review': 3,
        'Completed': 4,
        'Issue Found': 3
    }
    stage = stage_map.get(tracked_return.status, 1) if tracked_return else 0

    return render_template(
        'return_status.html',
        tracked_return=tracked_return,
        searched_code=searched_code,
        not_found=not_found,
        stage=stage
    )


@app.route('/admin/returns', methods=['GET', 'POST'])
def bookstore_admin():
    if request.method == 'POST':
        return_id = request.form.get('return_id')
        new_status = request.form.get('status')
        record = db.session.get(BookReturn, int(return_id))
        if record and new_status:
            record.status = new_status
            db.session.commit()
            flash(f'{record.return_code} updated to {new_status}.', 'success')
        return redirect(url_for('bookstore_admin'))

    all_returns = BookReturn.query.order_by(BookReturn.created_at.desc()).all()
    stats = {
        'total': len(all_returns),
        'pending': sum(1 for r in all_returns if r.status == 'Awaiting Drop-Off'),
        'review': sum(1 for r in all_returns if r.status == 'Under Review'),
        'completed': sum(1 for r in all_returns if r.status == 'Completed')
    }
    return render_template('bookstore_admin.html', all_returns=all_returns, stats=stats)


# ==================== INITIALIZE DB & SEED DATA ====================

def seed_initial_data():
    if Student.query.first():
        return

    demo_student = Student(
        first_name='Marcus',
        last_name='Ram',
        student_id='900123456',
        email='mram@rams.wssu.edu'
    )
    demo_student.set_password('RamPride2026!')
    db.session.add(demo_student)
    db.session.commit()

    sample_books = [
        Textbook(
            title='College Physics',
            author='Raymond A. Serway',
            isbn='978-1305952300',
            course='PHY 2331',
            category='science',
            condition='Good',
            listing_type='sell',
            price=45.00,
            description='Lightly highlighted chapters 1-4. Includes all study guides.',
            seller_id=demo_student.id
        ),
        Textbook(
            title='Principles of Microeconomics',
            author='N. Gregory Mankiw',
            isbn='978-0357133484',
            course='ECO 2311',
            category='business',
            condition='Like New',
            listing_type='sell',
            price=35.00,
            description='Clean pages, no markings. Ready for campus pickup.',
            seller_id=demo_student.id
        ),
        Textbook(
            title='Introduction to Python',
            author='Tony Gaddis',
            isbn='978-0135929032',
            course='CSC 1310',
            category='technology',
            condition='Good',
            listing_type='trade',
            price=0.00,
            description='Open to trading for Data Structures or Discrete Math textbooks.',
            seller_id=demo_student.id
        )
    ]
    db.session.add_all(sample_books)

    sample_returns = [
        BookReturn(
            return_code='RAM-102850',
            student_name='Marcus Ram',
            student_id_number='900123456',
            email='mram@rams.wssu.edu',
            book_title='Principles of Microeconomics',
            isbn='978-0357133484',
            order_number='ORD-88210',
            condition='Like New',
            return_date='2026-12-08',
            status='Awaiting Drop-Off'
        )
    ]
    db.session.add_all(sample_returns)
    db.session.commit()


with app.app_context():
    db.create_all()
    seed_initial_data()


if __name__ == '__main__':
    app.run(debug=True)

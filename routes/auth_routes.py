from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user

from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        login_val = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not login_val or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html', username=login_val)

        # Allow login via username or email
        user = User.query.filter(
            (User.username == login_val) | (User.email == login_val.lower())
        ).first()

        if user and user.check_password(password):
            if user.status == 'blocked':
                flash('Your account has been suspended by an administrator.', 'error')
                return render_template('login.html')

            login_user(user, remember=True)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))

        flash('Invalid username or password. Please try again.', 'error')
        return render_template('login.html', username=login_val)

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not full_name or not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html', full_name=full_name, username=username, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html', full_name=full_name, username=username, email=email)

        # Check existing username
        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'error')
            return render_template('register.html', full_name=full_name, email=email)

        # Check existing email
        if User.query.filter_by(email=email).first():
            flash('Email address is already registered. Please sign in.', 'error')
            return redirect(url_for('auth.login'))

        # Create user with secure cryptographic password hash
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role='user',
            status='active'
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()

            # Auto-login newly registered user and navigate to dashboard
            login_user(user, remember=True)
            flash(f'Account created successfully! Welcome to CodeVocalis AI, {user.full_name}.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during account creation. Please try again.', 'error')
            return render_template('register.html', full_name=full_name, username=username, email=email)

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))

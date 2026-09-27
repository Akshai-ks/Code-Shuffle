from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from models.user import UserModel

auth_bp = Blueprint('auth', __name__)

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = UserModel.get_user_by_id(user_id)
    if user and user.get('is_blocked'):
        session.clear()
        return None
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.get('role') != 'admin':
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.get('role') != 'admin':
            flash('Administrator access required.', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('user_id') and session.get('user_role') == 'admin':
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = UserModel.get_user_by_email(email)
        if not user or not UserModel.verify_password(user, password) or user['role'] != 'admin':
            flash('Invalid admin credentials.', 'danger')
            return render_template('admin/admin_login.html', email=email)

        session.permanent = True
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_role'] = 'admin'

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/admin_login.html')

@auth_bp.route('/logout')
@auth_bp.route('/admin/logout')
def logout():
    session.clear()
    flash('Logged out from admin workspace successfully.', 'info')
    return redirect(url_for('auth.admin_login'))

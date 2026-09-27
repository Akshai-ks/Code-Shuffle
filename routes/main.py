from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user import UserModel
from models.quote import QuoteModel
from models.category import CategoryModel

main_bp = Blueprint('main', __name__)

# PAGE 1: OPEN WELCOME INTRO SCREEN
@main_bp.route('/')
@main_bp.route('/welcome')
def welcome():
    return render_template('welcome.html')

# PAGE 2: MAIN DISCOVERY PLATFORM
@main_bp.route('/discover', methods=['GET', 'POST'])
def discover():
    categories = CategoryModel.get_all_categories()
    
    if request.method == 'POST':
        # Check if submitting quote
        text = request.form.get('text', '').strip()
        author = request.form.get('author', '').strip() or 'Unknown'
        category_id = request.form.get('category_id', type=int)

        if text and category_id:
            admin_user = UserModel.get_user_by_email('admin@stthomas.edu.in')
            sub_id = admin_user['id'] if admin_user else 1
            QuoteModel.submit_quote(text, author, category_id, sub_id)
            flash('Your quote has been submitted for review! It will be visible to everyone once approved by an admin. ✨', 'success')
            return redirect(url_for('main.discover'))

    return render_template('home.html', categories=categories)

@main_bp.route('/set-name', methods=['POST'])
def set_name():
    data = request.get_json() or {}
    name = data.get('name', '').strip() or request.form.get('name', '').strip()
    if name:
        session['user_name'] = name
        return jsonify({'success': True, 'name': name})
    return jsonify({'error': 'Name is required'}), 400

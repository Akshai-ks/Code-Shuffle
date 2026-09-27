from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import admin_required, get_current_user
from models.user import UserModel
from models.quote import QuoteModel
from models.category import CategoryModel
from models.report import ReportModel
from models.like import LikeModel
from database.db import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    user = get_current_user()
    conn = get_db()
    cursor = conn.cursor()
    
    # Stats
    cursor.execute("SELECT COUNT(*) as count FROM quotes")
    total_quotes = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM quotes WHERE status = 'approved'")
    approved_quotes = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM quotes WHERE status = 'pending'")
    pending_quotes = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM reports WHERE status = 'pending'")
    pending_reports = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM likes")
    total_likes = cursor.fetchone()['count']
    
    conn.close()

    recent_pending = QuoteModel.get_pending_quotes()[:5]
    recent_reports = ReportModel.get_all_reports(status='pending')[:5]

    return render_template(
        'admin/dashboard.html',
        user=user,
        total_quotes=total_quotes,
        approved_quotes=approved_quotes,
        pending_quotes=pending_quotes,
        pending_reports=pending_reports,
        total_likes=total_likes,
        recent_pending=recent_pending,
        recent_reports=recent_reports
    )

@admin_bp.route('/pending')
@admin_required
def pending_quotes():
    user = get_current_user()
    pending = QuoteModel.get_pending_quotes()
    return render_template('admin/pending.html', user=user, pending_quotes=pending)

@admin_bp.route('/quotes')
@admin_required
def all_quotes():
    user = get_current_user()
    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)

    quotes = QuoteModel.get_all_quotes_admin(status=status if status else None, search=search, category_id=category_id)
    categories = CategoryModel.get_all_categories()
    return render_template('admin/quotes.html', user=user, quotes=quotes, categories=categories, current_status=status, search=search, current_category=category_id)

@admin_bp.route('/users')
@admin_required
def users():
    user = get_current_user()
    search = request.args.get('search', '').strip()
    all_users = UserModel.get_all_users(search=search)
    return render_template('admin/users.html', user=user, users=all_users, search=search)

@admin_bp.route('/reports')
@admin_required
def reports():
    user = get_current_user()
    status = request.args.get('status', 'pending').strip()
    all_reports = ReportModel.get_all_reports(status=status if status != 'all' else None)
    return render_template('admin/reports.html', user=user, reports=all_reports, current_status=status)

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip()
        icon = request.form.get('icon', '').strip() or '✨'
        
        if not name or not slug:
            flash('Category name and slug are required.', 'danger')
        else:
            cat_id, err = CategoryModel.create_category(name, slug, icon)
            if err:
                flash(f'Error creating category: {err}', 'danger')
            else:
                flash(f'Category "{name}" created successfully!', 'success')
        return redirect(url_for('admin.categories'))

    categories_list = CategoryModel.get_all_categories()
    return render_template('admin/categories.html', user=user, categories=categories_list)

# Action API endpoints for Admin
@admin_bp.route('/quote/create', methods=['POST'])
@admin_required
def create_quote():
    data = request.form if request.form else (request.json or {})
    text = data.get('text', '').strip()
    author = data.get('author', '').strip() or 'Unknown'
    category_id = int(data.get('category_id') or 1)
    
    if not text or not category_id:
        if request.is_json:
            return jsonify({'error': 'Text and category required'}), 400
        flash('Text and category are required.', 'danger')
        return redirect(url_for('admin.all_quotes'))
        
    user = get_current_user()
    sub_id = user['id'] if user else 1
    new_id = QuoteModel.submit_quote(text, author, category_id, sub_id)
    QuoteModel.update_status(new_id, 'approved')
    
    if request.is_json:
        return jsonify({'success': True, 'quote_id': new_id})
    flash('New quote created and published successfully! ✨', 'success')
    return redirect(url_for('admin.all_quotes'))

@admin_bp.route('/quote/<int:quote_id>/status', methods=['POST'])
@admin_required
def update_quote_status(quote_id):
    status = request.form.get('status') or (request.json or {}).get('status')
    if status not in ['approved', 'rejected', 'pending']:
        return jsonify({'error': 'Invalid status'}), 400
    
    QuoteModel.update_status(quote_id, status)
    return jsonify({'success': True, 'status': status})

@admin_bp.route('/quote/<int:quote_id>/edit', methods=['POST'])
@admin_required
def edit_quote(quote_id):
    data = request.form if request.form else (request.json or {})
    text = data.get('text', '').strip()
    author = data.get('author', '').strip() or 'Unknown'
    category_id = int(data.get('category_id') or 1)
    
    if not text or not category_id:
        if request.is_json:
            return jsonify({'error': 'Text and category required'}), 400
        flash('Text and category required', 'danger')
        return redirect(url_for('admin.all_quotes'))
        
    QuoteModel.update_quote(quote_id, text, author, category_id)
    if request.is_json:
        return jsonify({'success': True})
    flash('Quote updated successfully.', 'success')
    return redirect(url_for('admin.all_quotes'))

@admin_bp.route('/quote/<int:quote_id>/delete', methods=['POST'])
@admin_required
def delete_quote(quote_id):
    # Auto-resolve any associated reports in DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE reports SET status = 'resolved' WHERE quote_id = ? AND status = 'pending'", (quote_id,))
    conn.commit()
    conn.close()

    QuoteModel.delete_quote(quote_id)
    return jsonify({'success': True})

@admin_bp.route('/quote/<int:quote_id>/featured', methods=['POST'])
@admin_required
def toggle_featured(quote_id):
    success, val = QuoteModel.toggle_featured(quote_id)
    return jsonify({'success': success, 'is_featured': val})

@admin_bp.route('/quote/<int:quote_id>/moment', methods=['POST'])
@admin_required
def toggle_moment(quote_id):
    success, val = QuoteModel.toggle_moment(quote_id)
    return jsonify({'success': success, 'is_quote_of_the_moment': val})

@admin_bp.route('/user/<int:user_id>/block', methods=['POST'])
@admin_required
def toggle_block_user(user_id):
    success, val = UserModel.toggle_block(user_id)
    return jsonify({'success': success, 'is_blocked': val})

@admin_bp.route('/report/<int:report_id>/status', methods=['POST'])
@admin_required
def update_report_status(report_id):
    status = request.form.get('status') or (request.json or {}).get('status')
    if status not in ['resolved', 'dismissed']:
        return jsonify({'error': 'Invalid status'}), 400
    ReportModel.update_report_status(report_id, status)
    return jsonify({'success': True, 'status': status})

@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    CategoryModel.delete_category(category_id)
    flash('Category deleted.', 'info')
    return redirect(url_for('admin.categories'))

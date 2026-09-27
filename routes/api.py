from flask import Blueprint, jsonify, request, session
from models.quote import QuoteModel
from models.like import LikeModel
from models.saved import SavedQuoteModel
from models.report import ReportModel

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/shuffle')
def shuffle_quote():
    user_id = session.get('user_id') or 2

    quote = QuoteModel.get_random_quote(user_id=user_id, category_id=None)
    
    if not quote:
        return jsonify({'error': 'No quotes available yet.'}), 404
    
    clean_quote = {
        'id': quote['id'],
        'text': quote['text'],
        'author': quote['author'] if quote['author'] else 'Unknown',
        'category_name': quote['category_name'],
        'category_icon': quote['category_icon'],
        'likes_count': quote['likes_count'],
        'is_liked': bool(quote.get('is_liked')),
        'is_saved': bool(quote.get('is_saved'))
    }

    return jsonify({
        'success': True,
        'quote': clean_quote
    })

@api_bp.route('/like/<int:quote_id>', methods=['POST'])
def toggle_like(quote_id):
    user_id = session.get('user_id') or 2
    is_liked, likes_count = LikeModel.toggle_like(user_id, quote_id)
    return jsonify({
        'success': True,
        'is_liked': is_liked,
        'likes_count': likes_count
    })

@api_bp.route('/save/<int:quote_id>', methods=['POST'])
def toggle_save(quote_id):
    user_id = session.get('user_id') or 2
    is_saved = SavedQuoteModel.toggle_save(user_id, quote_id)
    return jsonify({
        'success': True,
        'is_saved': is_saved
    })

@api_bp.route('/report/<int:quote_id>', methods=['POST'])
def report_quote(quote_id):
    data = request.get_json() or {}
    reason = data.get('reason', '').strip() or request.form.get('reason', '').strip()
    details = data.get('details', '').strip() or request.form.get('details', '').strip()
    
    if not reason:
        return jsonify({'error': 'Reason is required'}), 400
        
    user_id = session.get('user_id', 1)
    report_id = ReportModel.create_report(user_id, quote_id, reason, details)
    return jsonify({
        'success': True,
        'message': 'Report submitted for review. Thank you.',
        'report_id': report_id
    })

@api_bp.route('/quote/<int:quote_id>')
def get_quote(quote_id):
    quote = QuoteModel.get_quote_by_id(quote_id)
    if not quote:
        return jsonify({'error': 'Quote not found'}), 404
    clean_quote = {
        'id': quote['id'],
        'text': quote['text'],
        'author': quote['author'],
        'category_name': quote['category_name'],
        'category_icon': quote['category_icon'],
        'likes_count': quote['likes_count']
    }
    return jsonify({'success': True, 'quote': clean_quote})

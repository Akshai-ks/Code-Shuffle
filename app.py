import os
from flask import Flask, render_template, redirect, url_for
from database.db import init_db
from routes.auth import auth_bp
from routes.main import main_bp
from routes.api import api_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'rotaract_st_thomas_college_thrissur_key_2026')

# Initialize DB on start
init_db()

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content='<div class="text-center" style="padding: 4rem 1rem;"><h2>404 — Page Not Found</h2><p style="color: var(--text-secondary); margin-bottom: 1.5rem;">The page you are looking for does not exist.</p><a href="/" class="btn-pink">Return Home</a></div>'), 404

if __name__ == '__main__':
    print("Starting Rotaract Club Quote Discovery & Sharing Platform...")
    print("Official Logo loaded from static/images/rotaract-logo.png")
    app.run(host='127.0.0.1', port=5000, debug=True)

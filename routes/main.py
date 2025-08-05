from flask import Blueprint, redirect, url_for, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to shipments if logged in, otherwise to login"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('shipments.list_shipments'))

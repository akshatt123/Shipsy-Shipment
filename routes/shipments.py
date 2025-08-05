from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models.shipment import Shipment
from utils.decorators import login_required
from utils.validators import validate_shipment_data

shipments_bp = Blueprint('shipments', __name__)

@shipments_bp.route('/')
@login_required
def list_shipments():
    """List shipments with filtering and pagination"""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    express_filter = request.args.get('express', '')
    
    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    # Get shipments with filters
    shipments, total_pages, total_count = Shipment.find_by_user(
        user_id=session['user_id'],
        status_filter=status_filter,
        priority_filter=priority_filter,
        express_filter=express_filter,
        page=page,
        per_page=per_page
    )
    
    return render_template('shipments.html', 
                         shipments=shipments, 
                         current_page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         express_filter=express_filter,
                         status_choices=Shipment.get_status_choices(),
                         priority_choices=Shipment.get_priority_choices())

@shipments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_shipment():
    """Create a new shipment"""
    if request.method == 'POST':
        # Validate form data
        validation_errors = validate_shipment_data(request.form)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('create_shipment.html',
                                 status_choices=Shipment.get_status_choices(),
                                 priority_choices=Shipment.get_priority_choices())
        
        # Create new shipment
        shipment = Shipment(
            sender_name=request.form['sender_name'].strip(),
            sender_address=request.form['sender_address'].strip(),
            recipient_name=request.form['recipient_name'].strip(),
            recipient_address=request.form['recipient_address'].strip(),
            package_description=request.form['package_description'].strip(),
            weight=float(request.form['weight']) if request.form['weight'] else 0.0,
            status=request.form['status'],
            priority=request.form['priority'],
            is_express='is_express' in request.form,
            user_id=session['user_id']
        )
        
        try:
            shipment.save()
            flash(f'Shipment created successfully! Tracking Number: {shipment.tracking_number}', 'success')
            return redirect(url_for('shipments.list_shipments'))
        except Exception as e:
            flash('Failed to create shipment. Please try again.', 'error')
    
    return render_template('create_shipment.html',
                         status_choices=Shipment.get_status_choices(),
                         priority_choices=Shipment.get_priority_choices())

@shipments_bp.route('/<int:shipment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_shipment(shipment_id):
    """Edit an existing shipment"""
    shipment = Shipment.find_by_id(shipment_id, session['user_id'])
    
    if not shipment:
        flash('Shipment not found!', 'error')
        return redirect(url_for('shipments.list_shipments'))
    
    if request.method == 'POST':
        # Validate form data
        validation_errors = validate_shipment_data(request.form)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('edit_shipment.html', 
                                 shipment=shipment,
                                 status_choices=Shipment.get_status_choices(),
                                 priority_choices=Shipment.get_priority_choices())
        
        # Update shipment
        shipment.sender_name = request.form['sender_name'].strip()
        shipment.sender_address = request.form['sender_address'].strip()
        shipment.recipient_name = request.form['recipient_name'].strip()
        shipment.recipient_address = request.form['recipient_address'].strip()
        shipment.package_description = request.form['package_description'].strip()
        shipment.weight = float(request.form['weight']) if request.form['weight'] else 0.0
        shipment.status = request.form['status']
        shipment.priority = request.form['priority']
        shipment.is_express = 'is_express' in request.form
        
        try:
            shipment.save()
            flash('Shipment updated successfully!', 'success')
            return redirect(url_for('shipments.list_shipments'))
        except Exception as e:
            flash('Failed to update shipment. Please try again.', 'error')
    
    return render_template('edit_shipment.html', 
                         shipment=shipment,
                         status_choices=Shipment.get_status_choices(),
                         priority_choices=Shipment.get_priority_choices())

@shipments_bp.route('/<int:shipment_id>/delete', methods=['POST'])
@login_required
def delete_shipment(shipment_id):
    """Delete a shipment"""
    shipment = Shipment.find_by_id(shipment_id, session['user_id'])
    
    if not shipment:
        flash('Shipment not found!', 'error')
        return redirect(url_for('shipments.list_shipments'))
    
    try:
        shipment.delete()
        flash('Shipment deleted successfully!', 'success')
    except Exception as e:
        flash('Failed to delete shipment. Please try again.', 'error')
    
    return redirect(url_for('shipments.list_shipments'))

@shipments_bp.route('/<int:shipment_id>/toggle-express', methods=['POST'])
@login_required
def toggle_express(shipment_id):
    """Toggle express status of a shipment"""
    shipment = Shipment.find_by_id(shipment_id, session['user_id'])
    
    if not shipment:
        flash('Shipment not found!', 'error')
        return redirect(url_for('shipments.list_shipments'))
    
    try:
        shipment.is_express = not shipment.is_express
        shipment.save()
        status = 'marked as express' if shipment.is_express else 'unmarked as express'
        flash(f'Shipment {status} successfully!', 'success')
    except Exception as e:
        flash('Failed to update shipment. Please try again.', 'error')
    
    return redirect(url_for('shipments.list_shipments'))

@shipments_bp.route('/track', methods=['GET', 'POST'])
@login_required
def track_shipment():
    """Track a shipment by tracking number"""
    shipment = None
    
    if request.method == 'POST':
        tracking_number = request.form['tracking_number'].strip().upper()
        
        if tracking_number:
            shipment = Shipment.find_by_tracking_number(tracking_number, session['user_id'])
            if not shipment:
                flash('Shipment not found with this tracking number!', 'error')
        else:
            flash('Please enter a tracking number!', 'error')
    
    return render_template('track_shipment.html', shipment=shipment)

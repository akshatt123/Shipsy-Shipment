from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from models.shipment import Shipment
from utils.decorators import login_required
from utils.validators import validate_shipment_data

shipments_bp = Blueprint('shipments', __name__)

@shipments_bp.route('/')
@login_required
def list_shipments():
    """List shipments with filtering and pagination"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')
        express_filter = request.args.get('express', '')
        search_term = request.args.get('search', '').strip()
        
        # Pagination parameters
        page = int(request.args.get('page', 1))
        per_page = current_app.config['ITEMS_PER_PAGE']
        
        # Debug information
        print(f"DEBUG: User ID in session: {session.get('user_id')}")
        print(f"DEBUG: Username in session: {session.get('username')}")
        
        # Search or filter shipments
        if search_term:
            shipments, total_pages, total_count = Shipment.search_shipments(
                user_id=session['user_id'],
                search_term=search_term,
                page=page,
                per_page=per_page
            )
        else:
            shipments, total_pages, total_count = Shipment.find_by_user(
                user_id=session['user_id'],
                status_filter=status_filter,
                priority_filter=priority_filter,
                express_filter=express_filter,
                page=page,
                per_page=per_page
            )
        
        print(f"DEBUG: Found {len(shipments)} shipments for user {session['user_id']}")
        print(f"DEBUG: Total count: {total_count}, Total pages: {total_pages}")
        
        return render_template('shipments.html', 
                             shipments=shipments, 
                             current_page=page,
                             total_pages=total_pages,
                             total_count=total_count,
                             status_filter=status_filter,
                             priority_filter=priority_filter,
                             express_filter=express_filter,
                             search_term=search_term,
                             status_choices=Shipment.get_status_choices(),
                             priority_choices=Shipment.get_priority_choices())
    except Exception as e:
        flash('Error loading shipments. Please try again.', 'error')
        print(f"List shipments error: {e}")
        return render_template('shipments.html', shipments=[], current_page=1, 
                             total_pages=1, total_count=0, status_choices=[], priority_choices=[])

@shipments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_shipment():
    """Create a new shipment"""
    if request.method == 'POST':
        try:
            # Validate form data
            validation_errors = validate_shipment_data(request.form)
            if validation_errors:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('create_shipment.html',
                                     status_choices=Shipment.get_status_choices(),
                                     priority_choices=Shipment.get_priority_choices())
            
            # Debug information
            print(f"DEBUG: Creating shipment for user_id: {session['user_id']}")
            print(f"DEBUG: Session data: {dict(session)}")
            
            # Create new shipment
            shipment = Shipment(
                sender_name=request.form['sender_name'].strip(),
                sender_address=request.form['sender_address'].strip(),
                recipient_name=request.form['recipient_name'].strip(),
                recipient_address=request.form['recipient_address'].strip(),
                package_description=request.form.get('package_description', '').strip(),
                weight=float(request.form['weight']) if request.form.get('weight') else 0.0,
                status=request.form['status'],
                priority=request.form['priority'],
                is_express='is_express' in request.form,
                user_id=session['user_id']
            )
            
            shipment.save()
            print(f"DEBUG: Shipment saved with ID: {shipment.id}, user_id: {shipment.user_id}")
            flash(f'Shipment created successfully! Tracking Number: {shipment.tracking_number}', 'success')
            return redirect(url_for('shipments.list_shipments'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('Failed to create shipment. Please try again.', 'error')
            print(f"Create shipment error: {e}")
    
    return render_template('create_shipment.html',
                         status_choices=Shipment.get_status_choices(),
                         priority_choices=Shipment.get_priority_choices())

@shipments_bp.route('/<int:shipment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_shipment(shipment_id):
    """Edit an existing shipment"""
    try:
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
            shipment.package_description = request.form.get('package_description', '').strip()
            shipment.weight = float(request.form['weight']) if request.form.get('weight') else 0.0
            shipment.status = request.form['status']
            shipment.priority = request.form['priority']
            shipment.is_express = 'is_express' in request.form
            
            shipment.save()
            flash('Shipment updated successfully!', 'success')
            return redirect(url_for('shipments.list_shipments'))
        
        return render_template('edit_shipment.html', 
                             shipment=shipment,
                             status_choices=Shipment.get_status_choices(),
                             priority_choices=Shipment.get_priority_choices())
    except Exception as e:
        flash('Error processing shipment. Please try again.', 'error')
        print(f"Edit shipment error: {e}")
        return redirect(url_for('shipments.list_shipments'))

@shipments_bp.route('/<int:shipment_id>/delete', methods=['POST'])
@login_required
def delete_shipment(shipment_id):
    """Delete a shipment"""
    try:
        shipment = Shipment.find_by_id(shipment_id, session['user_id'])
        
        if not shipment:
            flash('Shipment not found!', 'error')
            return redirect(url_for('shipments.list_shipments'))
        
        shipment.delete()
        flash('Shipment deleted successfully!', 'success')
    except Exception as e:
        flash('Failed to delete shipment. Please try again.', 'error')
        print(f"Delete shipment error: {e}")
    
    return redirect(url_for('shipments.list_shipments'))

@shipments_bp.route('/<int:shipment_id>/toggle-express', methods=['POST'])
@login_required
def toggle_express(shipment_id):
    """Toggle express status of a shipment"""
    try:
        shipment = Shipment.find_by_id(shipment_id, session['user_id'])
        
        if not shipment:
            flash('Shipment not found!', 'error')
            return redirect(url_for('shipments.list_shipments'))
        
        shipment.is_express = not shipment.is_express
        shipment.save()
        status = 'marked as express' if shipment.is_express else 'unmarked as express'
        flash(f'Shipment {status} successfully!', 'success')
    except Exception as e:
        flash('Failed to update shipment. Please try again.', 'error')
        print(f"Toggle express error: {e}")
    
    return redirect(url_for('shipments.list_shipments'))

@shipments_bp.route('/track', methods=['GET', 'POST'])
@login_required
def track_shipment():
    """Track a shipment by tracking number"""
    shipment = None
    
    if request.method == 'POST':
        tracking_number = request.form.get('tracking_number', '').strip().upper()
        
        if tracking_number:
            try:
                shipment = Shipment.find_by_tracking_number(tracking_number, session['user_id'])
                if not shipment:
                    flash('Shipment not found with this tracking number!', 'error')
            except Exception as e:
                flash('Error tracking shipment. Please try again.', 'error')
                print(f"Track shipment error: {e}")
        else:
            flash('Please enter a tracking number!', 'error')
    
    return render_template('track_shipment.html', shipment=shipment)

@shipments_bp.route('/stats')
@login_required
def shipment_stats():
    """Display shipment statistics"""
    try:
        stats = Shipment.get_status_stats(session['user_id'])
        return render_template('shipment_stats.html', stats=stats)
    except Exception as e:
        flash('Error loading statistics. Please try again.', 'error')
        print(f"Shipment stats error: {e}")
        return redirect(url_for('shipments.list_shipments'))

@shipments_bp.route('/api/cost-calculator', methods=['POST'])
@login_required
def calculate_cost():
    """API endpoint to calculate shipping cost"""
    try:
        data = request.get_json()
        weight = data.get('weight', 0)
        priority = data.get('priority', 'standard')
        is_express = data.get('is_express', False)
        
        cost = Shipment.calculate_shipping_cost(weight, priority, is_express)
        return jsonify({'cost': cost})
    except Exception as e:
        print(f"Cost calculation error: {e}")
        return jsonify({'error': 'Failed to calculate cost'}), 500

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models.task import Task
from utils.decorators import login_required
from utils.validators import validate_task_data

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
@login_required
def list_tasks():
    """List tasks with filtering and pagination"""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    urgent_filter = request.args.get('urgent', '')
    
    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    # Get tasks with filters
    tasks, total_pages, total_count = Task.find_by_user(
        user_id=session['user_id'],
        status_filter=status_filter,
        priority_filter=priority_filter,
        urgent_filter=urgent_filter,
        page=page,
        per_page=per_page
    )
    
    return render_template('tasks.html', 
                         tasks=tasks, 
                         current_page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         urgent_filter=urgent_filter,
                         status_choices=Task.get_status_choices(),
                         priority_choices=Task.get_priority_choices())

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Create a new task"""
    if request.method == 'POST':
        # Validate form data
        validation_errors = validate_task_data(request.form)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('create_task.html',
                                 status_choices=Task.get_status_choices(),
                                 priority_choices=Task.get_priority_choices())
        
        # Create new task
        task = Task(
            title=request.form['title'].strip(),
            description=request.form['description'].strip(),
            status=request.form['status'],
            priority=request.form['priority'],
            is_urgent='is_urgent' in request.form,
            user_id=session['user_id']
        )
        
        try:
            task.save()
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks.list_tasks'))
        except Exception as e:
            flash('Failed to create task. Please try again.', 'error')
    
    return render_template('create_task.html',
                         status_choices=Task.get_status_choices(),
                         priority_choices=Task.get_priority_choices())

@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task"""
    task = Task.find_by_id(task_id, session['user_id'])
    
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    if request.method == 'POST':
        # Validate form data
        validation_errors = validate_task_data(request.form)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('edit_task.html', 
                                 task=task,
                                 status_choices=Task.get_status_choices(),
                                 priority_choices=Task.get_priority_choices())
        
        # Update task
        task.title = request.form['title'].strip()
        task.description = request.form['description'].strip()
        task.status = request.form['status']
        task.priority = request.form['priority']
        task.is_urgent = 'is_urgent' in request.form
        
        try:
            task.save()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('tasks.list_tasks'))
        except Exception as e:
            flash('Failed to update task. Please try again.', 'error')
    
    return render_template('edit_task.html', 
                         task=task,
                         status_choices=Task.get_status_choices(),
                         priority_choices=Task.get_priority_choices())

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    task = Task.find_by_id(task_id, session['user_id'])
    
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    try:
        task.delete()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        flash('Failed to delete task. Please try again.', 'error')
    
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/<int:task_id>/toggle-urgent', methods=['POST'])
@login_required
def toggle_urgent(task_id):
    """Toggle urgent status of a task"""
    task = Task.find_by_id(task_id, session['user_id'])
    
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('tasks.list_tasks'))
    
    try:
        task.is_urgent = not task.is_urgent
        task.save()
        status = 'marked as urgent' if task.is_urgent else 'unmarked as urgent'
        flash(f'Task {status} successfully!', 'success')
    except Exception as e:
        flash('Failed to update task. Please try again.', 'error')
    
    return redirect(url_for('tasks.list_tasks'))

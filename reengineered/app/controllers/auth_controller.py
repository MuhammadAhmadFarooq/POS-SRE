"""
Authentication Controller - Handles login/logout routes.
Replaces legacy Login_Interface.java functionality.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app.services.auth_service import AuthService, AuthenticationError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Redirect to appropriate page based on login status."""
    if current_user.is_authenticated:
        return redirect(AuthService.get_redirect_for_role(current_user))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(AuthService.get_redirect_for_role(current_user))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        try:
            # Authenticate user
            employee = AuthService.authenticate(username, password)
            
            # Log in user
            AuthService.login(employee, remember=remember)
            
            flash(f'Welcome back, {employee.full_name}!', 'success')
            
            # Redirect to appropriate dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(AuthService.get_redirect_for_role(employee))
            
        except AuthenticationError as e:
            flash(str(e), 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    name = current_user.full_name
    AuthService.logout()
    flash(f'Goodbye, {name}! You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        try:
            AuthService.change_password(current_user, current_password, new_password)
            flash('Password changed successfully!', 'success')
            return redirect(AuthService.get_redirect_for_role(current_user))
            
        except AuthenticationError as e:
            flash(str(e), 'danger')
    
    return render_template('auth/change_password.html')


@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile."""
    return render_template('auth/profile.html', employee=current_user)

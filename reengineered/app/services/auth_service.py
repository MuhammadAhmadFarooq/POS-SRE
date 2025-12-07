"""
Authentication Service - Handles user authentication and session management.
Replaces legacy POSSystem.java login/logout functionality with secure implementation.
"""
import logging
from datetime import datetime
from flask_login import login_user, logout_user
from app import db
from app.models.employee import Employee, EmployeeRole

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthService:
    """
    Authentication service with secure password handling.
    
    Improvements over legacy system:
    - PBKDF2 password hashing instead of plain text comparison
    - Login attempt tracking
    - Session management via Flask-Login
    - Role-based access control
    """
    
    @staticmethod
    def authenticate(username, password):
        """
        Authenticate user with username and password.
        
        Args:
            username: Employee username
            password: Plain text password
            
        Returns:
            Employee: Authenticated employee object
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if not username or not password:
            logger.warning(f'Authentication failed: Missing credentials')
            raise AuthenticationError('Username and password are required')
        
        # Find employee by username
        employee = Employee.query.filter_by(username=username).first()
        
        if employee is None:
            logger.warning(f'Authentication failed: User not found - {username}')
            raise AuthenticationError('Invalid username or password')
        
        # Check if account is active
        if not employee.is_active:
            logger.warning(f'Authentication failed: Inactive account - {username}')
            raise AuthenticationError('Account is inactive. Please contact administrator.')
        
        # Verify password
        if not employee.check_password(password):
            logger.warning(f'Authentication failed: Invalid password - {username}')
            raise AuthenticationError('Invalid username or password')
        
        # Update last login
        employee.update_last_login()
        
        # Log successful authentication
        logger.info(f'User authenticated successfully: {username}')
        
        return employee
    
    @staticmethod
    def login(employee, remember=False):
        """
        Log in the employee using Flask-Login.
        
        Args:
            employee: Employee model instance
            remember: Whether to remember the session
            
        Returns:
            bool: True if login successful
        """
        result = login_user(employee, remember=remember)
        if result:
            logger.info(f'User logged in: {employee.username}')
        return result
    
    @staticmethod
    def logout():
        """
        Log out the current user.
        
        Returns:
            bool: True if logout successful
        """
        logout_user()
        logger.info('User logged out')
        return True
    
    @staticmethod
    def register_employee(employee_id, username, password, first_name, last_name, 
                         role=EmployeeRole.CASHIER):
        """
        Register a new employee.
        
        Args:
            employee_id: Unique employee ID
            username: Username for login
            password: Plain text password (will be hashed)
            first_name: First name
            last_name: Last name
            role: Employee role (default: Cashier)
            
        Returns:
            Employee: Created employee object
            
        Raises:
            AuthenticationError: If registration fails
        """
        # Check if username already exists
        existing = Employee.query.filter_by(username=username).first()
        if existing:
            raise AuthenticationError(f'Username {username} already exists')
        
        # Check if employee_id already exists
        existing = Employee.query.filter_by(employee_id=employee_id).first()
        if existing:
            raise AuthenticationError(f'Employee ID {employee_id} already exists')
        
        # Create new employee
        employee = Employee(
            employee_id=employee_id,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        db.session.add(employee)
        db.session.commit()
        
        logger.info(f'New employee registered: {username} ({employee_id})')
        
        return employee
    
    @staticmethod
    def change_password(employee, old_password, new_password):
        """
        Change employee password.
        
        Args:
            employee: Employee model instance
            old_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed
            
        Raises:
            AuthenticationError: If password change fails
        """
        # Verify old password
        if not employee.check_password(old_password):
            raise AuthenticationError('Current password is incorrect')
        
        # Validate new password
        if len(new_password) < 4:
            raise AuthenticationError('Password must be at least 4 characters')
        
        # Set new password
        employee.set_password(new_password)
        db.session.commit()
        
        logger.info(f'Password changed for user: {employee.username}')
        
        return True
    
    @staticmethod
    def reset_password(employee, new_password):
        """
        Reset employee password (admin action).
        
        Args:
            employee: Employee model instance
            new_password: New password
            
        Returns:
            bool: True if password reset
        """
        employee.set_password(new_password)
        db.session.commit()
        
        logger.info(f'Password reset for user: {employee.username}')
        
        return True
    
    @staticmethod
    def deactivate_account(employee):
        """
        Deactivate an employee account.
        
        Args:
            employee: Employee model instance
            
        Returns:
            bool: True if deactivated
        """
        employee.is_active = False
        db.session.commit()
        
        logger.info(f'Account deactivated: {employee.username}')
        
        return True
    
    @staticmethod
    def activate_account(employee):
        """
        Activate an employee account.
        
        Args:
            employee: Employee model instance
            
        Returns:
            bool: True if activated
        """
        employee.is_active = True
        db.session.commit()
        
        logger.info(f'Account activated: {employee.username}')
        
        return True
    
    @staticmethod
    def get_redirect_for_role(employee):
        """
        Get redirect URL based on employee role.
        
        Args:
            employee: Employee model instance
            
        Returns:
            str: URL to redirect to
        """
        if employee.has_admin_access():
            return '/admin/dashboard'
        return '/cashier/dashboard'

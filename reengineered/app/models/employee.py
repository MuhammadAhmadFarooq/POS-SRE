"""
Employee Model - Represents employees/users of the POS system.
Replaces legacy Employee.java and employee database management.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class EmployeeRole:
    """Employee role constants."""
    CASHIER = 'Cashier'
    ADMIN = 'Admin'
    MANAGER = 'Manager'
    
    @classmethod
    def all_roles(cls):
        return [cls.CASHIER, cls.ADMIN, cls.MANAGER]


class Employee(UserMixin, db.Model):
    """
    Employee model with secure password handling.
    
    Improvements over legacy system:
    - PBKDF2 password hashing instead of plain text
    - Role-based access control
    - Login tracking
    - Soft delete support
    """
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(10), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=EmployeeRole.CASHIER)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='employee', lazy='dynamic')
    
    def __init__(self, employee_id, username, password, first_name, last_name, role=EmployeeRole.CASHIER):
        self.employee_id = employee_id
        self.username = username
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
    
    def set_password(self, password):
        """
        Hash password using PBKDF2 with SHA-256.
        
        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )
    
    def check_password(self, password):
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches
        """
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @property
    def full_name(self):
        """Get employee's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        """Check if employee has admin role."""
        return self.role == EmployeeRole.ADMIN
    
    def is_manager(self):
        """Check if employee has manager role."""
        return self.role == EmployeeRole.MANAGER
    
    def is_cashier(self):
        """Check if employee has cashier role."""
        return self.role == EmployeeRole.CASHIER
    
    def has_admin_access(self):
        """Check if employee has admin or manager access."""
        return self.role in [EmployeeRole.ADMIN, EmployeeRole.MANAGER]
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.full_name}>'

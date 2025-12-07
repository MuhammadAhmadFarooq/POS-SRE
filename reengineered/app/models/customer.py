"""
Customer Model - Represents customers in the POS system.
Replaces legacy user database management.
"""
from datetime import datetime
from app import db


class Customer(db.Model):
    """
    Customer model for tracking customer information and rentals.
    
    Improvements over legacy system:
    - Proper customer records instead of just phone numbers
    - Relationship tracking with transactions and rentals
    - Customer history and loyalty features
    """
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='customer', lazy='dynamic')
    rentals = db.relationship('Rental', backref='customer', lazy='dynamic')
    
    def __init__(self, phone, name=None, email=None, address=None):
        self.phone = phone
        self.name = name
        self.email = email
        self.address = address
    
    def get_active_rentals(self):
        """Get all unreturned rentals for this customer."""
        return self.rentals.filter_by(returned=False).all()
    
    def get_overdue_rentals(self):
        """Get all overdue rentals for this customer."""
        from datetime import datetime
        return self.rentals.filter(
            db.and_(
                Rental.returned == False,
                Rental.due_date < datetime.utcnow()
            )
        ).all()
    
    def get_rental_history(self):
        """Get all rentals for this customer."""
        return self.rentals.order_by(Rental.rental_date.desc()).all()
    
    def get_transaction_history(self, limit=50):
        """Get recent transactions for this customer."""
        return self.transactions.order_by(
            Transaction.created_at.desc()
        ).limit(limit).all()
    
    def get_total_spent(self):
        """Calculate total amount spent by customer."""
        result = db.session.query(
            db.func.sum(Transaction.total)
        ).filter(
            Transaction.customer_id == self.id
        ).scalar()
        return result or 0.0
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'email': self.email,
            'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_spent': self.get_total_spent()
        }
    
    def __repr__(self):
        return f'<Customer {self.phone}: {self.name or "Unknown"}>'


# Import for type hints
from app.models.rental import Rental
from app.models.transaction import Transaction

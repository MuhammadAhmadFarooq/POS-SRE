"""
Rental Model - Represents item rentals in the POS system.
Replaces legacy rental database management.
"""
from datetime import datetime, timedelta
from app import db


class Rental(db.Model):
    """
    Rental model for tracking item rentals and returns.
    
    Improvements over legacy system:
    - Proper date tracking
    - Late fee calculation
    - Return status tracking
    - Customer association
    """
    __tablename__ = 'rentals'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)
    
    # Rental details
    quantity = db.Column(db.Integer, nullable=False, default=1)
    rental_price = db.Column(db.Float, nullable=False)
    rental_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    
    # Return details
    returned = db.Column(db.Boolean, default=False)
    return_date = db.Column(db.DateTime, nullable=True)
    late_fee = db.Column(db.Float, default=0.0)
    
    # Metadata
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, customer_id, item_id, rental_price, quantity=1, 
                 rental_days=7, transaction_id=None):
        self.customer_id = customer_id
        self.item_id = item_id
        self.rental_price = rental_price
        self.quantity = quantity
        self.transaction_id = transaction_id
        self.due_date = datetime.utcnow() + timedelta(days=rental_days)
    
    def is_overdue(self):
        """Check if rental is overdue."""
        if self.returned:
            return False
        return datetime.utcnow() > self.due_date
    
    def days_overdue(self):
        """Calculate number of days overdue."""
        if not self.is_overdue():
            return 0
        delta = datetime.utcnow() - self.due_date
        return max(0, delta.days)
    
    def calculate_late_fee(self, fee_per_day=2.00):
        """
        Calculate late fee based on days overdue.
        
        Args:
            fee_per_day: Fee charged per day overdue
            
        Returns:
            float: Total late fee
        """
        days = self.days_overdue()
        return days * fee_per_day * self.quantity
    
    def process_return(self, fee_per_day=2.00):
        """
        Process rental return.
        
        Args:
            fee_per_day: Late fee per day
            
        Returns:
            float: Late fee if any
        """
        self.returned = True
        self.return_date = datetime.utcnow()
        self.late_fee = self.calculate_late_fee(fee_per_day)
        
        # Restore item quantity
        if self.item:
            self.item.add_stock(self.quantity)
        
        return self.late_fee
    
    def days_remaining(self):
        """Calculate days remaining until due date."""
        if self.returned:
            return 0
        delta = self.due_date - datetime.utcnow()
        return max(0, delta.days)
    
    def extend_rental(self, additional_days):
        """
        Extend rental due date.
        
        Args:
            additional_days: Number of days to extend
        """
        if not self.returned:
            self.due_date = self.due_date + timedelta(days=additional_days)
    
    @property
    def total_price(self):
        """Calculate total rental price including any late fees."""
        return (self.rental_price * self.quantity) + self.late_fee
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity': self.quantity,
            'rental_price': self.rental_price,
            'rental_date': self.rental_date.isoformat() if self.rental_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'returned': self.returned,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'late_fee': self.late_fee,
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue(),
            'total_price': self.total_price
        }
    
    def __repr__(self):
        status = 'Returned' if self.returned else ('Overdue' if self.is_overdue() else 'Active')
        return f'<Rental {self.id}: Item {self.item_id} - {status}>'

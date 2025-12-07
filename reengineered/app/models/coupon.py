"""
Coupon Model - Represents discount coupons in the POS system.
Replaces legacy couponNumber.txt management.
"""
from datetime import datetime
from app import db


class Coupon(db.Model):
    """
    Coupon model for managing discount coupons.
    
    Improvements over legacy system:
    - Proper expiration tracking
    - Usage limits
    - Percentage and fixed amount discounts
    - Active/inactive status
    """
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200), nullable=True)
    
    # Discount details
    discount_percent = db.Column(db.Float, default=0.0)  # Percentage discount
    discount_amount = db.Column(db.Float, default=0.0)   # Fixed amount discount
    minimum_purchase = db.Column(db.Float, default=0.0)  # Minimum purchase amount
    
    # Usage tracking
    max_uses = db.Column(db.Integer, nullable=True)  # None = unlimited
    times_used = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='coupon', lazy='dynamic')
    
    def __init__(self, code, discount_percent=0.0, discount_amount=0.0, 
                 description=None, max_uses=None, expires_at=None, minimum_purchase=0.0):
        self.code = code.upper()
        self.discount_percent = discount_percent
        self.discount_amount = discount_amount
        self.description = description
        self.max_uses = max_uses
        self.expires_at = expires_at
        self.minimum_purchase = minimum_purchase
    
    def is_expired(self):
        """Check if coupon is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_usage_exceeded(self):
        """Check if coupon has exceeded max uses."""
        if self.max_uses is None:
            return False
        return self.times_used >= self.max_uses
    
    def is_valid(self):
        """Check if coupon is valid for use."""
        return (
            self.is_active and 
            not self.is_expired() and 
            not self.is_usage_exceeded()
        )
    
    def can_apply_to_amount(self, amount):
        """
        Check if coupon can be applied to purchase amount.
        
        Args:
            amount: Purchase amount
            
        Returns:
            bool: True if coupon can be applied
        """
        return self.is_valid() and amount >= self.minimum_purchase
    
    def calculate_discount(self, amount):
        """
        Calculate discount for given amount.
        
        Args:
            amount: Purchase amount
            
        Returns:
            float: Discount amount
        """
        if not self.can_apply_to_amount(amount):
            return 0.0
        
        if self.discount_percent > 0:
            return amount * (self.discount_percent / 100)
        elif self.discount_amount > 0:
            return min(self.discount_amount, amount)
        return 0.0
    
    def use(self):
        """Record a use of this coupon."""
        self.times_used += 1
    
    def deactivate(self):
        """Deactivate the coupon."""
        self.is_active = False
    
    def activate(self):
        """Activate the coupon."""
        self.is_active = True
    
    def remaining_uses(self):
        """Get remaining uses if limited."""
        if self.max_uses is None:
            return None
        return max(0, self.max_uses - self.times_used)
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'discount_percent': self.discount_percent,
            'discount_amount': self.discount_amount,
            'minimum_purchase': self.minimum_purchase,
            'max_uses': self.max_uses,
            'times_used': self.times_used,
            'remaining_uses': self.remaining_uses(),
            'is_active': self.is_active,
            'is_valid': self.is_valid(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def __repr__(self):
        return f'<Coupon {self.code}: {self.discount_percent}% off>'

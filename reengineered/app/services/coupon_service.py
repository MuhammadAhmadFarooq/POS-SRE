"""
Coupon Service - Manages discount coupons.
Replaces legacy couponNumber.txt management.
"""
import logging
from app import db
from app.models.coupon import Coupon

logger = logging.getLogger(__name__)


class CouponError(Exception):
    """Custom exception for coupon errors."""
    pass


class CouponService:
    """
    Coupon service for managing discount coupons.
    
    Improvements over legacy system:
    - Proper validation and expiration
    - Usage tracking
    - Multiple discount types
    """
    
    @staticmethod
    def get_all_coupons(active_only=False):
        """
        Get all coupons.
        
        Args:
            active_only: Only return active coupons
            
        Returns:
            list: List of coupons
        """
        query = Coupon.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Coupon.code).all()
    
    @staticmethod
    def get_coupon(id):
        """Get coupon by ID."""
        return Coupon.query.get(id)
    
    @staticmethod
    def get_coupon_by_code(code):
        """Get coupon by code."""
        return Coupon.query.filter_by(code=code.upper()).first()
    
    @staticmethod
    def create_coupon(code, discount_percent=0, discount_amount=0,
                     description=None, max_uses=None, expires_at=None,
                     minimum_purchase=0):
        """
        Create a new coupon.
        
        Args:
            code: Unique coupon code
            discount_percent: Percentage discount
            discount_amount: Fixed amount discount
            description: Coupon description
            max_uses: Maximum number of uses
            expires_at: Expiration datetime
            minimum_purchase: Minimum purchase amount
            
        Returns:
            Coupon: Created coupon
            
        Raises:
            CouponError: If creation fails
        """
        # Validate
        if discount_percent == 0 and discount_amount == 0:
            raise CouponError("Must specify either percentage or amount discount")
        
        if discount_percent > 0 and discount_amount > 0:
            raise CouponError("Cannot have both percentage and amount discount")
        
        if discount_percent < 0 or discount_percent > 100:
            raise CouponError("Discount percentage must be between 0 and 100")
        
        if discount_amount < 0:
            raise CouponError("Discount amount cannot be negative")
        
        # Check for existing code
        if Coupon.query.filter_by(code=code.upper()).first():
            raise CouponError(f"Coupon code {code} already exists")
        
        coupon = Coupon(
            code=code,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            description=description,
            max_uses=max_uses,
            expires_at=expires_at,
            minimum_purchase=minimum_purchase
        )
        
        db.session.add(coupon)
        db.session.commit()
        
        logger.info(f'Coupon created: {code}')
        
        return coupon
    
    @staticmethod
    def validate_coupon(code, purchase_amount=0):
        """
        Validate a coupon code.
        
        Args:
            code: Coupon code to validate
            purchase_amount: Current purchase amount
            
        Returns:
            dict: Validation result
        """
        coupon = CouponService.get_coupon_by_code(code)
        
        if not coupon:
            return {
                'valid': False,
                'message': 'Coupon not found'
            }
        
        if not coupon.is_active:
            return {
                'valid': False,
                'message': 'Coupon is inactive'
            }
        
        if coupon.is_expired():
            return {
                'valid': False,
                'message': 'Coupon has expired'
            }
        
        if coupon.is_usage_exceeded():
            return {
                'valid': False,
                'message': 'Coupon usage limit reached'
            }
        
        if purchase_amount < coupon.minimum_purchase:
            return {
                'valid': False,
                'message': f'Minimum purchase of ${coupon.minimum_purchase:.2f} required'
            }
        
        discount = coupon.calculate_discount(purchase_amount)
        
        return {
            'valid': True,
            'coupon': coupon,
            'discount': discount,
            'message': f'Coupon valid! Discount: ${discount:.2f}'
        }
    
    @staticmethod
    def use_coupon(coupon):
        """
        Record coupon usage.
        
        Args:
            coupon: Coupon model instance
            
        Returns:
            Coupon: Updated coupon
        """
        coupon.use()
        db.session.commit()
        
        logger.info(f'Coupon used: {coupon.code} (uses: {coupon.times_used})')
        
        return coupon
    
    @staticmethod
    def deactivate_coupon(coupon):
        """Deactivate a coupon."""
        coupon.deactivate()
        db.session.commit()
        
        logger.info(f'Coupon deactivated: {coupon.code}')
        
        return coupon
    
    @staticmethod
    def activate_coupon(coupon):
        """Activate a coupon."""
        coupon.activate()
        db.session.commit()
        
        logger.info(f'Coupon activated: {coupon.code}')
        
        return coupon
    
    @staticmethod
    def update_coupon(coupon, discount_percent=None, discount_amount=None,
                     max_uses=None, expires_at=None):
        """
        Update an existing coupon.
        
        Args:
            coupon: Coupon model instance
            discount_percent: New percentage discount
            discount_amount: New fixed amount discount
            max_uses: New maximum uses
            expires_at: New expiration datetime
            
        Returns:
            Coupon: Updated coupon
        """
        if discount_percent is not None:
            coupon.discount_percent = discount_percent
        if discount_amount is not None:
            coupon.discount_amount = discount_amount
        if max_uses is not None:
            coupon.max_uses = max_uses
        if expires_at is not None:
            coupon.expires_at = expires_at
        
        db.session.commit()
        
        logger.info(f'Coupon updated: {coupon.code}')
        
        return coupon
    
    @staticmethod
    def delete_coupon(coupon):
        """Delete a coupon (hard delete)."""
        code = coupon.code
        db.session.delete(coupon)
        db.session.commit()
        
        logger.info(f'Coupon deleted: {code}')
    
    @staticmethod
    def get_coupon_stats():
        """
        Get coupon statistics.
        
        Returns:
            dict: Coupon statistics
        """
        total = Coupon.query.count()
        active = Coupon.query.filter_by(is_active=True).count()
        total_uses = db.session.query(db.func.sum(Coupon.times_used)).scalar() or 0
        
        return {
            'total_coupons': total,
            'active_coupons': active,
            'inactive_coupons': total - active,
            'total_uses': total_uses
        }
    
    @staticmethod
    def generate_coupon_code(prefix='SAVE'):
        """
        Generate a unique coupon code.
        
        Args:
            prefix: Code prefix
            
        Returns:
            str: Unique coupon code
        """
        import random
        import string
        
        while True:
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            code = f'{prefix}{suffix}'
            
            if not Coupon.query.filter_by(code=code).first():
                return code

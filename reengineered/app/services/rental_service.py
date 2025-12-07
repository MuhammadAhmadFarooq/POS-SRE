"""
Rental Service - Manages rental operations.
Replaces legacy rental database and POR.java functionality.
"""
import logging
from datetime import datetime
from app import db
from app.models.rental import Rental
from app.models.customer import Customer
from app.models.item import Item

logger = logging.getLogger(__name__)


class RentalError(Exception):
    """Custom exception for rental errors."""
    pass


class RentalService:
    """
    Rental service for managing item rentals.
    
    Improvements over legacy system:
    - Proper date tracking
    - Late fee management
    - Customer rental history
    - Overdue tracking
    """
    
    @staticmethod
    def get_active_rentals(customer_phone=None):
        """
        Get all active (unreturned) rentals.
        
        Args:
            customer_phone: Optional filter by customer
            
        Returns:
            list: List of active rentals
        """
        query = Rental.query.filter_by(returned=False)
        
        if customer_phone:
            customer = Customer.query.filter_by(phone=customer_phone).first()
            if customer:
                query = query.filter_by(customer_id=customer.id)
            else:
                return []
        
        return query.order_by(Rental.due_date).all()
    
    @staticmethod
    def get_overdue_rentals():
        """
        Get all overdue rentals.
        
        Returns:
            list: List of overdue rentals
        """
        return Rental.query.filter(
            Rental.returned == False,
            Rental.due_date < datetime.utcnow()
        ).order_by(Rental.due_date).all()
    
    @staticmethod
    def get_rentals_by_customer(customer_phone):
        """
        Get all rentals for a customer.
        
        Args:
            customer_phone: Customer phone number
            
        Returns:
            list: List of rentals
        """
        customer = Customer.query.filter_by(phone=customer_phone).first()
        if not customer:
            return []
        
        return Rental.query.filter_by(customer_id=customer.id)\
            .order_by(Rental.rental_date.desc()).all()
    
    @staticmethod
    def get_rental(rental_id):
        """Get rental by ID."""
        return Rental.query.get(rental_id)
    
    @staticmethod
    def process_return(rental, late_fee_per_day=2.00):
        """
        Process a rental return.
        
        Args:
            rental: Rental model instance
            late_fee_per_day: Fee per day late
            
        Returns:
            float: Late fee charged
            
        Raises:
            RentalError: If return fails
        """
        if rental.returned:
            raise RentalError("Rental has already been returned")
        
        late_fee = rental.process_return(late_fee_per_day)
        db.session.commit()
        
        logger.info(f'Rental returned: ID {rental.id}, Late fee: ${late_fee:.2f}')
        
        return late_fee
    
    @staticmethod
    def extend_rental(rental, days):
        """
        Extend a rental's due date.
        
        Args:
            rental: Rental model instance
            days: Number of days to extend
            
        Returns:
            Rental: Updated rental
            
        Raises:
            RentalError: If extension fails
        """
        if rental.returned:
            raise RentalError("Cannot extend a returned rental")
        
        if days <= 0:
            raise RentalError("Extension days must be positive")
        
        rental.extend_rental(days)
        db.session.commit()
        
        logger.info(f'Rental extended: ID {rental.id}, New due date: {rental.due_date}')
        
        return rental
    
    @staticmethod
    def check_customer_has_overdue(customer_phone):
        """
        Check if customer has overdue rentals.
        
        Args:
            customer_phone: Customer phone number
            
        Returns:
            bool: True if customer has overdue rentals
        """
        customer = Customer.query.filter_by(phone=customer_phone).first()
        if not customer:
            return False
        
        overdue = Rental.query.filter(
            Rental.customer_id == customer.id,
            Rental.returned == False,
            Rental.due_date < datetime.utcnow()
        ).first()
        
        return overdue is not None
    
    @staticmethod
    def get_rental_stats():
        """
        Get rental statistics.
        
        Returns:
            dict: Rental statistics
        """
        total_active = Rental.query.filter_by(returned=False).count()
        total_overdue = len(RentalService.get_overdue_rentals())
        total_returned = Rental.query.filter_by(returned=True).count()
        
        # Total late fees collected
        total_late_fees = db.session.query(
            db.func.sum(Rental.late_fee)
        ).filter(Rental.returned == True).scalar() or 0.0
        
        # Pending late fees
        pending_late_fees = sum(
            r.calculate_late_fee() 
            for r in RentalService.get_overdue_rentals()
        )
        
        return {
            'active_rentals': total_active,
            'overdue_rentals': total_overdue,
            'returned_rentals': total_returned,
            'total_late_fees_collected': total_late_fees,
            'pending_late_fees': pending_late_fees
        }
    
    @staticmethod
    def get_due_soon_rentals(days=3):
        """
        Get rentals due within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            list: Rentals due soon
        """
        from datetime import timedelta
        
        cutoff = datetime.utcnow() + timedelta(days=days)
        
        return Rental.query.filter(
            Rental.returned == False,
            Rental.due_date <= cutoff,
            Rental.due_date >= datetime.utcnow()
        ).order_by(Rental.due_date).all()

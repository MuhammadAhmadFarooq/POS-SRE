"""
Employee Service - Manages employee CRUD operations.
Replaces legacy EmployeeManagement.java functionality.
"""
import logging
from app import db
from app.models.employee import Employee, EmployeeRole

logger = logging.getLogger(__name__)


class EmployeeError(Exception):
    """Custom exception for employee errors."""
    pass


class EmployeeService:
    """
    Employee service for managing employee records.
    
    Improvements over legacy system:
    - Proper CRUD operations
    - Role management
    - Search and filtering
    - Soft delete support
    """
    
    @staticmethod
    def get_all_employees(active_only=True):
        """
        Get all employees.
        
        Args:
            active_only: Only return active employees
            
        Returns:
            list: List of Employee objects
        """
        query = Employee.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Employee.last_name).all()
    
    @staticmethod
    def get_employee(id):
        """Get employee by database ID."""
        return Employee.query.get(id)
    
    @staticmethod
    def get_employee_by_employee_id(employee_id):
        """Get employee by employee ID."""
        return Employee.query.filter_by(employee_id=employee_id).first()
    
    @staticmethod
    def get_employee_by_username(username):
        """Get employee by username."""
        return Employee.query.filter_by(username=username).first()
    
    @staticmethod
    def search_employees(query):
        """
        Search employees by name or ID.
        
        Args:
            query: Search string
            
        Returns:
            list: Matching employees
        """
        search = f'%{query}%'
        return Employee.query.filter(
            db.or_(
                Employee.first_name.ilike(search),
                Employee.last_name.ilike(search),
                Employee.employee_id.ilike(search),
                Employee.username.ilike(search)
            ),
            Employee.is_active == True
        ).all()
    
    @staticmethod
    def create_employee(employee_id, username, password, first_name, last_name,
                       role=EmployeeRole.CASHIER):
        """
        Create a new employee.
        
        Args:
            employee_id: Unique employee ID
            username: Login username
            password: Plain text password
            first_name: First name
            last_name: Last name
            role: Employee role
            
        Returns:
            Employee: Created employee
            
        Raises:
            EmployeeError: If creation fails
        """
        # Check for existing employee_id
        if Employee.query.filter_by(employee_id=employee_id).first():
            raise EmployeeError(f'Employee ID {employee_id} already exists')
        
        # Check for existing username
        if Employee.query.filter_by(username=username).first():
            raise EmployeeError(f'Username {username} already exists')
        
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
        
        logger.info(f'Employee created: {employee_id} - {first_name} {last_name}')
        
        return employee
    
    @staticmethod
    def update_employee(employee, first_name=None, last_name=None, role=None):
        """
        Update employee details.
        
        Args:
            employee: Employee model instance
            first_name: New first name
            last_name: New last name
            role: New role
            
        Returns:
            Employee: Updated employee
        """
        if first_name is not None:
            employee.first_name = first_name
        if last_name is not None:
            employee.last_name = last_name
        if role is not None:
            employee.role = role
        
        db.session.commit()
        
        logger.info(f'Employee updated: {employee.employee_id}')
        
        return employee
    
    @staticmethod
    def delete_employee(employee):
        """
        Soft delete an employee.
        
        Args:
            employee: Employee model instance
            
        Returns:
            Employee: Deactivated employee
        """
        employee.is_active = False
        db.session.commit()
        
        logger.info(f'Employee deactivated: {employee.employee_id}')
        
        return employee
    
    @staticmethod
    def restore_employee(employee):
        """
        Restore a deactivated employee.
        
        Args:
            employee: Employee model instance
            
        Returns:
            Employee: Activated employee
        """
        employee.is_active = True
        db.session.commit()
        
        logger.info(f'Employee restored: {employee.employee_id}')
        
        return employee
    
    @staticmethod
    def get_employees_by_role(role):
        """
        Get employees by role.
        
        Args:
            role: Employee role
            
        Returns:
            list: Employees with specified role
        """
        return Employee.query.filter_by(role=role, is_active=True).all()
    
    @staticmethod
    def generate_employee_id():
        """
        Generate a new unique employee ID.
        
        Returns:
            str: New employee ID
        """
        # Get the highest existing ID number
        last_employee = Employee.query.order_by(Employee.id.desc()).first()
        
        if last_employee:
            # Try to extract number from existing ID
            try:
                num = int(last_employee.employee_id.replace('E', ''))
                return f'E{num + 1:04d}'
            except ValueError:
                pass
        
        return 'E0001'
    
    @staticmethod
    def get_employee_stats():
        """
        Get employee statistics.
        
        Returns:
            dict: Employee statistics
        """
        total = Employee.query.count()
        active = Employee.query.filter_by(is_active=True).count()
        admins = Employee.query.filter_by(role=EmployeeRole.ADMIN, is_active=True).count()
        managers = Employee.query.filter_by(role=EmployeeRole.MANAGER, is_active=True).count()
        cashiers = Employee.query.filter_by(role=EmployeeRole.CASHIER, is_active=True).count()
        
        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'admins': admins,
            'managers': managers,
            'cashiers': cashiers
        }

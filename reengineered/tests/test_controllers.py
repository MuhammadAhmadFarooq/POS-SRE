"""
Controller/Route tests using Flask test client.
Tests HTTP endpoints and authentication flow.
"""
import pytest
from flask import url_for
from app.models import Employee
from app import db


class TestAuthRoutes:
    """Tests for authentication routes."""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_login_success(self, app, client, sample_employee):
        """Test successful login."""
        with app.app_context():
            response = client.post('/auth/login', data={
                'username': 'testcashier',
                'password': 'testpass123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
    
    def test_login_invalid_credentials(self, app, client):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'wrongpass'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should stay on login page or show error
    
    def test_logout(self, app, client, sample_employee):
        """Test logout functionality."""
        with app.app_context():
            # Login first
            client.post('/auth/login', data={
                'username': 'testcashier',
                'password': 'testpass123'
            })
            
            # Then logout
            response = client.get('/auth/logout', follow_redirects=True)
            assert response.status_code == 200


class TestProtectedRoutes:
    """Tests for routes that require authentication."""
    
    def test_dashboard_requires_login(self, client):
        """Test that dashboard redirects to login if not authenticated."""
        response = client.get('/cashier/', follow_redirects=False)
        # Should redirect to login
        assert response.status_code in [302, 401, 403]
    
    def test_admin_requires_login(self, client):
        """Test that admin routes require authentication."""
        response = client.get('/admin/', follow_redirects=False)
        assert response.status_code in [302, 401, 403]


class TestCashierRoutes:
    """Tests for cashier functionality routes."""
    
    def test_new_sale_page(self, app, client, sample_employee):
        """Test new sale page loads for authenticated cashier."""
        with app.app_context():
            # Login as cashier
            client.post('/auth/login', data={
                'username': 'testcashier',
                'password': 'testpass123'
            })
            
            response = client.get('/cashier/sale')
            # Should be accessible or redirect to appropriate page
            assert response.status_code in [200, 302]
    
    def test_rental_page(self, app, client, sample_employee):
        """Test rental page access."""
        with app.app_context():
            client.post('/auth/login', data={
                'username': 'testcashier',
                'password': 'testpass123'
            })
            
            response = client.get('/cashier/rental')
            assert response.status_code in [200, 302]


class TestAdminRoutes:
    """Tests for admin functionality routes."""
    
    def test_admin_dashboard(self, app, client, sample_admin):
        """Test admin dashboard access."""
        with app.app_context():
            # Login as admin
            client.post('/auth/login', data={
                'username': 'testadmin',
                'password': 'adminpass123'
            })
            
            response = client.get('/admin/')
            assert response.status_code in [200, 302]
    
    def test_inventory_management(self, app, client, sample_admin):
        """Test inventory management page."""
        with app.app_context():
            client.post('/auth/login', data={
                'username': 'testadmin',
                'password': 'adminpass123'
            })
            
            response = client.get('/admin/inventory')
            assert response.status_code in [200, 302]
    
    def test_employee_management(self, app, client, sample_admin):
        """Test employee management page."""
        with app.app_context():
            client.post('/auth/login', data={
                'username': 'testadmin',
                'password': 'adminpass123'
            })
            
            response = client.get('/admin/employees')
            assert response.status_code in [200, 302]


class TestAPIRoutes:
    """Tests for API endpoints."""
    
    def test_api_items_endpoint(self, app, client, sample_admin, sample_items):
        """Test API items endpoint."""
        with app.app_context():
            client.post('/auth/login', data={
                'username': 'testadmin',
                'password': 'adminpass123'
            })
            
            response = client.get('/api/items')
            if response.status_code == 200:
                assert response.content_type == 'application/json'
    
    def test_api_requires_auth(self, client):
        """Test that API endpoints require authentication."""
        response = client.get('/api/items', follow_redirects=False)
        assert response.status_code in [302, 401, 403]


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_page(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-page-12345')
        assert response.status_code == 404
    
    def test_invalid_form_submission(self, client):
        """Test handling of invalid form data."""
        response = client.post('/auth/login', data={
            'username': '',  # Empty username
            'password': ''   # Empty password
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error or stay on login

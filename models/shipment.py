from database import execute_query
from datetime import datetime
import math
import random
import string
import sqlite3

class Shipment:
    def __init__(self, id=None, tracking_number=None, sender_name=None, sender_address=None,
                 recipient_name=None, recipient_address=None, package_description=None,
                 weight=None, status='pending', priority='standard', is_express=False,
                 shipping_cost=0.0, created_at=None, updated_at=None, user_id=None):
        self.id = id
        self.tracking_number = tracking_number
        self.sender_name = sender_name
        self.sender_address = sender_address
        self.recipient_name = recipient_name
        self.recipient_address = recipient_address
        self.package_description = package_description
        self.weight = weight or 0.0
        self.status = status
        self.priority = priority
        self.is_express = is_express
        self.shipping_cost = shipping_cost
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_id = user_id
    
    @staticmethod
    def generate_tracking_number():
        """Generate a unique tracking number"""
        while True:
            prefix = "SHP"
            random_part = ''.join(random.choices(string.digits, k=8))
            tracking_number = f"{prefix}{random_part}"
            
            # Check if tracking number already exists
            existing = execute_query(
                'SELECT id FROM shipments WHERE tracking_number = ?',
                (tracking_number,),
                fetch_one=True
            )
            if not existing:
                return tracking_number
    
    @staticmethod
    def calculate_shipping_cost(weight, priority, is_express):
        """Calculate shipping cost based on weight, priority, and express service"""
        try:
            base_cost = 5.0  # Base shipping cost
            weight_float = float(weight or 0)
            weight_cost = weight_float * 2.0  # $2 per kg
            
            priority_multiplier = {
                'standard': 1.0,
                'priority': 1.5,
                'urgent': 2.0
            }
            
            cost = base_cost + weight_cost
            cost *= priority_multiplier.get(priority, 1.0)
            
            if is_express:
                cost *= 1.8  # 80% surcharge for express
            
            return round(cost, 2)
        except (ValueError, TypeError):
            return 5.0  # Return base cost if calculation fails
    
    @staticmethod
    def find_by_id(shipment_id, user_id):
        """Find shipment by ID and user ID"""
        try:
            shipment_data = execute_query(
                'SELECT * FROM shipments WHERE id = ? AND user_id = ?',
                (shipment_id, user_id),
                fetch_one=True
            )
            if shipment_data:
                return Shipment._from_db_row(shipment_data)
            return None
        except Exception as e:
            print(f"Error finding shipment by ID: {e}")
            return None
    
    @staticmethod
    def find_by_tracking_number(tracking_number, user_id=None):
        """Find shipment by tracking number"""
        try:
            if user_id:
                shipment_data = execute_query(
                    'SELECT * FROM shipments WHERE tracking_number = ? AND user_id = ?',
                    (tracking_number.upper(), user_id),
                    fetch_one=True
                )
            else:
                shipment_data = execute_query(
                    'SELECT * FROM shipments WHERE tracking_number = ?',
                    (tracking_number.upper(),),
                    fetch_one=True
                )
            
            if shipment_data:
                return Shipment._from_db_row(shipment_data)
            return None
        except Exception as e:
            print(f"Error finding shipment by tracking number: {e}")
            return None
    
    @staticmethod
    def find_by_user(user_id, status_filter=None, priority_filter=None, 
                     express_filter=None, page=1, per_page=5):
        """Find shipments by user with filtering and pagination"""
        try:
            # Build query with filters
            query = 'SELECT * FROM shipments WHERE user_id = ?'
            params = [user_id]
            
            if status_filter:
                query += ' AND status = ?'
                params.append(status_filter)
            
            if priority_filter:
                query += ' AND priority = ?'
                params.append(priority_filter)
            
            if express_filter:
                query += ' AND is_express = ?'
                params.append(1 if express_filter == 'true' else 0)
            
            # Count total records for pagination
            count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
            total_count = execute_query(count_query, params, fetch_one=True)[0]
            
            # Get paginated results
            offset = (page - 1) * per_page
            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([per_page, offset])
            
            shipments_data = execute_query(query, params, fetch_all=True)
            shipments = [Shipment._from_db_row(shipment_data) for shipment_data in shipments_data]
            
            total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
            
            return shipments, total_pages, total_count
        except Exception as e:
            print(f"Error finding shipments by user: {e}")
            return [], 1, 0
    
    def save(self):
        """Save shipment to database"""
        try:
            if not self.tracking_number:
                self.tracking_number = self.generate_tracking_number()
            
            # Calculate shipping cost
            self.shipping_cost = self.calculate_shipping_cost(
                self.weight, self.priority, self.is_express
            )
            
            if self.id:
                # Update existing shipment
                execute_query(
                    '''UPDATE shipments 
                       SET tracking_number = ?, sender_name = ?, sender_address = ?,
                           recipient_name = ?, recipient_address = ?, package_description = ?,
                           weight = ?, status = ?, priority = ?, is_express = ?,
                           shipping_cost = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE id = ? AND user_id = ?''',
                    (self.tracking_number, self.sender_name, self.sender_address,
                     self.recipient_name, self.recipient_address, self.package_description,
                     self.weight, self.status, self.priority, self.is_express,
                     self.shipping_cost, self.id, self.user_id)
                )
            else:
                # Create new shipment
                self.id = execute_query(
                    '''INSERT INTO shipments (tracking_number, sender_name, sender_address,
                                            recipient_name, recipient_address, package_description,
                                            weight, status, priority, is_express, shipping_cost, user_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (self.tracking_number, self.sender_name, self.sender_address,
                     self.recipient_name, self.recipient_address, self.package_description,
                     self.weight, self.status, self.priority, self.is_express,
                     self.shipping_cost, self.user_id)
                )
            return self
        except sqlite3.IntegrityError as e:
            if 'tracking_number' in str(e):
                # Generate new tracking number and try again
                self.tracking_number = self.generate_tracking_number()
                return self.save()
            else:
                raise ValueError(f"Database constraint violation: {e}")
        except Exception as e:
            print(f"Error saving shipment: {e}")
            raise
    
    def delete(self):
        """Delete shipment from database"""
        try:
            if self.id:
                execute_query(
                    'DELETE FROM shipments WHERE id = ? AND user_id = ?',
                    (self.id, self.user_id)
                )
                return True
            return False
        except Exception as e:
            print(f"Error deleting shipment: {e}")
            raise
    
    @staticmethod
    def _from_db_row(row):
        """Create Shipment instance from database row"""
        return Shipment(
            id=row['id'],
            tracking_number=row['tracking_number'],
            sender_name=row['sender_name'],
            sender_address=row['sender_address'],
            recipient_name=row['recipient_name'],
            recipient_address=row['recipient_address'],
            package_description=row['package_description'],
            weight=row['weight'],
            status=row['status'],
            priority=row['priority'],
            is_express=bool(row['is_express']),
            shipping_cost=row['shipping_cost'],
            created_at=row['created_at'],
            updated_at=row['updated_at'] if 'updated_at' in row.keys() else None,
            user_id=row['user_id']
        )
    
    def to_dict(self):
        """Convert shipment to dictionary"""
        return {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'sender_name': self.sender_name,
            'sender_address': self.sender_address,
            'recipient_name': self.recipient_name,
            'recipient_address': self.recipient_address,
            'package_description': self.package_description,
            'weight': self.weight,
            'status': self.status,
            'priority': self.priority,
            'is_express': self.is_express,
            'shipping_cost': self.shipping_cost,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id
        }
    
    @staticmethod
    def get_status_choices():
        """Get available status choices"""
        return ['pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'returned']
    
    @staticmethod
    def get_priority_choices():
        """Get available priority choices"""
        return ['standard', 'priority', 'urgent']
    
    @staticmethod
    def get_status_stats(user_id):
        """Get shipment status statistics for a user"""
        try:
            stats = execute_query(
                '''SELECT status, COUNT(*) as count, 
                          AVG(shipping_cost) as avg_cost,
                          SUM(shipping_cost) as total_cost
                   FROM shipments 
                   WHERE user_id = ? 
                   GROUP BY status 
                   ORDER BY count DESC''',
                (user_id,),
                fetch_all=True
            )
            return [dict(stat) for stat in stats]
        except Exception as e:
            print(f"Error getting status stats: {e}")
            return []
    
    @staticmethod
    def search_shipments(user_id, search_term, page=1, per_page=5):
        """Search shipments by various fields"""
        try:
            search_pattern = f"%{search_term}%"
            query = '''SELECT * FROM shipments 
                       WHERE user_id = ? AND (
                           tracking_number LIKE ? OR
                           sender_name LIKE ? OR
                           recipient_name LIKE ? OR
                           package_description LIKE ?
                       )'''
            params = [user_id, search_pattern, search_pattern, search_pattern, search_pattern]
            
            # Count total results
            count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
            total_count = execute_query(count_query, params, fetch_one=True)[0]
            
            # Get paginated results
            offset = (page - 1) * per_page
            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([per_page, offset])
            
            shipments_data = execute_query(query, params, fetch_all=True)
            shipments = [Shipment._from_db_row(shipment_data) for shipment_data in shipments_data]
            
            total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
            
            return shipments, total_pages, total_count
        except Exception as e:
            print(f"Error searching shipments: {e}")
            return [], 1, 0

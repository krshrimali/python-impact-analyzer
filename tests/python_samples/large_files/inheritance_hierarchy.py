# Large Python file with deep inheritance hierarchies
# This file simulates a complex object-oriented system with multiple levels of inheritance

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
import datetime
import uuid
import random
import math

# Base classes
class Entity(ABC):
    """Base class for all entities in the system."""
    
    def __init__(self, entity_id: str = None):
        self.entity_id = entity_id or str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
    
    def update(self) -> None:
        """Update the entity's timestamp."""
        self.updated_at = datetime.datetime.now()
    
    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary."""
        return {
            "entity_id": self.entity_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "entity_type": self.__class__.__name__
        }
    
    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Entity':
        """Create an entity from a dictionary."""
        entity = cls(entity_id=data.get("entity_id"))
        entity.created_at = datetime.datetime.fromisoformat(data.get("created_at"))
        entity.updated_at = datetime.datetime.fromisoformat(data.get("updated_at"))
        return entity
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.entity_id})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.entity_id == other.entity_id


class ValueObject(ABC):
    """Base class for immutable value objects."""
    
    @abstractmethod
    def equals(self, other: 'ValueObject') -> bool:
        """Check if two value objects are equal."""
        pass
    
    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Convert the value object to a dictionary."""
        pass
    
    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'ValueObject':
        """Create a value object from a dictionary."""
        pass


class Aggregate(Entity):
    """Base class for aggregate roots."""
    
    def __init__(self, entity_id: str = None):
        super().__init__(entity_id)
        self._events: List[DomainEvent] = []
    
    def add_event(self, event: 'DomainEvent') -> None:
        """Add a domain event to the aggregate."""
        self._events.append(event)
    
    def clear_events(self) -> List['DomainEvent']:
        """Clear and return all pending events."""
        events = self._events.copy()
        self._events.clear()
        return events
    
    @abstractmethod
    def apply_event(self, event: 'DomainEvent') -> None:
        """Apply a domain event to the aggregate."""
        pass


class DomainEvent(ABC):
    """Base class for domain events."""
    
    def __init__(self, aggregate_id: str):
        self.event_id = str(uuid.uuid4())
        self.aggregate_id = aggregate_id
        self.timestamp = datetime.datetime.now()
    
    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Convert the event to a dictionary."""
        return {
            "event_id": self.event_id,
            "aggregate_id": self.aggregate_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.__class__.__name__
        }
    
    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create an event from a dictionary."""
        event = cls(aggregate_id=data.get("aggregate_id"))
        event.event_id = data.get("event_id")
        event.timestamp = datetime.datetime.fromisoformat(data.get("timestamp"))
        return event


class Repository(ABC):
    """Base class for repositories."""
    
    @abstractmethod
    def save(self, aggregate: Aggregate) -> None:
        """Save an aggregate to the repository."""
        pass
    
    @abstractmethod
    def find_by_id(self, aggregate_id: str) -> Optional[Aggregate]:
        """Find an aggregate by its ID."""
        pass
    
    @abstractmethod
    def delete(self, aggregate_id: str) -> None:
        """Delete an aggregate from the repository."""
        pass


class Service(ABC):
    """Base class for domain services."""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the service."""
        pass


# Value Objects
class Address(ValueObject):
    """Address value object."""
    
    def __init__(self, street: str, city: str, state: str, postal_code: str, country: str):
        self.street = street
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.country = country
    
    def equals(self, other: 'Address') -> bool:
        if not isinstance(other, Address):
            return False
        return (
            self.street == other.street and
            self.city == other.city and
            self.state == other.state and
            self.postal_code == other.postal_code and
            self.country == other.country
        )
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Address':
        return cls(
            street=data.get("street", ""),
            city=data.get("city", ""),
            state=data.get("state", ""),
            postal_code=data.get("postal_code", ""),
            country=data.get("country", "")
        )
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"


class Money(ValueObject):
    """Money value object."""
    
    def __init__(self, amount: float, currency: str):
        self.amount = amount
        self.currency = currency
    
    def equals(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        return Money(self.amount * factor, self.currency)
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "currency": self.currency
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Money':
        return cls(
            amount=data.get("amount", 0.0),
            currency=data.get("currency", "USD")
        )
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


class Email(ValueObject):
    """Email value object."""
    
    def __init__(self, address: str):
        if not self._is_valid_email(address):
            raise ValueError(f"Invalid email address: {address}")
        self.address = address
    
    def _is_valid_email(self, address: str) -> bool:
        # Simple validation for demonstration
        return "@" in address and "." in address.split("@")[1]
    
    def equals(self, other: 'Email') -> bool:
        if not isinstance(other, Email):
            return False
        return self.address.lower() == other.address.lower()
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "address": self.address
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Email':
        return cls(address=data.get("address", ""))
    
    def __str__(self) -> str:
        return self.address


# Domain Entities
class Person(Entity):
    """Person entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", email: Optional[Email] = None, address: Optional[Address] = None):
        super().__init__(entity_id)
        self.name = name
        self.email = email
        self.address = address
    
    def update_name(self, name: str) -> None:
        """Update the person's name."""
        self.name = name
        self.update()
    
    def update_email(self, email: Email) -> None:
        """Update the person's email."""
        self.email = email
        self.update()
    
    def update_address(self, address: Address) -> None:
        """Update the person's address."""
        self.address = address
        self.update()
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "name": self.name,
            "email": self.email.serialize() if self.email else None,
            "address": self.address.serialize() if self.address else None
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Person':
        person = super().deserialize(data)
        person.name = data.get("name", "")
        
        email_data = data.get("email")
        if email_data:
            person.email = Email.deserialize(email_data)
        
        address_data = data.get("address")
        if address_data:
            person.address = Address.deserialize(address_data)
        
        return person


class Customer(Person):
    """Customer entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", email: Optional[Email] = None, 
                 address: Optional[Address] = None, customer_number: str = "", 
                 loyalty_points: int = 0):
        super().__init__(entity_id, name, email, address)
        self.customer_number = customer_number or f"CUST-{random.randint(10000, 99999)}"
        self.loyalty_points = loyalty_points
        self.orders: List[str] = []  # List of order IDs
    
    def add_loyalty_points(self, points: int) -> None:
        """Add loyalty points to the customer."""
        self.loyalty_points += points
        self.update()
    
    def use_loyalty_points(self, points: int) -> bool:
        """Use loyalty points if available."""
        if points <= self.loyalty_points:
            self.loyalty_points -= points
            self.update()
            return True
        return False
    
    def add_order(self, order_id: str) -> None:
        """Add an order to the customer's history."""
        if order_id not in self.orders:
            self.orders.append(order_id)
            self.update()
    
    def get_order_count(self) -> int:
        """Get the number of orders placed by the customer."""
        return len(self.orders)
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "customer_number": self.customer_number,
            "loyalty_points": self.loyalty_points,
            "orders": self.orders
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Customer':
        customer = super().deserialize(data)
        customer.customer_number = data.get("customer_number", "")
        customer.loyalty_points = data.get("loyalty_points", 0)
        customer.orders = data.get("orders", [])
        return customer


class Employee(Person):
    """Employee entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", email: Optional[Email] = None, 
                 address: Optional[Address] = None, employee_id: str = "", 
                 department: str = "", position: str = "", salary: Optional[Money] = None):
        super().__init__(entity_id, name, email, address)
        self.employee_id = employee_id or f"EMP-{random.randint(10000, 99999)}"
        self.department = department
        self.position = position
        self.salary = salary
        self.hire_date = datetime.date.today()
        self.reports_to: Optional[str] = None  # Employee ID of manager
    
    def promote(self, new_position: str, salary_increase: Money) -> None:
        """Promote the employee to a new position with a salary increase."""
        self.position = new_position
        if self.salary:
            self.salary = self.salary.add(salary_increase)
        else:
            self.salary = salary_increase
        self.update()
    
    def transfer_department(self, new_department: str) -> None:
        """Transfer the employee to a new department."""
        self.department = new_department
        self.update()
    
    def assign_manager(self, manager_id: str) -> None:
        """Assign a manager to the employee."""
        self.reports_to = manager_id
        self.update()
    
    def calculate_years_of_service(self) -> float:
        """Calculate the employee's years of service."""
        today = datetime.date.today()
        delta = today - self.hire_date
        return delta.days / 365.25
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "employee_id": self.employee_id,
            "department": self.department,
            "position": self.position,
            "salary": self.salary.serialize() if self.salary else None,
            "hire_date": self.hire_date.isoformat(),
            "reports_to": self.reports_to
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Employee':
        employee = super().deserialize(data)
        employee.employee_id = data.get("employee_id", "")
        employee.department = data.get("department", "")
        employee.position = data.get("position", "")
        
        salary_data = data.get("salary")
        if salary_data:
            employee.salary = Money.deserialize(salary_data)
        
        hire_date = data.get("hire_date")
        if hire_date:
            employee.hire_date = datetime.date.fromisoformat(hire_date)
        
        employee.reports_to = data.get("reports_to")
        
        return employee


class Manager(Employee):
    """Manager entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", email: Optional[Email] = None, 
                 address: Optional[Address] = None, employee_id: str = "", 
                 department: str = "", position: str = "", salary: Optional[Money] = None,
                 management_level: int = 1):
        super().__init__(entity_id, name, email, address, employee_id, department, position, salary)
        self.management_level = management_level
        self.direct_reports: List[str] = []  # List of employee IDs
    
    def add_direct_report(self, employee_id: str) -> None:
        """Add a direct report to the manager."""
        if employee_id not in self.direct_reports:
            self.direct_reports.append(employee_id)
            self.update()
    
    def remove_direct_report(self, employee_id: str) -> None:
        """Remove a direct report from the manager."""
        if employee_id in self.direct_reports:
            self.direct_reports.remove(employee_id)
            self.update()
    
    def get_team_size(self) -> int:
        """Get the size of the manager's team."""
        return len(self.direct_reports)
    
    def promote_management_level(self) -> None:
        """Promote the manager to the next management level."""
        self.management_level += 1
        self.update()
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "management_level": self.management_level,
            "direct_reports": self.direct_reports
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Manager':
        manager = super().deserialize(data)
        manager.management_level = data.get("management_level", 1)
        manager.direct_reports = data.get("direct_reports", [])
        return manager


class ExecutiveManager(Manager):
    """Executive manager entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", email: Optional[Email] = None, 
                 address: Optional[Address] = None, employee_id: str = "", 
                 department: str = "", position: str = "", salary: Optional[Money] = None,
                 management_level: int = 3, stock_options: int = 0):
        super().__init__(entity_id, name, email, address, employee_id, department, position, salary, management_level)
        self.stock_options = stock_options
        self.executive_benefits: List[str] = []
    
    def grant_stock_options(self, options: int) -> None:
        """Grant stock options to the executive."""
        self.stock_options += options
        self.update()
    
    def add_executive_benefit(self, benefit: str) -> None:
        """Add an executive benefit."""
        if benefit not in self.executive_benefits:
            self.executive_benefits.append(benefit)
            self.update()
    
    def calculate_total_compensation(self) -> Money:
        """Calculate the executive's total compensation including stock options."""
        if not self.salary:
            return Money(0, "USD")
        
        # Simplified calculation for demonstration
        stock_value = self.stock_options * 100  # Assume each option is worth $100
        return self.salary.add(Money(stock_value, self.salary.currency))
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "stock_options": self.stock_options,
            "executive_benefits": self.executive_benefits
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'ExecutiveManager':
        executive = super().deserialize(data)
        executive.stock_options = data.get("stock_options", 0)
        executive.executive_benefits = data.get("executive_benefits", [])
        return executive


# Product-related entities
class Product(Entity):
    """Product entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", description: str = "", 
                 price: Optional[Money] = None, sku: str = ""):
        super().__init__(entity_id)
        self.name = name
        self.description = description
        self.price = price
        self.sku = sku or f"SKU-{random.randint(10000, 99999)}"
        self.categories: List[str] = []
        self.is_active = True
    
    def update_price(self, price: Money) -> None:
        """Update the product's price."""
        self.price = price
        self.update()
    
    def add_category(self, category: str) -> None:
        """Add a category to the product."""
        if category not in self.categories:
            self.categories.append(category)
            self.update()
    
    def deactivate(self) -> None:
        """Deactivate the product."""
        self.is_active = False
        self.update()
    
    def activate(self) -> None:
        """Activate the product."""
        self.is_active = True
        self.update()
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "name": self.name,
            "description": self.description,
            "price": self.price.serialize() if self.price else None,
            "sku": self.sku,
            "categories": self.categories,
            "is_active": self.is_active
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Product':
        product = super().deserialize(data)
        product.name = data.get("name", "")
        product.description = data.get("description", "")
        
        price_data = data.get("price")
        if price_data:
            product.price = Money.deserialize(price_data)
        
        product.sku = data.get("sku", "")
        product.categories = data.get("categories", [])
        product.is_active = data.get("is_active", True)
        
        return product


class PhysicalProduct(Product):
    """Physical product entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", description: str = "", 
                 price: Optional[Money] = None, sku: str = "", weight: float = 0.0, 
                 dimensions: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        super().__init__(entity_id, name, description, price, sku)
        self.weight = weight  # in kg
        self.dimensions = dimensions  # (length, width, height) in cm
        self.inventory_count = 0
        self.reorder_threshold = 10
    
    def add_inventory(self, quantity: int) -> None:
        """Add inventory to the product."""
        self.inventory_count += quantity
        self.update()
    
    def remove_inventory(self, quantity: int) -> bool:
        """Remove inventory from the product if available."""
        if quantity <= self.inventory_count:
            self.inventory_count -= quantity
            self.update()
            return True
        return False
    
    def needs_reorder(self) -> bool:
        """Check if the product needs to be reordered."""
        return self.inventory_count <= self.reorder_threshold
    
    def calculate_volume(self) -> float:
        """Calculate the product's volume in cubic centimeters."""
        length, width, height = self.dimensions
        return length * width * height
    
    def calculate_shipping_cost(self, distance: float) -> Money:
        """Calculate the shipping cost based on weight and distance."""
        if not self.price:
            return Money(0, "USD")
        
        # Simplified calculation for demonstration
        base_cost = 5.0  # Base shipping cost in the same currency as the product
        weight_factor = self.weight * 0.1  # $0.10 per kg
        distance_factor = distance * 0.001  # $0.001 per km
        
        shipping_cost = base_cost + weight_factor + distance_factor
        return Money(shipping_cost, self.price.currency)
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "weight": self.weight,
            "dimensions": self.dimensions,
            "inventory_count": self.inventory_count,
            "reorder_threshold": self.reorder_threshold
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'PhysicalProduct':
        product = super().deserialize(data)
        product.weight = data.get("weight", 0.0)
        product.dimensions = data.get("dimensions", (0.0, 0.0, 0.0))
        product.inventory_count = data.get("inventory_count", 0)
        product.reorder_threshold = data.get("reorder_threshold", 10)
        return product


class DigitalProduct(Product):
    """Digital product entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", description: str = "", 
                 price: Optional[Money] = None, sku: str = "", file_size: float = 0.0, 
                 download_url: str = ""):
        super().__init__(entity_id, name, description, price, sku)
        self.file_size = file_size  # in MB
        self.download_url = download_url
        self.license_type = "standard"
        self.version = "1.0.0"
    
    def update_version(self, version: str) -> None:
        """Update the product's version."""
        self.version = version
        self.update()
    
    def update_download_url(self, url: str) -> None:
        """Update the product's download URL."""
        self.download_url = url
        self.update()
    
    def update_license_type(self, license_type: str) -> None:
        """Update the product's license type."""
        self.license_type = license_type
        self.update()
    
    def generate_download_link(self, customer_id: str) -> str:
        """Generate a unique download link for a customer."""
        timestamp = int(datetime.datetime.now().timestamp())
        token = f"{customer_id}-{timestamp}-{uuid.uuid4()}"
        return f"{self.download_url}?token={token}"
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "file_size": self.file_size,
            "download_url": self.download_url,
            "license_type": self.license_type,
            "version": self.version
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'DigitalProduct':
        product = super().deserialize(data)
        product.file_size = data.get("file_size", 0.0)
        product.download_url = data.get("download_url", "")
        product.license_type = data.get("license_type", "standard")
        product.version = data.get("version", "1.0.0")
        return product


class SubscriptionProduct(DigitalProduct):
    """Subscription product entity."""
    
    def __init__(self, entity_id: str = None, name: str = "", description: str = "", 
                 price: Optional[Money] = None, sku: str = "", file_size: float = 0.0, 
                 download_url: str = "", billing_period: str = "monthly"):
        super().__init__(entity_id, name, description, price, sku, file_size, download_url)
        self.billing_period = billing_period  # "monthly", "quarterly", "annual"
        self.trial_period_days = 0
        self.features: List[str] = []
    
    def set_trial_period(self, days: int) -> None:
        """Set the trial period in days."""
        self.trial_period_days = days
        self.update()
    
    def add_feature(self, feature: str) -> None:
        """Add a feature to the subscription."""
        if feature not in self.features:
            self.features.append(feature)
            self.update()
    
    def remove_feature(self, feature: str) -> None:
        """Remove a feature from the subscription."""
        if feature in self.features:
            self.features.remove(feature)
            self.update()
    
    def calculate_annual_cost(self) -> Money:
        """Calculate the annual cost of the subscription."""
        if not self.price:
            return Money(0, "USD")
        
        if self.billing_period == "monthly":
            return self.price.multiply(12)
        elif self.billing_period == "quarterly":
            return self.price.multiply(4)
        elif self.billing_period == "annual":
            return self.price.multiply(1)
        else:
            return Money(0, self.price.currency)
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "billing_period": self.billing_period,
            "trial_period_days": self.trial_period_days,
            "features": self.features
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'SubscriptionProduct':
        product = super().deserialize(data)
        product.billing_period = data.get("billing_period", "monthly")
        product.trial_period_days = data.get("trial_period_days", 0)
        product.features = data.get("features", [])
        return product


# Order-related entities
class OrderItem(Entity):
    """Order item entity."""
    
    def __init__(self, entity_id: str = None, product_id: str = "", quantity: int = 1, 
                 unit_price: Optional[Money] = None):
        super().__init__(entity_id)
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
    
    def update_quantity(self, quantity: int) -> None:
        """Update the item's quantity."""
        self.quantity = quantity
        self.update()
    
    def calculate_total(self) -> Optional[Money]:
        """Calculate the total price for this item."""
        if not self.unit_price:
            return None
        return self.unit_price.multiply(self.quantity)
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price.serialize() if self.unit_price else None
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'OrderItem':
        item = super().deserialize(data)
        item.product_id = data.get("product_id", "")
        item.quantity = data.get("quantity", 1)
        
        unit_price_data = data.get("unit_price")
        if unit_price_data:
            item.unit_price = Money.deserialize(unit_price_data)
        
        return item


class Order(Aggregate):
    """Order aggregate."""
    
    def __init__(self, entity_id: str = None, customer_id: str = ""):
        super().__init__(entity_id)
        self.customer_id = customer_id
        self.order_number = f"ORD-{random.randint(10000, 99999)}"
        self.order_date = datetime.datetime.now()
        self.status = "pending"
        self.items: List[OrderItem] = []
        self.shipping_address: Optional[Address] = None
        self.billing_address: Optional[Address] = None
        self.shipping_cost: Optional[Money] = None
        self.tax_amount: Optional[Money] = None
        self.discount_amount: Optional[Money] = None
    
    def add_item(self, item: OrderItem) -> None:
        """Add an item to the order."""
        self.items.append(item)
        self.update()
        self.add_event(OrderItemAddedEvent(self.entity_id, item.entity_id))
    
    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the order."""
        for i, item in enumerate(self.items):
            if item.entity_id == item_id:
                del self.items[i]
                self.update()
                self.add_event(OrderItemRemovedEvent(self.entity_id, item_id))
                return True
        return False
    
    def update_status(self, status: str) -> None:
        """Update the order's status."""
        old_status = self.status
        self.status = status
        self.update()
        self.add_event(OrderStatusChangedEvent(self.entity_id, old_status, status))
    
    def set_shipping_address(self, address: Address) -> None:
        """Set the shipping address."""
        self.shipping_address = address
        self.update()
    
    def set_billing_address(self, address: Address) -> None:
        """Set the billing address."""
        self.billing_address = address
        self.update()
    
    def set_shipping_cost(self, cost: Money) -> None:
        """Set the shipping cost."""
        self.shipping_cost = cost
        self.update()
    
    def set_tax_amount(self, tax: Money) -> None:
        """Set the tax amount."""
        self.tax_amount = tax
        self.update()
    
    def set_discount_amount(self, discount: Money) -> None:
        """Set the discount amount."""
        self.discount_amount = discount
        self.update()
    
    def calculate_subtotal(self) -> Optional[Money]:
        """Calculate the subtotal of all items."""
        if not self.items:
            return None
        
        subtotal = None
        for item in self.items:
            item_total = item.calculate_total()
            if item_total:
                if subtotal is None:
                    subtotal = item_total
                else:
                    subtotal = subtotal.add(item_total)
        
        return subtotal
    
    def calculate_total(self) -> Optional[Money]:
        """Calculate the total order amount including shipping, tax, and discounts."""
        subtotal = self.calculate_subtotal()
        if not subtotal:
            return None
        
        total = subtotal
        
        if self.shipping_cost:
            total = total.add(self.shipping_cost)
        
        if self.tax_amount:
            total = total.add(self.tax_amount)
        
        if self.discount_amount:
            total = total.subtract(self.discount_amount)
        
        return total
    
    def apply_event(self, event: DomainEvent) -> None:
        """Apply a domain event to the order."""
        if isinstance(event, OrderItemAddedEvent):
            # In a real implementation, we would reconstruct the item from the event
            pass
        elif isinstance(event, OrderItemRemovedEvent):
            for i, item in enumerate(self.items):
                if item.entity_id == event.item_id:
                    del self.items[i]
                    break
        elif isinstance(event, OrderStatusChangedEvent):
            self.status = event.new_status
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "customer_id": self.customer_id,
            "order_number": self.order_number,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "items": [item.serialize() for item in self.items],
            "shipping_address": self.shipping_address.serialize() if self.shipping_address else None,
            "billing_address": self.billing_address.serialize() if self.billing_address else None,
            "shipping_cost": self.shipping_cost.serialize() if self.shipping_cost else None,
            "tax_amount": self.tax_amount.serialize() if self.tax_amount else None,
            "discount_amount": self.discount_amount.serialize() if self.discount_amount else None
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'Order':
        order = super().deserialize(data)
        order.customer_id = data.get("customer_id", "")
        order.order_number = data.get("order_number", "")
        
        order_date = data.get("order_date")
        if order_date:
            order.order_date = datetime.datetime.fromisoformat(order_date)
        
        order.status = data.get("status", "pending")
        
        items_data = data.get("items", [])
        for item_data in items_data:
            order.items.append(OrderItem.deserialize(item_data))
        
        shipping_address_data = data.get("shipping_address")
        if shipping_address_data:
            order.shipping_address = Address.deserialize(shipping_address_data)
        
        billing_address_data = data.get("billing_address")
        if billing_address_data:
            order.billing_address = Address.deserialize(billing_address_data)
        
        shipping_cost_data = data.get("shipping_cost")
        if shipping_cost_data:
            order.shipping_cost = Money.deserialize(shipping_cost_data)
        
        tax_amount_data = data.get("tax_amount")
        if tax_amount_data:
            order.tax_amount = Money.deserialize(tax_amount_data)
        
        discount_amount_data = data.get("discount_amount")
        if discount_amount_data:
            order.discount_amount = Money.deserialize(discount_amount_data)
        
        return order


# Domain Events
class OrderItemAddedEvent(DomainEvent):
    """Event raised when an item is added to an order."""
    
    def __init__(self, aggregate_id: str, item_id: str):
        super().__init__(aggregate_id)
        self.item_id = item_id
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "item_id": self.item_id
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'OrderItemAddedEvent':
        event = super().deserialize(data)
        event.item_id = data.get("item_id", "")
        return event


class OrderItemRemovedEvent(DomainEvent):
    """Event raised when an item is removed from an order."""
    
    def __init__(self, aggregate_id: str, item_id: str):
        super().__init__(aggregate_id)
        self.item_id = item_id
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "item_id": self.item_id
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'OrderItemRemovedEvent':
        event = super().deserialize(data)
        event.item_id = data.get("item_id", "")
        return event


class OrderStatusChangedEvent(DomainEvent):
    """Event raised when an order's status changes."""
    
    def __init__(self, aggregate_id: str, old_status: str, new_status: str):
        super().__init__(aggregate_id)
        self.old_status = old_status
        self.new_status = new_status
    
    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "old_status": self.old_status,
            "new_status": self.new_status
        })
        return data
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'OrderStatusChangedEvent':
        event = super().deserialize(data)
        event.old_status = data.get("old_status", "")
        event.new_status = data.get("new_status", "")
        return event


# Repositories
class InMemoryOrderRepository(Repository):
    """In-memory implementation of an order repository."""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
    
    def save(self, aggregate: Aggregate) -> None:
        """Save an order to the repository."""
        if not isinstance(aggregate, Order):
            raise ValueError("Can only save Order aggregates")
        
        self.orders[aggregate.entity_id] = aggregate
    
    def find_by_id(self, aggregate_id: str) -> Optional[Aggregate]:
        """Find an order by its ID."""
        return self.orders.get(aggregate_id)
    
    def delete(self, aggregate_id: str) -> None:
        """Delete an order from the repository."""
        if aggregate_id in self.orders:
            del self.orders[aggregate_id]


# Services
class OrderService(Service):
    """Service for order-related operations."""
    
    def __init__(self, order_repository: Repository):
        self.order_repository = order_repository
    
    def execute(self, command: str, *args, **kwargs) -> Any:
        """Execute a command on the service."""
        if command == "create_order":
            return self.create_order(*args, **kwargs)
        elif command == "add_item_to_order":
            return self.add_item_to_order(*args, **kwargs)
        elif command == "place_order":
            return self.place_order(*args, **kwargs)
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def create_order(self, customer_id: str) -> Order:
        """Create a new order for a customer."""
        order = Order(customer_id=customer_id)
        self.order_repository.save(order)
        return order
    
    def add_item_to_order(self, order_id: str, product_id: str, quantity: int, unit_price: Money) -> bool:
        """Add an item to an order."""
        order = self.order_repository.find_by_id(order_id)
        if not order or not isinstance(order, Order):
            return False
        
        item = OrderItem(product_id=product_id, quantity=quantity, unit_price=unit_price)
        order.add_item(item)
        self.order_repository.save(order)
        return True
    
    def place_order(self, order_id: str) -> bool:
        """Place an order (change its status to 'placed')."""
        order = self.order_repository.find_by_id(order_id)
        if not order or not isinstance(order, Order):
            return False
        
        if not order.items:
            return False
        
        if not order.shipping_address:
            return False
        
        order.update_status("placed")
        self.order_repository.save(order)
        return True


# Example usage
def main():
    # Create a customer
    email = Email("john.doe@example.com")
    address = Address("123 Main St", "Anytown", "CA", "12345", "USA")
    customer = Customer(name="John Doe", email=email, address=address)
    
    # Create some products
    phone = PhysicalProduct(
        name="Smartphone XL",
        description="The latest smartphone with advanced features",
        price=Money(799.99, "USD"),
        weight=0.2,
        dimensions=(15.0, 7.5, 0.8)
    )
    
    software = DigitalProduct(
        name="Photo Editor Pro",
        description="Professional photo editing software",
        price=Money(149.99, "USD"),
        file_size=250.0,
        download_url="https://example.com/downloads/photo-editor-pro"
    )
    
    subscription = SubscriptionProduct(
        name="Cloud Storage Plus",
        description="Premium cloud storage service",
        price=Money(9.99, "USD"),
        billing_period="monthly",
        download_url="https://example.com/cloud-storage"
    )
    subscription.add_feature("50GB storage")
    subscription.add_feature("File versioning")
    subscription.add_feature("Secure sharing")
    
    # Create an order repository and service
    order_repository = InMemoryOrderRepository()
    order_service = OrderService(order_repository)
    
    # Create an order
    order = order_service.create_order(customer.entity_id)
    
    # Add items to the order
    order_service.add_item_to_order(order.entity_id, phone.entity_id, 1, phone.price)
    order_service.add_item_to_order(order.entity_id, software.entity_id, 1, software.price)
    order_service.add_item_to_order(order.entity_id, subscription.entity_id, 12, subscription.price)
    
    # Set shipping and billing addresses
    order.set_shipping_address(address)
    order.set_billing_address(address)
    
    # Set shipping cost and tax
    order.set_shipping_cost(Money(10.00, "USD"))
    subtotal = order.calculate_subtotal()
    if subtotal:
        tax_rate = 0.08  # 8% tax rate
        tax_amount = subtotal.multiply(tax_rate)
        order.set_tax_amount(tax_amount)
    
    # Apply a discount
    order.set_discount_amount(Money(50.00, "USD"))
    
    # Place the order
    success = order_service.place_order(order.entity_id)
    
    # Print order details
    if success:
        print(f"Order {order.order_number} placed successfully")
        print(f"Customer: {customer.name}")
        print(f"Shipping to: {order.shipping_address}")
        print("\nItems:")
        for item in order.items:
            total = item.calculate_total()
            print(f"- {item.product_id}: {item.quantity} x {item.unit_price} = {total}")
        
        print(f"\nSubtotal: {order.calculate_subtotal()}")
        print(f"Shipping: {order.shipping_cost}")
        print(f"Tax: {order.tax_amount}")
        print(f"Discount: {order.discount_amount}")
        print(f"Total: {order.calculate_total()}")
    else:
        print("Failed to place order")

if __name__ == "__main__":
    main()
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    """
    Represents a company in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    employees = db.relationship('Employee', backref='company', lazy=True)

    def to_dict(self):
        """Serializes the Company object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'employee_count': len(self.employees)
        }

    def __repr__(self):
        return f'<Company {self.name}>'

class Employee(db.Model):
    """
    Represents an employee in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    salary = db.Column(db.Float, nullable=True)
    manager_id = db.Column(db.Integer, nullable=True)
    department_id = db.Column(db.Integer, nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    def to_dict(self):
        """Serializes the Employee object to a dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'salary': self.salary,
            'manager_id': self.manager_id,
            'department_id': self.department_id,
            'company_name': self.company.name if self.company else None
        }

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'

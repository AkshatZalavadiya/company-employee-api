from flask import Blueprint, request, jsonify
import pandas as pd
from .models import db, Company, Employee

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    API endpoint to upload a CSV or Excel file, process it, and insert data into the database.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = file.filename
    if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        return jsonify({"error": "Invalid file type. Please upload a CSV or XLSX file."}), 400

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        else: # .xlsx
            df = pd.read_excel(file)

        unique_companies = df['COMPANY_NAME'].unique()
        company_map = {c.name: c.id for c in Company.query.filter(Company.name.in_(unique_companies)).all()}
        
        new_company_names = set(unique_companies) - set(company_map.keys())
        if new_company_names:
            new_companies = [Company(name=name) for name in new_company_names]
            db.session.bulk_save_objects(new_companies, return_defaults=True)
            db.session.commit()
            for company in new_companies:
                company_map[company.name] = company.id

        # Get all employee IDs from the uploaded file
        incoming_employee_ids = df['EMPLOYEE_ID'].tolist()
        
        # Find which of these IDs already exist in the database
        existing_employees = db.session.query(Employee.id).filter(Employee.id.in_(incoming_employee_ids)).all()
        existing_employee_ids = {e_id for e_id, in existing_employees}

        employee_mappings = []
        for _, row in df.iterrows():
            employee_id = row['EMPLOYEE_ID']
            if employee_id not in existing_employee_ids:
                company_id = company_map.get(row['COMPANY_NAME'])
                if company_id:
                    employee_mappings.append({
                        'id': row['EMPLOYEE_ID'],
                        'first_name': row['FIRST_NAME'],
                        'last_name': row['LAST_NAME'],
                        'phone_number': row.get('PHONE_NUMBER'),
                        'salary': row.get('SALARY'),
                        'manager_id': row.get('MANAGER_ID'),
                        'department_id': row.get('DEPARTMENT_ID'),
                        'company_id': company_id
                    })
        
        if employee_mappings:
            db.session.bulk_insert_mappings(Employee, employee_mappings)
            db.session.commit()
        
        inserted_count = len(employee_mappings)
        skipped_count = len(incoming_employee_ids) - inserted_count
        message = f"File processed. Inserted {inserted_count} new employees. Skipped {skipped_count} existing employees."

        return jsonify({"message": message}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/companies', methods=['GET'])
def get_companies():
    """Returns a serialized list of all companies."""
    companies = Company.query.all()
    return jsonify([c.to_dict() for c in companies])

@api_bp.route('/employees', methods=['GET'])
def get_employees():
    """Returns a serialized list of all employees."""
    employees = Employee.query.all()
    return jsonify([e.to_dict() for e in employees])

from flask import Blueprint, request, jsonify
from models import db, Chemical

chemical_bp = Blueprint("chemical", __name__)

@chemical_bp.route('/add', methods=['POST'])
def add_chemical():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    # Required fields
    required_fields = ['nameCn', 'casNo']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400

    # Handle hazardClasses as a comma-separated string
    hazard_classes_str = ','.join(data.get('hazardClasses', []))

    new_chemical = Chemical(
        name_cn=data['nameCn'],
        name_en=data.get('nameEn'),
        cas_no=data['casNo'],
        molecular_formula=data.get('molecularFormula'),
        molecular_weight=data.get('molecularWeight'),
        aliases=data.get('aliases'),
        image_url=data.get('imageUrl'),
        specification=data.get('specification'),
        form_state=data.get('formState'),
        hazard_classes=hazard_classes_str,
        hazard_description=data.get('hazardDescription'),
        signal_word=data.get('signalWord'),
        hazard_statements=data.get('hazardStatements'),
        precautionary_statements=data.get('precautionaryStatements')
    )

    try:
        db.session.add(new_chemical)
        db.session.commit()
        return jsonify({'message': 'Chemical added successfully', 'chemical': new_chemical.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error adding chemical', 'error': str(e)}), 500

@chemical_bp.route('/list', methods=['GET'])
def list_chemicals():
    chemicals = Chemical.query.all()
    return jsonify([chemical.to_dict() for chemical in chemicals]), 200

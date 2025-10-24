from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="staff")  # admin/staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Chemical(db.Model):
    __tablename__ = 'chemicals'
    id = db.Column(db.Integer, primary_key=True)
    name_cn = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255), nullable=True)
    cas_no = db.Column(db.String(50), unique=True, nullable=False)
    molecular_formula = db.Column(db.String(100), nullable=True)
    molecular_weight = db.Column(db.String(100), nullable=True)
    aliases = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    specification = db.Column(db.String(255), nullable=True)
    form_state = db.Column(db.String(50), nullable=True)
    hazard_classes = db.Column(db.Text, nullable=True)
    hazard_description = db.Column(db.Text, nullable=True)
    signal_word = db.Column(db.String(50), nullable=True)
    hazard_statements = db.Column(db.Text, nullable=True)
    precautionary_statements = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Chemical {self.name_cn} ({self.cas_no})>'

    def to_dict(self):
        return {
            'id': self.id,
            'nameCn': self.name_cn,
            'nameEn': self.name_en,
            'casNo': self.cas_no,
            'molecularFormula': self.molecular_formula,
            'molecularWeight': self.molecular_weight,
            'aliases': self.aliases,
            'imageUrl': self.image_url,
            'specification': self.specification,
            'formState': self.form_state,
            'hazardClasses': self.hazard_classes.split(',') if self.hazard_classes else [],
            'hazardDescription': self.hazard_description,
            'signalWord': self.signal_word,
            'hazardStatements': self.hazard_statements,
            'precautionaryStatements': self.precautionary_statements,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }

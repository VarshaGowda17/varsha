from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    certificates = db.relationship('Certificate', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    student_name = db.Column(db.String(150), nullable=False)
    student_id_number = db.Column(db.String(50), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    degree_type = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(150), nullable=False)
    university_name = db.Column(db.String(200), nullable=False, default='Global University')
    graduation_date = db.Column(db.Date, nullable=False)
    grade = db.Column(db.String(20), nullable=True)
    honors = db.Column(db.String(100), nullable=True)
    
    certificate_hash = db.Column(db.String(256), nullable=False)
    blockchain_tx_hash = db.Column(db.String(256), nullable=True)
    block_number = db.Column(db.Integer, nullable=True)
    ipfs_hash = db.Column(db.String(256), nullable=True)
    
    qr_code_path = db.Column(db.String(500), nullable=True)
    certificate_file_path = db.Column(db.String(500), nullable=True)
    
    status = db.Column(db.String(20), default='active')
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    revoked_at = db.Column(db.DateTime, nullable=True)
    revocation_reason = db.Column(db.Text, nullable=True)
    
    issued_by = db.Column(db.String(100), nullable=True)
    
    def generate_certificate_id(self):
        unique_string = f"{self.student_id_number}{self.course_name}{datetime.utcnow().timestamp()}"
        self.certificate_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16].upper()
        return self.certificate_id
    
    def generate_hash(self):
        data = f"{self.student_name}{self.student_id_number}{self.course_name}{self.degree_type}{self.department}{self.graduation_date}{self.university_name}"
        self.certificate_hash = hashlib.sha256(data.encode()).hexdigest()
        return self.certificate_hash
    
    def is_valid(self):
        return self.status == 'active'
    
    def revoke(self, reason=""):
        self.status = 'revoked'
        self.revoked_at = datetime.utcnow()
        self.revocation_reason = reason
    
    def __repr__(self):
        return f'<Certificate {self.certificate_id}>'


class BlockchainTransaction(db.Model):
    __tablename__ = 'blockchain_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_hash = db.Column(db.String(256), unique=True, nullable=False)
    block_number = db.Column(db.Integer, nullable=False)
    certificate_id = db.Column(db.String(64), nullable=False)
    certificate_hash = db.Column(db.String(256), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    gas_used = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='confirmed')
    
    def __repr__(self):
        return f'<BlockchainTransaction {self.transaction_hash[:16]}...>'


class VerificationLog(db.Model):
    __tablename__ = 'verification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(64), nullable=False)
    verification_result = db.Column(db.Boolean, nullable=False)
    verification_method = db.Column(db.String(50), nullable=False)
    verifier_ip = db.Column(db.String(45), nullable=True)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VerificationLog {self.certificate_id}>'

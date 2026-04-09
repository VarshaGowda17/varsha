from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os
import json
import socket

from config import Config, get_local_ip
from models import db, User, Certificate, BlockchainTransaction, VerificationLog
from blockchain import blockchain
from ipfs_simulator import ipfs
from qr_generator import qr_generator
from certificate_generator import certificate_generator

app = Flask(__name__)
app.config.from_object(Config)
app.config['WTF_CSRF_ENABLED'] = True

csrf = CSRFProtect(app)

os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'), exist_ok=True)
os.makedirs(app.config.get('CERTIFICATE_FOLDER', 'static/certificates'), exist_ok=True)
os.makedirs(app.config.get('QR_CODE_FOLDER', 'static/qrcodes'), exist_ok=True)
os.makedirs('static/ipfs_storage', exist_ok=True)

# Load saved QR configuration if it exists
def load_qr_config():
    """Load QR configuration from file if it exists"""
    config_file = Config.QR_CONFIG_FILE
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                if 'SERVER_ADDRESS' in config_data and config_data['SERVER_ADDRESS']:
                    Config.SERVER_ADDRESS = config_data['SERVER_ADDRESS']
        except Exception as e:
            print(f"Error loading QR config: {e}")

load_qr_config()

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_base_url():
    return request.host_url.rstrip('/')

def get_public_url():
    """Get the public server URL for QR codes and certificate sharing"""
    return Config.get_public_url()

with app.app_context():
    db.create_all()
    
    # Rebuild blockchain registry from existing certificates
    existing_certificates = Certificate.query.all()
    for cert in existing_certificates:
        if cert.certificate_id not in blockchain.certificate_registry:
            blockchain.certificate_registry[cert.certificate_id] = {
                'hash': cert.certificate_hash,
                'block_number': cert.block_number if cert.block_number else 0,
                'block_hash': cert.blockchain_tx_hash if cert.blockchain_tx_hash else '',
                'status': cert.status,
                'issued_at': str(cert.issued_at)
            }
            if cert.status == 'revoked' and cert.revoked_at:
                blockchain.certificate_registry[cert.certificate_id]['revoked_at'] = str(cert.revoked_at)


@app.route('/')
def index():
    stats = {
        'total_certificates': Certificate.query.count(),
        'verified_today': VerificationLog.query.filter(
            VerificationLog.verified_at >= date.today()
        ).count(),
        'blockchain_blocks': len(blockchain.chain),
        'active_users': User.query.filter_by(is_admin=False).count()
    }
    return render_template('index.html', stats=stats)


@app.route('/setup', methods=['GET', 'POST'])
def setup_qr_config():
    """Setup page for configuring QR code server address"""
    local_ip = get_local_ip()
    current_server = Config.SERVER_ADDRESS or f'http://{local_ip}:5000'
    
    if request.method == 'POST':
        server_address = request.form.get('server_address', '').strip()
        
        if not server_address:
            flash('Server address cannot be empty.', 'danger')
            return render_template('setup_qr.html', local_ip=local_ip, current_server=current_server)
        
        # Validate URL format
        if not server_address.startswith(('http://', 'https://')):
            server_address = f'http://{server_address}'
        
        # Save to config
        Config.SERVER_ADDRESS = server_address
        
        # Also save to a persistent config file
        config_data = {
            'SERVER_ADDRESS': server_address,
            'saved_at': datetime.utcnow().isoformat()
        }
        
        try:
            config_file = Config.QR_CONFIG_FILE
            os.makedirs(os.path.dirname(config_file) if os.path.dirname(config_file) else '.', exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            flash(f'Server address updated to: {server_address}', 'success')
        except Exception as e:
            flash(f'Error saving configuration: {str(e)}', 'danger')
        
        return redirect(url_for('setup_qr_config'))
    
    return render_template('setup_qr.html', local_ip=local_ip, current_server=current_server)


@app.route('/api/qr-config', methods=['GET', 'POST'])
def api_qr_config():
    """API endpoint for managing QR code configuration"""
    if request.method == 'GET':
        local_ip = get_local_ip()
        return jsonify({
            'current_server': Config.SERVER_ADDRESS or f'http://{local_ip}:5000',
            'local_ip': local_ip,
            'configured': Config.SERVER_ADDRESS is not None
        })
    
    if request.method == 'POST':
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        server_address = data.get('server_address', '').strip()
        
        if not server_address:
            return jsonify({'success': False, 'message': 'Server address cannot be empty'}), 400
        
        if not server_address.startswith(('http://', 'https://')):
            server_address = f'http://{server_address}'
        
        Config.SERVER_ADDRESS = server_address
        
        config_data = {
            'SERVER_ADDRESS': server_address,
            'saved_at': datetime.utcnow().isoformat()
        }
        
        try:
            config_file = Config.QR_CONFIG_FILE
            os.makedirs(os.path.dirname(config_file) if os.path.dirname(config_file) else '.', exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            return jsonify({'success': True, 'message': 'Configuration updated', 'server_address': server_address})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error saving configuration: {str(e)}'}), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        department = request.form.get('department', '').strip()
        
        if not all([username, email, password, full_name]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            student_id=student_id if student_id else None,
            department=department if department else None,
            is_admin=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            admin_user = User.query.filter_by(username='admin', is_admin=True).first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@university.edu',
                    full_name='System Administrator',
                    is_admin=True
                )
                admin_user.set_password(Config.ADMIN_PASSWORD)
                db.session.add(admin_user)
                db.session.commit()
            
            login_user(admin_user)
            flash('Welcome, Administrator!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin_dashboard'))
            return redirect(next_page or url_for('dashboard'))
        
        flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    certificates = Certificate.query.filter_by(user_id=current_user.id).order_by(Certificate.issued_at.desc()).all()
    return render_template('dashboard.html', certificates=certificates)


@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    stats = {
        'total_certificates': Certificate.query.count(),
        'active_certificates': Certificate.query.filter_by(status='active').count(),
        'revoked_certificates': Certificate.query.filter_by(status='revoked').count(),
        'total_users': User.query.filter_by(is_admin=False).count(),
        'blockchain_blocks': len(blockchain.chain),
        'total_verifications': VerificationLog.query.count()
    }
    
    recent_certificates = Certificate.query.order_by(Certificate.issued_at.desc()).limit(10).all()
    recent_verifications = VerificationLog.query.order_by(VerificationLog.verified_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_certificates=recent_certificates,
                         recent_verifications=recent_verifications)


@app.route('/admin/issue-certificate', methods=['GET', 'POST'])
@login_required
def issue_certificate():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.filter_by(is_admin=False).all()
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        student_name = request.form.get('student_name', '').strip()
        student_id_number = request.form.get('student_id_number', '').strip()
        course_name = request.form.get('course_name', '').strip()
        degree_type = request.form.get('degree_type', '').strip()
        department = request.form.get('department', '').strip()
        university_name = request.form.get('university_name', 'Global University').strip()
        graduation_date_str = request.form.get('graduation_date', '')
        grade = request.form.get('grade', '').strip()
        
        if not all([user_id, student_name, student_id_number, course_name, degree_type, department, graduation_date_str]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/issue_certificate.html', users=users)
        
        try:
            graduation_date = datetime.strptime(graduation_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid graduation date format.', 'danger')
            return render_template('admin/issue_certificate.html', users=users)
        
        certificate = Certificate(
            user_id=int(user_id),
            student_name=student_name,
            student_id_number=student_id_number,
            course_name=course_name,
            degree_type=degree_type,
            department=department,
            university_name=university_name,
            graduation_date=graduation_date,
            grade=grade if grade else None,
            honors=None,
            issued_by=current_user.full_name
        )
        
        certificate.generate_certificate_id()
        certificate.generate_hash()
        
        blockchain_result = blockchain.add_certificate(
            certificate.certificate_id,
            certificate.certificate_hash,
            student_name,
            course_name,
            current_user.full_name
        )
        
        if blockchain_result['success']:
            certificate.blockchain_tx_hash = blockchain_result['transaction_hash']
            certificate.block_number = blockchain_result['block_number']
            
            tx = BlockchainTransaction(
                transaction_hash=blockchain_result['transaction_hash'],
                block_number=blockchain_result['block_number'],
                certificate_id=certificate.certificate_id,
                certificate_hash=certificate.certificate_hash,
                action='ISSUED',
                gas_used=blockchain_result.get('gas_used', 0)
            )
            db.session.add(tx)
        
        # Use public URL for QR codes to ensure they work on any device
        verification_url = f"{get_public_url()}/verify/{certificate.certificate_id}"
        qr_path = qr_generator.generate_certificate_qr(
            certificate.certificate_id,
            verification_url,
            certificate.certificate_hash
        )
        certificate.qr_code_path = qr_path
        
        cert_image_path = certificate_generator.generate_certificate_image({
            'certificate_id': certificate.certificate_id,
            'student_name': student_name,
            'course_name': course_name,
            'degree_type': degree_type,
            'department': department,
            'university_name': university_name,
            'graduation_date': graduation_date,
            'grade': grade
        }, qr_path)
        certificate.certificate_file_path = cert_image_path
        
        ipfs_cid = ipfs.add_json({
            'certificate_id': certificate.certificate_id,
            'student_name': student_name,
            'student_id': student_id_number,
            'course_name': course_name,
            'degree_type': degree_type,
            'department': department,
            'university_name': university_name,
            'graduation_date': str(graduation_date),
            'grade': grade,
            'certificate_hash': certificate.certificate_hash,
            'blockchain_tx': certificate.blockchain_tx_hash,
            'issued_at': str(datetime.utcnow())
        })
        certificate.ipfs_hash = ipfs_cid
        
        db.session.add(certificate)
        db.session.commit()
        
        flash(f'Certificate issued successfully! Certificate ID: {certificate.certificate_id}', 'success')
        return redirect(url_for('view_certificate', certificate_id=certificate.certificate_id))
    
    return render_template('admin/issue_certificate.html', users=users)


@app.route('/admin/certificates')
@login_required
def admin_certificates():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    certificates = Certificate.query.order_by(Certificate.issued_at.desc()).all()
    return render_template('admin/certificates.html', certificates=certificates)


@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/blockchain')
@login_required
def admin_blockchain():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    chain_info = blockchain.get_chain_info()
    blocks = blockchain.get_all_blocks()
    
    return render_template('admin/blockchain.html', chain_info=chain_info, blocks=blocks)


@app.route('/admin/revoke/<certificate_id>', methods=['POST'])
@login_required
def revoke_certificate(certificate_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
    if not certificate:
        return jsonify({'success': False, 'message': 'Certificate not found'}), 404
    
    reason = request.form.get('reason', 'Revoked by administrator')
    
    blockchain_result = blockchain.revoke_certificate(certificate_id, reason)
    
    if blockchain_result['success']:
        certificate.revoke(reason)
        
        tx = BlockchainTransaction(
            transaction_hash=blockchain_result['transaction_hash'],
            block_number=blockchain_result['block_number'],
            certificate_id=certificate_id,
            certificate_hash=certificate.certificate_hash,
            action='REVOKED'
        )
        db.session.add(tx)
        db.session.commit()
        
        flash('Certificate revoked successfully.', 'success')
        return redirect(url_for('admin_certificates'))
    
    flash('Failed to revoke certificate.', 'danger')
    return redirect(url_for('admin_certificates'))


@app.route('/certificate/<certificate_id>')
@login_required
def view_certificate(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    
    if not current_user.is_admin and certificate.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    blockchain_info = blockchain.verify_certificate(certificate_id, certificate.certificate_hash)
    
    return render_template('certificate_view.html', 
                         certificate=certificate, 
                         blockchain_info=blockchain_info,
                         base_url=get_base_url())


@app.route('/verify/<certificate_id>')
def verify_certificate_public(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
    
    if not certificate:
        verification_result = {
            'valid': False,
            'status': 'NOT_FOUND',
            'message': 'Certificate not found in our records'
        }
        
        log = VerificationLog(
            certificate_id=certificate_id,
            verification_result=False,
            verification_method='web',
            verifier_ip=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return render_template('verify.html', 
                             certificate=None, 
                             result=verification_result,
                             certificate_id=certificate_id)
    
    blockchain_result = blockchain.verify_certificate(certificate_id, certificate.certificate_hash)
    
    log = VerificationLog(
        certificate_id=certificate_id,
        verification_result=blockchain_result['valid'],
        verification_method='web',
        verifier_ip=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return render_template('verify.html', 
                         certificate=certificate, 
                         result=blockchain_result,
                         certificate_id=certificate_id)


@app.route('/verify', methods=['GET', 'POST'])
def verify_page():
    if request.method == 'POST':
        certificate_id = request.form.get('certificate_id', '').strip().upper()
        if certificate_id:
            return redirect(url_for('verify_certificate_public', certificate_id=certificate_id))
        flash('Please enter a certificate ID.', 'warning')
    
    return render_template('verify_form.html')


@app.route('/scan')
def scan_qr():
    return render_template('scan.html')


@app.route('/api/verify/<certificate_id>')
def api_verify(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id.upper()).first()
    
    if not certificate:
        return jsonify({
            'valid': False,
            'status': 'NOT_FOUND',
            'message': 'Certificate not found',
            'certificate_id': certificate_id
        })
    
    blockchain_result = blockchain.verify_certificate(certificate_id, certificate.certificate_hash)
    
    log = VerificationLog(
        certificate_id=certificate_id,
        verification_result=blockchain_result['valid'],
        verification_method='api',
        verifier_ip=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    response = {
        'valid': blockchain_result['valid'],
        'status': blockchain_result['status'],
        'message': blockchain_result['message'],
        'certificate_id': certificate_id,
        'blockchain_verified': blockchain_result.get('blockchain_verified', False)
    }
    
    if blockchain_result['valid']:
        response.update({
            'student_name': certificate.student_name,
            'course_name': certificate.course_name,
            'degree_type': certificate.degree_type,
            'university_name': certificate.university_name,
            'graduation_date': str(certificate.graduation_date),
            'block_number': blockchain_result.get('block_number'),
            'issued_at': blockchain_result.get('issued_at')
        })
    
    return jsonify(response)


@app.route('/api/blockchain/info')
def api_blockchain_info():
    return jsonify(blockchain.get_chain_info())


@app.route('/download/certificate/<certificate_id>')
@login_required
def download_certificate(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)
    
    if certificate.certificate_file_path and os.path.exists(certificate.certificate_file_path):
        return send_file(
            certificate.certificate_file_path,
            as_attachment=True,
            download_name=f'certificate_{certificate_id}.png'
        )
    
    abort(404)


@app.route('/download/qr/<certificate_id>')
@login_required
def download_qr(certificate_id):
    certificate = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)
    
    if certificate.qr_code_path and os.path.exists(certificate.qr_code_path):
        return send_file(
            certificate.qr_code_path,
            as_attachment=True,
            download_name=f'qr_code_{certificate_id}.png'
        )
    
    abort(404)


@app.route('/ipfs/<cid>')
def serve_ipfs(cid):
    file_path, error = ipfs.get_file(cid)
    if error:
        abort(404)
    
    file_info = ipfs.get_file_info(cid)
    return send_file(file_path, mimetype=file_info.get('content_type', 'application/octet-stream'))


@app.route('/features')
def features():
    return render_template('features.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@app.context_processor
def utility_processor():
    return {
        'now': datetime.utcnow(),
        'app_name': 'CertChain',
        'university_name': 'Global University'
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

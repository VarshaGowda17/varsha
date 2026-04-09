import os
import socket

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket connection to get the machine's IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'blockchain-cert-secret-key-2024'
    
    USE_MYSQL = os.environ.get('USE_MYSQL', 'false').lower() == 'true'
    
    if USE_MYSQL:
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
        MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'blockchain_certs')
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///blockchain_certs.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = 'static/uploads'
    CERTIFICATE_FOLDER = 'static/certificates'
    QR_CODE_FOLDER = 'static/qrcodes'
    QR_CONFIG_FILE = 'qr_config.json'
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin'
    
    BLOCKCHAIN_NETWORK = 'local'
    GANACHE_URL = os.environ.get('GANACHE_URL', 'http://127.0.0.1:8545')
    
    # Server address for public access (used for QR codes and sharing)
    # Can be set via environment variable or configured via admin panel
    # Format: http://domain.com or http://192.168.1.100:5000
    SERVER_ADDRESS = os.environ.get('SERVER_ADDRESS', None)
    
    @staticmethod
    def get_public_url():
        """Get the public server URL for certificates and QR codes"""
        if Config.SERVER_ADDRESS:
            return Config.SERVER_ADDRESS.rstrip('/')
        else:
            # Fallback to local IP for network access
            local_ip = get_local_ip()
            return f'http://{local_ip}:5000'

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from PIL import Image, ImageDraw, ImageFont
import os
import io
import base64


class QRCodeGenerator:
    def __init__(self, output_folder='static/qrcodes'):
        self.output_folder = output_folder
        self._ensure_folder_exists()
    
    def _ensure_folder_exists(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def generate_verification_url(self, certificate_id, base_url):
        return f"{base_url}/verify/{certificate_id}"
    
    def generate_qr_code(self, data, filename, style='default'):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        if style == 'rounded':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer()
            )
        elif style == 'gradient':
            img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=RadialGradiantColorMask(
                    back_color=(255, 255, 255),
                    center_color=(0, 50, 100),
                    edge_color=(0, 100, 180)
                )
            )
        else:
            img = qr.make_image(fill_color="#1a365d", back_color="white")
        
        img = img.convert('RGB')
        
        file_path = os.path.join(self.output_folder, filename)
        img.save(file_path, 'PNG')
        
        return file_path
    
    def generate_certificate_qr(self, certificate_id, verification_url, certificate_hash=None):
        qr_data = {
            'url': verification_url,
            'cert_id': certificate_id
        }
        
        if certificate_hash:
            qr_data['hash'] = certificate_hash[:16]
        
        data_string = verification_url
        
        filename = f"cert_qr_{certificate_id}.png"
        
        qr_path = self.generate_qr_code(data_string, filename, style='rounded')
        
        self._add_label_to_qr(qr_path, certificate_id)
        
        return qr_path
    
    def _add_label_to_qr(self, qr_path, certificate_id):
        img = Image.open(qr_path)
        
        new_height = img.height + 40
        new_img = Image.new('RGB', (img.width, new_height), 'white')
        new_img.paste(img, (0, 0))
        
        draw = ImageDraw.Draw(new_img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        text = f"ID: {certificate_id}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (new_img.width - text_width) // 2
        y = img.height + 10
        
        draw.text((x, y), text, fill='#1a365d', font=font)
        
        new_img.save(qr_path, 'PNG')
    
    def qr_to_base64(self, qr_path):
        with open(qr_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def generate_qr_base64(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#1a365d", back_color="white")
        img = img.convert('RGB')
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')


qr_generator = QRCodeGenerator()

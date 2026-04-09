from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import hashlib


class CertificateGenerator:
    def __init__(self, output_folder='static/certificates'):
        self.output_folder = output_folder
        self._ensure_folder_exists()
        self.width = 1400
        self.height = 1000
    
    def _ensure_folder_exists(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def _get_font(self, size, bold=False):
        try:
            if bold:
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default()
    
    def _draw_centered_text(self, draw, y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, y), text, font=font, fill=fill)
    
    def _draw_decorative_border(self, draw):
        gold = '#B8860B'
        dark_blue = '#1a365d'
        
        draw.rectangle([15, 15, self.width - 15, self.height - 15], outline=dark_blue, width=4)
        draw.rectangle([25, 25, self.width - 25, self.height - 25], outline=gold, width=2)
        draw.rectangle([35, 35, self.width - 35, self.height - 35], outline=dark_blue, width=1)
        
        corner_size = 50
        corners = [
            (25, 25),
            (self.width - 25 - corner_size, 25),
            (25, self.height - 25 - corner_size),
            (self.width - 25 - corner_size, self.height - 25 - corner_size)
        ]
        for cx, cy in corners:
            for i in range(3):
                offset = i * 8
                draw.arc([cx + offset, cy + offset, cx + corner_size - offset, cy + corner_size - offset], 
                        0, 90, fill=gold, width=2)
    
    def _draw_ribbon(self, draw, x, y, color):
        ribbon_width = 80
        ribbon_height = 100
        draw.polygon([
            (x, y),
            (x + ribbon_width, y),
            (x + ribbon_width, y + ribbon_height),
            (x + ribbon_width // 2, y + ribbon_height - 20),
            (x, y + ribbon_height)
        ], fill=color)
    
    def generate_certificate_image(self, certificate_data, qr_image_path=None):
        img = Image.new('RGB', (self.width, self.height), '#FFFEF7')
        draw = ImageDraw.Draw(img)
        
        self._draw_decorative_border(draw)
        
        title_font = self._get_font(48, bold=True)
        subtitle_font = self._get_font(32, bold=True)
        name_font = self._get_font(44, bold=True)
        text_font = self._get_font(22)
        small_font = self._get_font(16)
        
        dark_blue = '#1a365d'
        gold = '#B8860B'
        text_gray = '#4a5568'
        
        university_name = certificate_data.get('university_name', 'Global University')
        self._draw_centered_text(draw, 80, university_name.upper(), title_font, dark_blue)
        
        draw.line([(300, 145), (self.width - 300, 145)], fill=gold, width=2)
        
        self._draw_centered_text(draw, 180, "CERTIFICATE", self._get_font(56, bold=True), dark_blue)
        self._draw_centered_text(draw, 250, "OF ACHIEVEMENT", subtitle_font, gold)
        
        draw.line([(400, 310), (self.width - 400, 310)], fill=gold, width=1)
        
        self._draw_centered_text(draw, 350, "This is to certify that", text_font, text_gray)
        
        student_name = certificate_data.get('student_name', 'Student Name')
        self._draw_centered_text(draw, 420, student_name, name_font, dark_blue)
        
        name_width = draw.textbbox((0, 0), student_name, font=name_font)[2]
        line_x_start = (self.width - name_width) // 2 - 30
        line_x_end = (self.width + name_width) // 2 + 30
        draw.line([(line_x_start, 480), (line_x_end, 480)], fill=gold, width=2)
        
        self._draw_centered_text(draw, 520, "has successfully completed the requirements for the degree of", text_font, text_gray)
        
        degree = certificate_data.get('degree_type', 'Bachelor of Science')
        course = certificate_data.get('course_name', 'Computer Science')
        self._draw_centered_text(draw, 580, f"{degree}", subtitle_font, dark_blue)
        self._draw_centered_text(draw, 630, f"in {course}", text_font, text_gray)
        
        department = certificate_data.get('department', 'Department of Computer Science')
        self._draw_centered_text(draw, 680, f"from {department}", text_font, text_gray)
        
        if certificate_data.get('grade'):
            grade_text = f"with {certificate_data.get('grade', '')}"
            self._draw_centered_text(draw, 730, grade_text, text_font, gold)
        
        grad_date = certificate_data.get('graduation_date', datetime.now().strftime('%B %d, %Y'))
        if hasattr(grad_date, 'strftime'):
            grad_date = grad_date.strftime('%B %d, %Y')
        self._draw_centered_text(draw, 780, f"Conferred on {grad_date}", text_font, text_gray)
        
        sig_y = 860
        draw.line([(150, sig_y), (400, sig_y)], fill=dark_blue, width=1)
        draw.line([(self.width - 400, sig_y), (self.width - 150, sig_y)], fill=dark_blue, width=1)
        
        registrar_text = "University Registrar"
        bbox = draw.textbbox((0, 0), registrar_text, font=small_font)
        text_width = bbox[2] - bbox[0]
        draw.text(((150 + 400 - text_width) // 2, sig_y + 10), registrar_text, font=small_font, fill=text_gray)
        
        dean_text = "Dean of Faculty"
        bbox = draw.textbbox((0, 0), dean_text, font=small_font)
        text_width = bbox[2] - bbox[0]
        draw.text((self.width - 400 + (250 - text_width) // 2, sig_y + 10), dean_text, font=small_font, fill=text_gray)
        
        seal_x = self.width // 2
        seal_y = sig_y - 20
        seal_radius = 45
        draw.ellipse([seal_x - seal_radius, seal_y - seal_radius, seal_x + seal_radius, seal_y + seal_radius], 
                    outline=gold, width=3)
        draw.ellipse([seal_x - seal_radius + 8, seal_y - seal_radius + 8, 
                     seal_x + seal_radius - 8, seal_y + seal_radius - 8], 
                    outline=gold, width=1)
        seal_font = self._get_font(12, bold=True)
        self._draw_centered_text(draw, seal_y - 8, "OFFICIAL", seal_font, gold)
        self._draw_centered_text(draw, seal_y + 6, "SEAL", seal_font, gold)
        
        if qr_image_path and os.path.exists(qr_image_path):
            qr_img = Image.open(qr_image_path)
            qr_size = 90
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            qr_position = (self.width - qr_size - 55, self.height - qr_size - 55)
            
            border = 5
            qr_bg = Image.new('RGB', (qr_size + border * 2, qr_size + border * 2), '#FFFFFF')
            img.paste(qr_bg, (qr_position[0] - border, qr_position[1] - border))
            img.paste(qr_img, qr_position)
        
        cert_id = certificate_data.get('certificate_id', 'N/A')
        id_font = self._get_font(14)
        id_text = f"Certificate ID: {cert_id}"
        draw.text((55, self.height - 50), id_text, font=id_font, fill=text_gray)
        
        verified_font = self._get_font(12, bold=True)
        verified_text = "Blockchain Verified"
        draw.text((55, self.height - 30), verified_text, font=verified_font, fill='#38a169')
        
        filename = f"certificate_{cert_id}.png"
        file_path = os.path.join(self.output_folder, filename)
        img.save(file_path, 'PNG', quality=95)
        
        return file_path


certificate_generator = CertificateGenerator()

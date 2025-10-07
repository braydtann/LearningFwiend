"""
Certificate PDF Generation Module
=================================

Generates professional PDF certificates using the provided template and ReportLab.
"""

import io
import os
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, darkblue, gold
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

logger = logging.getLogger(__name__)

class CertificateGenerator:
    """Professional PDF Certificate Generator"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.template_url = "https://customer-assets.emergentagent.com/job_quiz-progress-fix/artifacts/cwq2pzta_blank_certificate_templates_Certifier_blog_5_2b8da760be.png"
        self.template_path = Path("/app/backend/certificate_template.png")
        
    def download_template(self) -> bool:
        """Download the certificate template if not exists."""
        try:
            if self.template_path.exists():
                logger.info("Certificate template already exists")
                return True
                
            logger.info("Downloading certificate template...")
            response = requests.get(self.template_url, timeout=30)
            response.raise_for_status()
            
            with open(self.template_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Certificate template downloaded to {self.template_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download certificate template: {str(e)}")
            return False
    
    def generate_certificate_pdf(
        self,
        certificate_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate a professional PDF certificate.
        
        Args:
            certificate_data: Dictionary containing certificate information
            output_path: Optional path to save the PDF file
        
        Returns:
            bytes: PDF content as bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create canvas
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Download template if needed
            if not self.download_template():
                # Fallback to generating without template
                return self._generate_fallback_certificate(certificate_data, buffer)
            
            # Add template background
            try:
                # Load and resize template to fit A4
                img = Image.open(self.template_path)
                img_width, img_height = img.size
                
                # Calculate scaling to fit A4 page
                scale_x = width / img_width
                scale_y = height / img_height
                scale = min(scale_x, scale_y)
                
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Center the image
                x_offset = (width - new_width) / 2
                y_offset = (height - new_height) / 2
                
                c.drawImage(
                    self.template_path,
                    x_offset, y_offset,
                    width=new_width,
                    height=new_height,
                    preserveAspectRatio=True
                )
                
            except Exception as e:
                logger.warning(f"Failed to load template image: {str(e)}, using fallback")
                return self._generate_fallback_certificate(certificate_data, buffer)
            
            # Add certificate text content
            self._add_certificate_content(c, certificate_data, width, height)
            
            # Finalize PDF
            c.save()
            buffer.seek(0)
            
            # Optionally save to file
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
                logger.info(f"Certificate saved to {output_path}")
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to generate certificate PDF: {str(e)}")
            # Return fallback certificate
            return self._generate_fallback_certificate(certificate_data, io.BytesIO())
    
    def _add_certificate_content(self, canvas_obj, cert_data: Dict[str, Any], width: float, height: float):
        """Add text content to the certificate."""
        try:
            # Certificate title
            canvas_obj.setFont("Helvetica-Bold", 32)
            canvas_obj.setFillColor(darkblue)
            
            title = "CERTIFICATE OF COMPLETION"
            if cert_data.get("type") == "program_completion":
                title = "PROGRAM COMPLETION CERTIFICATE"
            
            title_width = canvas_obj.stringWidth(title, "Helvetica-Bold", 32)
            canvas_obj.drawString((width - title_width) / 2, height - 180, title)
            
            # Student name
            canvas_obj.setFont("Helvetica-Bold", 24)
            canvas_obj.setFillColor(black)
            student_name = cert_data.get("studentName", "Unknown Student")
            name_width = canvas_obj.stringWidth(student_name, "Helvetica-Bold", 24)
            canvas_obj.drawString((width - name_width) / 2, height - 280, student_name)
            
            # Course/Program name
            canvas_obj.setFont("Helvetica", 18)
            course_program = cert_data.get("courseName") or cert_data.get("programName", "Unknown Course/Program")
            
            # Wrap long course/program names
            max_width = width - 100
            if canvas_obj.stringWidth(course_program, "Helvetica", 18) > max_width:
                # Simple word wrapping
                words = course_program.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if canvas_obj.stringWidth(test_line, "Helvetica", 18) <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # Draw multiple lines
                for i, line in enumerate(lines):
                    line_width = canvas_obj.stringWidth(line, "Helvetica", 18)
                    canvas_obj.drawString((width - line_width) / 2, height - 380 - (i * 25), line)
            else:
                # Single line
                course_width = canvas_obj.stringWidth(course_program, "Helvetica", 18)
                canvas_obj.drawString((width - course_width) / 2, height - 380, course_program)
            
            # Completion date
            canvas_obj.setFont("Helvetica", 14)
            completion_date = cert_data.get("completionDate", datetime.utcnow())
            if isinstance(completion_date, str):
                date_str = completion_date[:10]  # Extract date part
            else:
                date_str = completion_date.strftime("%B %d, %Y")
            
            date_text = f"Completed on {date_str}"
            date_width = canvas_obj.stringWidth(date_text, "Helvetica", 14)
            canvas_obj.drawString((width - date_width) / 2, height - 450, date_text)
            
            # Grade and score
            if cert_data.get("grade") and cert_data.get("score"):
                grade_text = f"Grade: {cert_data['grade']} ({cert_data['score']:.1f}%)"
                grade_width = canvas_obj.stringWidth(grade_text, "Helvetica", 12)
                canvas_obj.drawString((width - grade_width) / 2, height - 480, grade_text)
            
            # Certificate number
            cert_number = cert_data.get("certificateNumber", "Unknown")
            canvas_obj.setFont("Helvetica", 10)
            canvas_obj.setFillColor(Color(0.5, 0.5, 0.5))
            canvas_obj.drawString(50, 50, f"Certificate No: {cert_number}")
            
            # Verification code
            verification_code = cert_data.get("verificationCode", "")
            if verification_code:
                canvas_obj.drawString(50, 30, f"Verification Code: {verification_code}")
            
            # Issue date
            issue_date = cert_data.get("issueDate", datetime.utcnow())
            if isinstance(issue_date, str):
                issue_str = issue_date[:10]
            else:
                issue_str = issue_date.strftime("%Y-%m-%d")
            
            canvas_obj.drawRightString(width - 50, 50, f"Issued: {issue_str}")
            
        except Exception as e:
            logger.error(f"Error adding certificate content: {str(e)}")
    
    def _generate_fallback_certificate(self, cert_data: Dict[str, Any], buffer: io.BytesIO) -> bytes:
        """Generate a fallback certificate without template."""
        try:
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Draw border
            c.setStrokeColor(darkblue)
            c.setLineWidth(3)
            c.rect(50, 50, width - 100, height - 100)
            
            # Inner decorative border
            c.setStrokeColor(gold)
            c.setLineWidth(1)
            c.rect(70, 70, width - 140, height - 140)
            
            # Add content
            self._add_certificate_content(c, cert_data, width, height)
            
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to generate fallback certificate: {str(e)}")
            return b"Certificate generation failed"

# Global instance
certificate_generator = CertificateGenerator()

def generate_certificate_pdf(certificate_data: Dict[str, Any]) -> bytes:
    """
    Generate a PDF certificate from certificate data.
    
    Args:
        certificate_data: Dictionary containing certificate information
    
    Returns:
        bytes: PDF content as bytes
    """
    return certificate_generator.generate_certificate_pdf(certificate_data)
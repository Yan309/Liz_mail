epl"""Email sending functionality with SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """Handle email sending via SMTP."""
    
    def __init__(self):
        """Initialize email sender with SMTP configuration."""
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_password = Config.SMTP_PASSWORD
        self.max_retries = Config.MAX_RETRIES
    
    def create_email(self, to_email: str, subject: str, body: str, 
                     from_name: Optional[str] = None) -> MIMEMultipart:
        """
        Create an email message.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML supported)
            from_name: Optional sender name
        
        Returns:
            MIMEMultipart message object
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['To'] = to_email
        
        if from_name:
            msg['From'] = f"{from_name} <{self.smtp_user}>"
        else:
            msg['From'] = self.smtp_user
        
        # Support both plain text and HTML
        if '<html>' in body.lower() or '<body>' in body.lower():
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        return msg
    
    def send_email(self, email_data: Dict[str, Any]) -> bool:
        """
        Send an email via SMTP with retry logic.
        
        Args:
            email_data: Dictionary containing:
                - to: recipient email
                - subject: email subject
                - body: email body
                - from_name: (optional) sender name
        
        Returns:
            True if email sent successfully, False otherwise
        """
        to_email = email_data.get('to')
        subject = email_data.get('subject')
        body = email_data.get('body')
        from_name = email_data.get('from_name')
        
        if not all([to_email, subject, body]):
            logger.error("Missing required email fields")
            return False
        
        # Retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                # Create message
                msg = self.create_email(to_email, subject, body, from_name)
                
                # Connect to SMTP server with timeout
                # Use SMTP_SSL for port 465, SMTP with starttls for port 587
                if self.smtp_port == 465:
                    # SSL connection
                    with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10) as server:
                        server.login(self.smtp_user, self.smtp_password)
                        server.send_message(msg)
                else:
                    # TLS connection (port 587 or 25)
                    with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                        server.starttls()
                        server.login(self.smtp_user, self.smtp_password)
                        server.send_message(msg)
                
                logger.info(f"Email sent successfully to {to_email}")
                return True
                
            except smtplib.SMTPException as e:
                logger.warning(f"SMTP error on attempt {attempt}/{self.max_retries} for {to_email}: {e}")
                if attempt == self.max_retries:
                    logger.error(f"Failed to send email to {to_email} after {self.max_retries} attempts")
                    return False
            except TimeoutError as e:
                logger.error(f"Connection timeout for {to_email}: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error sending email to {to_email}: {e}")
                return False
        
        return False
    
    def test_connection(self) -> bool:
        """Test SMTP connection and credentials."""
        try:
            # Use SMTP_SSL for port 465, SMTP with starttls for port 587
            if self.smtp_port == 465:
                # SSL connection
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.login(self.smtp_user, self.smtp_password)
            else:
                # TLS connection (port 587 or 25)
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
            
            logger.info("SMTP connection test successful")
            return True
        except TimeoutError as e:
            logger.error(f"Connection timeout: {e}")
            return False
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"Connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False


class EmailTemplates:
    """Pre-defined email templates."""
    
    @staticmethod
    def screening_email(candidate_name: str, position: str, company_name: str, 
                       hr_name: str, questions: list = None, 
                       additional_info: str = "") -> Dict[str, str]:
        """
        Generate a screening email template.
        
        Args:
            candidate_name: Name of the candidate
            position: Job position
            company_name: Company name
            hr_name: HR representative name
            questions: List of questions to ask
            additional_info: Additional custom information
        
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        questions_html = ""
        if questions:
            questions_html = "<ol>"
            for q in questions:
                questions_html += f"<li>{q}</li>"
            questions_html += "</ol>"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Dear {candidate_name},</p>
            
            <p>Thank you for your interest in the <strong>{position}</strong> position at {company_name}. 
            We have reviewed your CV and are impressed with your qualifications.</p>
            
            <p>We would like to move forward with your application and learn more about your experience. 
            Please take a moment to answer the following questions:</p>
            
            {questions_html}
            
            {f"<p>{additional_info}</p>" if additional_info else ""}
            
            <p>Please reply to this email with your responses at your earliest convenience.</p>
            
            <p>We look forward to hearing from you!</p>
            
            <p>Best regards,<br>
            {hr_name}<br>
            {company_name}</p>
        </body>
        </html>
        """
        
        return {
            'subject': f"Application for {position} - Next Steps",
            'body': body
        }
    
    @staticmethod
    def rejection_email(candidate_name: str, position: str, company_name: str,
                       hr_name: str, additional_message: str = "") -> Dict[str, str]:
        """
        Generate a rejection email template.
        
        Args:
            candidate_name: Name of the candidate
            position: Job position
            company_name: Company name
            hr_name: HR representative name
            additional_message: Additional custom message
        
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Dear {candidate_name},</p>
            
            <p>Thank you for taking the time to apply for the <strong>{position}</strong> position at {company_name} 
            and for sharing your CV with us.</p>
            
            <p>After careful consideration, we regret to inform you that we will not be moving forward with 
            your application at this time. We received many qualified applications, and the selection process 
            was highly competitive.</p>
            
            {f"<p>{additional_message}</p>" if additional_message else ""}
            
            <p>We appreciate your interest in {company_name} and encourage you to apply for future opportunities 
            that match your skills and experience.</p>
            
            <p>We wish you all the best in your job search and future career endeavors.</p>
            
            <p>Best regards,<br>
            {hr_name}<br>
            {company_name}</p>
        </body>
        </html>
        """
        
        return {
            'subject': f"Application Update - {position} Position",
            'body': body
        }
    
    @staticmethod
    def custom_email(subject: str, body: str, variables: Dict[str, str] = None) -> Dict[str, str]:
        """
        Generate a custom email with variable substitution.
        
        Args:
            subject: Email subject (can contain {variable} placeholders)
            body: Email body (can contain {variable} placeholders)
            variables: Dictionary of variables to substitute
        
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        if variables:
            try:
                subject = subject.format(**variables)
                body = body.format(**variables)
            except KeyError as e:
                logger.warning(f"Variable {e} not found in template")
        
        return {
            'subject': subject,
            'body': body
        }

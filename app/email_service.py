import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email_notification(subject, message, recipient=None):
    """
    Sends an email notification using credentials from the app's configuration.
    """
    try:
        # If no specific recipient is provided, it defaults to sending to you (the admin)
        if recipient is None:
            recipient = current_app.config['ADMIN_EMAIL']
        
        # Create the email message structure
        msg = MIMEMultipart()
        msg['From'] = current_app.config['ADMIN_EMAIL']
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Attach the message content
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to the SMTP server (e.g., Gmail)
        server = smtplib.SMTP(current_app.config['SMTP_SERVER'], current_app.config['SMTP_PORT'])
        server.starttls() # Secure the connection
        # Log in using the credentials from your .env file
        server.login(current_app.config['ADMIN_EMAIL'], current_app.config['EMAIL_PASSWORD'])
        # Send the email
        server.sendmail(current_app.config['ADMIN_EMAIL'], recipient, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        # --- CORRECTED: Use the app logger instead of print for better error handling ---
        current_app.logger.error(f"Error sending email: {e}")
        return False
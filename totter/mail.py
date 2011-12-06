import smtplib
from email.mime.text import MIMEText
def send_email(from_name, to_emails, subject, message):
    if not isinstance(to_emails, list):
        to_emails = [to_emails]
    msg = MIMEText(message.encode('utf-8'), 'plain', 'utf-8') 
    msg['Subject'] = subject
    msg['From'] = from_name
    msg['To'] = ','.join(to_emails)
    
    s = smtplib.SMTP('localhost')
    s.sendmail(from_name, to_emails, msg.as_string())
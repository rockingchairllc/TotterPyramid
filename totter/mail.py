import smtplib
from email.mime.text import MIMEText
def send_invite_email(from_name, to_emails, message):
    return
    if not isinstance(to_emails, list):
        to_emails = [to_emails]
    msg = MIMEText(fp.read())
    msg['Subject'] = "You've been invited!"
    msg['From'] = from_name
    msg['To'] = ','.join(to_emails)
    
    s = smtplib.SMTP('localhost')
    s.sendmail(from_name, to_emails, msg.as_string
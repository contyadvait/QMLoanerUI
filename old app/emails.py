import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import secret


def send_email(subject, body, to_emails, attachment_path, attach=True):
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587
    sender_email = secret.EMAIL_ID
    sender_password = secret.EMAIL_PASSWORD

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attach:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'pdf')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                        f'attachment; filename="{attachment_path}"')
            msg.attach(part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_emails, text)
        server.quit()

        print(f"Email sent to your email and the teachers' emails.")

    except smtplib.SMTPAuthenticationError as e:
        print(f'Authentication error: {e}')
    except Exception as e:
        print(f'An error occurred: {e}')

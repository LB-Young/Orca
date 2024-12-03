import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, sender_password, receiver_email, subject, body):
    # Create a MIMEMultipart object
    print(sender_email, sender_password, receiver_email, subject, body)
    print("send success")
    return
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Create a secure connection with the server and send the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Secure the connection
    server.login(sender_email, sender_password)  # Login to your email account
    server.sendmail(sender_email, receiver_email, msg.as_string())  # Send email
    server.quit()

    print("Email sent successfully!")


if __name__ == "__main__":
    # Example usage:
    sender = "lby15356@gmail.com"
    password = "seulby356.."  # Make sure to handle passwords securely, e.g., using environment variables
    receiver = "Young.liu@aishu.cn"
    subject = "Test Email"
    body = "This is a test email sent from Python!"

    send_email(sender_email=sender, sender_password=password, receiver_email=receiver, subject=subject, body=body)

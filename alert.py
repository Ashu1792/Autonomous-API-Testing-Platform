import smtplib
from email.mime.text import MIMEText

EMAIL = "Ashupal1507@gmail.com"
PASSWORD = "cpsj avhl nzbd jnpy"
TO_EMAIL = "ashupal112200@gmail.com"

def send_alert(api, status):

    subject = "⚠ API Failure Alert"

    body = f"""
    API Monitoring Alert

    API: {api}
    Status Code: {status}

    The API is not responding correctly.
    """

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com",465)
        server.login(EMAIL,PASSWORD)
        server.send_message(msg)
        server.quit()

        print("Alert email sent")

    except Exception as e:
        print("Email alert failed:",e)
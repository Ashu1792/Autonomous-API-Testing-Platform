import smtplib
from email.mime.text import MIMEText

EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"

def send_alert(api_url, status):

    message = f"API FAILURE ALERT\n\nAPI: {api_url}\nStatus Code: {status}"

    msg = MIMEText(message)

    msg["Subject"] = "API Monitoring Alert"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    try:

        server = smtplib.SMTP("smtp.gmail.com",587)

        server.starttls()

        server.login(EMAIL,PASSWORD)

        server.send_message(msg)

        server.quit()

        print("Alert email sent")

    except Exception as e:

        print("Email error:",e)
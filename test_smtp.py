import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
PORT = int(os.getenv('EMAIL_PORT', '587'))
USER = os.getenv('EMAIL_HOST_USER')
PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
RECIPIENT = os.getenv('TEST_SMTP_RECIPIENT', 'your@email.example')

if not USER or not PASSWORD:
	print('ERROR: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set in environment.')
	print('Set them in your .env or environment and retry. Example:')
	print('  EMAIL_HOST_USER=fitzone.alerts@gmail.com')
	print('  EMAIL_HOST_PASSWORD=<your_app_password>')
	raise SystemExit(1)

try:
	s = smtplib.SMTP(HOST, PORT, timeout=10)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(USER, PASSWORD)
	s.sendmail(USER, [RECIPIENT], 'Subject:SMTP Test\n\nOK')
	s.quit()
	print('SMTP OK — message queued/sent.')
except Exception as e:
	print('SMTP test failed:', repr(e))
	raise
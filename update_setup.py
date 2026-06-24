import re

# Read the current SETUP.md
with open('SETUP.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new email section
new_email_section = """## ?? Step 7: Configure Email (For Password Reset & Account Notifications)

### Setup Steps (Using Environment Variables - Recommended):

1. **Enable 2-Step Verification on Gmail account** (`fitzone.alerts@gmail.com`):
   - Go to [myaccount.google.com/security](https://myaccount.google.com/security)
   - Find "2-Step Verification" and enable it
   - Confirm your phone number

2. **Generate App Password**:
   - Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select **App: Mail**
   - Select **Device: Other (custom name)** → type "Django FitZone"
   - Click **Generate**
   - Copy the **16-character password** shown (format: `xxxx xxxx xxxx xxxx`)

3. **Create/Update `.env` file** in project root:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_HOST_USER=fitzone.alerts@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password_here
   DEFAULT_FROM_EMAIL="FitZone <fitzone.alerts@gmail.com>"
   ```

4. **Do NOT commit `.env`** (add to `.gitignore` if not already there):
   ```bash
   echo ".env" >> .gitignore
   ```

5. **Restart Django** after updating `.env` for settings to take effect.

### Test Email Sending:

Once configured, test email delivery with the new management command:

```bash
# Send test email to your personal address
python manage.py send_test_email your@personal.email.com

# Or send to the configured account
python manage.py send_test_email
```

**Expected output:** "✓ Email sent successfully!" and you should receive the test email shortly.

**Alternative test (Django shell):**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Body', settings.DEFAULT_FROM_EMAIL, ['your@personal.email.com'])
```

**Note:** If `EMAIL_HOST_PASSWORD` is not set, Django will fall back to the console email backend (emails print to terminal instead of being sent).

---"""

# Use regex to replace the old email section with the new one
old_pattern = r'## \?\? Step 7: Configure Email.*?(?=---\s+## \?\? Step 8:)'
new_content = re.sub(old_pattern, new_email_section + '\n\n', content, flags=re.DOTALL)

# Write back to SETUP.md
with open('SETUP.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✓ SETUP.md updated successfully')

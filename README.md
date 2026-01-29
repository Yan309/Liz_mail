# 📧 Lizmail - Automated Email System

Simple, powerful email automation for HR professionals. Scan CVs, extract emails, send customized messages.

## ✨ Features

- **📁 CV Parsing**: Extract emails from PDF, Word, and ZIP files automatically
- **✉️ Email Templates**: Pre-built screening and rejection email templates
- **📋 Custom Emails**: Create templates with variables like `{candidate_name}`, `{position}`
- **⚡ Background Processing**: Send emails without blocking the interface
- **📊 Progress Tracking**: Monitor email sending status in real-time

## 🚀 5-Step Setup

### 1. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure SMTP (Required!)
Edit `.env` file:
```env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Gmail Setup:**
- Enable 2FA on your Google account
- Visit: https://myaccount.google.com/apppasswords
- Generate "App Password" for Mail
- Use that password (not your regular password!)

### 4. Run Application
```powershell
streamlit run app_simple.py
```

### 5. Open Browser
http://localhost:8501

## 📖 Usage

### Extract Emails from CVs
1. Go to **"Upload & Extract"** tab
2. Upload PDF/Word/ZIP files
3. Click **"Extract Emails"**
4. Download extracted email list (optional)

### Send Screening Emails
1. Go to **"Screening Email"** tab
2. Fill in: Company, Position, HR Name
3. Add optional screening questions
4. Select recipients
5. Click **"Send Screening Emails"**

### Send Rejection Emails
1. Go to **"Rejection Email"** tab
2. Fill in required details
3. Add encouraging message (optional)
4. Select recipients
5. Send!

### Send Custom Emails
1. Go to **"Custom Email"** tab
2. Write subject and body with variables: `{candidate_name}`, `{position}`, etc.
3. Define variable values
4. Select recipients
5. Send!

## ⚙️ Configuration (.env file)

| Variable | Description | Default |
|----------|-------------|---------|
| `SMTP_HOST` | SMTP server | smtp.gmail.com |
| `SMTP_PORT` | SMTP port | 587 |
| `SMTP_USER` | Your email | **REQUIRED** |
| `SMTP_PASSWORD` | App password | **REQUIRED** |
| `MAX_RETRIES` | Retry attempts | 3 |
| `PROCESSING_DELAY` | Delay between emails (seconds) | 2 |

## 🔧 Troubleshooting

**Virtual environment won't activate?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```

**SMTP authentication failed?**
- Use App Password, not regular password
- Enable 2-Factor Authentication first
- Check credentials in .env file

**No emails extracted from CVs?**
- Ensure CVs are readable text (not scanned images)
- Check file format: PDF, DOC, DOCX, ZIP only
- View console for error messages

**Module not found?**
```powershell
# Make sure venv is activated (see (venv) in prompt)
pip install -r requirements.txt
```

## 📁 Project Files

- `app_simple.py` - Main Streamlit application (use this!)
- `cv_parser.py` - CV email extraction
- `email_sender.py` - SMTP sending & templates
- `config.py` - Configuration management
- `requirements.txt` - Python dependencies
- `.env` - Your SMTP configuration

## 🎯 Tips

- **Rate Limiting**: Adjust `PROCESSING_DELAY` in .env (higher = slower/safer)
- **Gmail Limits**: ~500 emails/day for free accounts
- **Progress**: Check sidebar for sending status
- **Multiple Recipients**: Use multiselect to choose specific emails

## 🔒 Security

- Never commit `.env` file to git
- Use App Passwords instead of account passwords
- Keep credentials secure
- Rotate passwords regularly

## 💡 Example Workflow

1. Upload 50 CVs (PDF/Word/ZIP) → Extract emails
2. Filter to 20 candidates → Send screening emails
3. Review responses
4. Select 5 finalists → Send interview invitations  
5. Notify remaining → Send rejection emails

---

**Made with ❤️ for HR professionals | Streamlit-powered | No Docker required**

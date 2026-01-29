# 🔧 SMTP Setup for Company Email (aliyan.haq@liztek.ca)

## How to Find Your SMTP Settings

You need to get these details from your IT department or email provider:

### Required Information:
1. **SMTP Host** - The mail server address
2. **SMTP Port** - Usually 587 (TLS) or 465 (SSL)
3. **Your Email** - aliyan.haq@liztek.ca
4. **Your Password** - Your email password

---

## Common SMTP Server Patterns

Try these common formats (replace in .env file):

### Option 1: Standard Mail Server
```env
SMTP_HOST=mail.liztek.ca
SMTP_PORT=587
SMTP_USER=aliyan.haq@liztek.ca
SMTP_PASSWORD=your-password
```

### Option 2: SMTP Subdomain
```env
SMTP_HOST=smtp.liztek.ca
SMTP_PORT=587
SMTP_USER=aliyan.haq@liztek.ca
SMTP_PASSWORD=your-password
```

### Option 3: If Using Microsoft 365/Outlook
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=aliyan.haq@liztek.ca
SMTP_PASSWORD=your-password
```

### Option 4: If Using Google Workspace (G Suite)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=aliyan.haq@liztek.ca
SMTP_PASSWORD=your-password
```

---

## How to Find Your Company's Settings

### Method 1: Check Your Email Client
1. Open Outlook/Thunderbird/Mail app
2. Go to **Account Settings**
3. Look for **Outgoing Mail (SMTP)** settings
4. Copy the server name and port

### Method 2: Ask IT Department
Contact your IT support and ask for:
- "SMTP server address for sending emails"
- "SMTP port number"
- "Does it require TLS/SSL?"

### Method 3: Online Lookup
Search: **"liztek.ca SMTP settings"** or **"liztek SMTP server"**

---

## Testing Your Configuration

1. **Update .env file** with correct settings
2. **Restart the Streamlit app**
3. Go to **SMTP Settings** in sidebar
4. Click **"Test SMTP Connection"**
5. If it works → ✅ You're ready!
6. If it fails → Try another configuration

---

## Common Ports

| Port | Type | When to Use |
|------|------|-------------|
| 587 | TLS | Most modern servers (try first) |
| 465 | SSL | Older secure servers |
| 25 | None/TLS | Usually blocked by ISPs |
| 2525 | Alternative | Backup for port 25 |

---

## Troubleshooting

**"Authentication failed"**
→ Check your password is correct
→ Some companies require app passwords (like Gmail)

**"Connection refused"**
→ Wrong SMTP_HOST or SMTP_PORT
→ Check firewall/antivirus settings

**"Connection timeout"**
→ Server address might be wrong
→ Port might be blocked

---

## Current Configuration

Your `.env` file is currently set to:
```env
SMTP_HOST=mail.liztek.ca
SMTP_PORT=587
SMTP_USER=aliyan.haq@liztek.ca
SMTP_PASSWORD=your-email-password
```

**⚠️ Replace `your-email-password` with your actual email password!**

---

## Quick Test Command

After updating .env, test in PowerShell:

```powershell
# Restart the app to load new settings
# The app will show connection status in the SMTP Settings panel
```

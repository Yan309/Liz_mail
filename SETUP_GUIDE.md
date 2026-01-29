# 🚀 Step-by-Step Setup Guide

## Step 1: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

## Step 2: Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

## Step 3: Configure Environment

```powershell
# Copy the example environment file
copy .env.example .env

# Now edit .env file and add your SMTP credentials
notepad .env
```

**Required settings in .env:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**For Gmail:**
1. Go to https://myaccount.google.com/apppasswords
2. Generate an "App Password"
3. Use that password in SMTP_PASSWORD

## Step 4: Run the Application

```powershell
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Run the Streamlit app
streamlit run app.py
```

## Step 5: Access the Application

The app will automatically open in your browser at:
**http://localhost:8501**

---

## Quick Commands Reference

```powershell
# Activate virtual environment (if not active)
.\venv\Scripts\activate

# Deactivate virtual environment
deactivate

# Run the app
streamlit run app.py

# Reinstall dependencies (if needed)
pip install -r requirements.txt
```

## Troubleshooting

**Issue**: Virtual environment won't activate
```powershell
# Try this command first
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
.\venv\Scripts\activate
```

**Issue**: Module not found errors
```powershell
# Make sure you're in the virtual environment (see (venv) in prompt)
# Then reinstall
pip install -r requirements.txt
```

**Issue**: SMTP authentication failed
- For Gmail: Use App Password, not your regular password
- Enable 2-Factor Authentication first
- Generate App Password from Google Account settings

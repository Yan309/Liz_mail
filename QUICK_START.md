# Quick Start Scripts

## Windows

### Start with Docker (Recommended)
```batch
docker-compose up -d
```

### Start Locally
```batch
# Terminal 1 - Start Worker
python worker.py

# Terminal 2 - Start Web App
streamlit run app.py
```

### Quick Setup Script
```batch
python run.py
```

## Linux/Mac

### Start with Docker (Recommended)
```bash
docker-compose up -d
```

### Start Locally
```bash
# Terminal 1 - Start Worker
python worker.py

# Terminal 2 - Start Web App
streamlit run app.py
```

### Quick Setup Script
```bash
python run.py
```

## Access Points

- **Web Application**: http://localhost:8501
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## Configuration

1. Copy `.env.example` to `.env`
2. Add your SMTP credentials
3. Adjust other settings as needed

## Need Help?

See README.md for detailed documentation.

"""Quick start script to run the application locally."""
import subprocess
import sys
import os
import time
from pathlib import Path


def check_env_file():
    """Check if .env file exists."""
    if not Path('.env').exists():
        print("⚠️  .env file not found!")
        print("Creating .env from .env.example...")
        if Path('.env.example').exists():
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created. Please configure it with your SMTP credentials.")
            print("Edit .env file and then run this script again.")
            sys.exit(0)
        else:
            print("❌ .env.example not found either!")
            sys.exit(1)


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import streamlit
        import pika
        import dotenv
        print("✅ Dependencies are installed")
        return True
    except ImportError:
        print("⚠️  Dependencies not installed")
        print("Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True


def check_rabbitmq():
    """Check if RabbitMQ is running."""
    try:
        import pika
        from config import Config
        
        credentials = pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=Config.RABBITMQ_HOST,
            port=Config.RABBITMQ_PORT,
            credentials=credentials,
            connection_attempts=1,
            retry_delay=1
        )
        connection = pika.BlockingConnection(parameters)
        connection.close()
        print("✅ RabbitMQ is running")
        return True
    except Exception as e:
        print("⚠️  RabbitMQ is not running")
        print("\nTo start RabbitMQ with Docker:")
        print("  docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management")
        print("\nOr use Docker Compose:")
        print("  docker-compose up -d rabbitmq")
        return False


def main():
    """Run the startup script."""
    print("🚀 Starting Lizmail Setup...\n")
    
    # Check .env
    check_env_file()
    
    # Check dependencies
    check_dependencies()
    
    # Check RabbitMQ
    rabbitmq_running = check_rabbitmq()
    
    if not rabbitmq_running:
        response = input("\nDo you want to continue without RabbitMQ? (emails won't be sent) [y/N]: ")
        if response.lower() != 'y':
            print("Please start RabbitMQ and run this script again.")
            sys.exit(0)
    
    print("\n" + "="*60)
    print("📧 Lizmail - Automated Email System")
    print("="*60)
    
    print("\n📝 To use the system:")
    print("1. Start the worker (in a separate terminal):")
    print("   python worker.py")
    print("\n2. The Streamlit app will open in your browser")
    print("\n3. Configure SMTP settings in the web interface or .env file")
    print("\n" + "="*60 + "\n")
    
    # Start Streamlit
    print("🌐 Starting Streamlit application...\n")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])


if __name__ == "__main__":
    main()

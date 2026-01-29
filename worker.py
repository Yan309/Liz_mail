"""Background worker to consume email tasks from RabbitMQ and send emails."""
import sys
import logging
from email_sender import EmailSender
from queue_manager import EmailQueueConsumer
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start the email worker."""
    try:
        logger.info("Starting Email Worker...")
        
        # Validate configuration
        Config.validate()
        
        # Initialize email sender
        email_sender = EmailSender()
        
        # Test SMTP connection
        if not email_sender.test_connection():
            logger.error("SMTP connection failed. Please check your configuration.")
            sys.exit(1)
        
        logger.info("SMTP connection verified successfully")
        
        # Initialize and start consumer
        consumer = EmailQueueConsumer(email_sender.send_email)
        
        logger.info("Email Worker is ready and waiting for messages...")
        logger.info(f"Queue: {Config.RABBITMQ_QUEUE}")
        logger.info("Press CTRL+C to stop")
        
        consumer.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Email Worker stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in Email Worker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

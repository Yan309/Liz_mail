"""RabbitMQ message queue implementation for email processing."""
import pika
import json
import logging
import time
from typing import Dict, Any, Callable
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailQueueProducer:
    """Producer to send email tasks to RabbitMQ."""
    
    def __init__(self):
        """Initialize connection to RabbitMQ."""
        self.connection = None
        self.channel = None
        self.connect()
    
    def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(
                Config.RABBITMQ_USER,
                Config.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue with persistence
            self.channel.queue_declare(
                queue=Config.RABBITMQ_QUEUE,
                durable=True
            )
            
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def send_email_task(self, email_data: Dict[str, Any]) -> bool:
        """
        Send an email task to the queue.
        
        Args:
            email_data: Dictionary containing email details
                {
                    'to': 'recipient@example.com',
                    'subject': 'Email subject',
                    'body': 'Email body',
                    'template_type': 'screening' or 'rejection',
                    'metadata': {...}
                }
        
        Returns:
            True if successful, False otherwise
        """
        try:
            message = json.dumps(email_data)
            
            self.channel.basic_publish(
                exchange='',
                routing_key=Config.RABBITMQ_QUEUE,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Email task queued for: {email_data.get('to', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue email task: {e}")
            return False
    
    def send_bulk_email_tasks(self, email_list: list) -> Dict[str, int]:
        """
        Send multiple email tasks to the queue.
        
        Returns:
            Dictionary with 'success' and 'failed' counts
        """
        stats = {'success': 0, 'failed': 0}
        
        for email_data in email_list:
            if self.send_email_task(email_data):
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(f"Bulk queue operation: {stats['success']} succeeded, {stats['failed']} failed")
        return stats
    
    def close(self):
        """Close RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")


class EmailQueueConsumer:
    """Consumer to process email tasks from RabbitMQ."""
    
    def __init__(self, email_sender_callback: Callable):
        """
        Initialize consumer.
        
        Args:
            email_sender_callback: Function to call for sending emails
        """
        self.connection = None
        self.channel = None
        self.email_sender_callback = email_sender_callback
        self.connect()
    
    def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(
                Config.RABBITMQ_USER,
                Config.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue (ensure it exists)
            self.channel.queue_declare(
                queue=Config.RABBITMQ_QUEUE,
                durable=True
            )
            
            # Set QoS to process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info("Consumer connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect consumer to RabbitMQ: {e}")
            raise
    
    def callback(self, ch, method, properties, body):
        """Process a message from the queue."""
        try:
            # Parse message
            email_data = json.loads(body)
            logger.info(f"Processing email for: {email_data.get('to', 'unknown')}")
            
            # Send email using callback
            success = self.email_sender_callback(email_data)
            
            if success:
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Email sent successfully to: {email_data.get('to', 'unknown')}")
            else:
                # Reject and requeue for retry
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                logger.warning(f"Email failed, requeuing: {email_data.get('to', 'unknown')}")
            
            # Add delay to prevent overwhelming SMTP server
            time.sleep(Config.PROCESSING_DELAY)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject without requeue if message is malformed
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Start consuming messages from the queue."""
        try:
            self.channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE,
                on_message_callback=self.callback
            )
            
            logger.info("Started consuming messages. Press CTRL+C to exit.")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            raise
    
    def stop_consuming(self):
        """Stop consuming messages."""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("Consumer stopped and connection closed")
        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")

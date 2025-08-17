import boto3
import json
import time

# Create SQS client only (no SNS needed for receiving)
sqs = boto3.client('sqs', region_name='ap-southeast-1')

# Define queue name (matching the publisher)
queue_name = 'LifeBeing_sensor_queue'

print(f"Starting LifeBeing sensor data receiver...")

# Get the SQS queue
try:
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    print(f"Connected to queue: {queue_url}")
except sqs.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
        print(f"Error: Queue '{queue_name}' not found. Please run the publisher first to create the queue.")
        exit()
    else:
        raise e

print("Waiting for LifeBeing sensor messages...")

while True:
    try:
        # Poll for messages
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
            AttributeNames=['All'],
            MessageAttributeNames=['All']
        )

        if 'Messages' in messages:
            for msg in messages['Messages']:
                try:
                    # Parse the message body
                    if 'Body' in msg:
                        message_data = json.loads(msg['Body'])

                        print(f"\n--- Received LifeBeing Sensor Data ---")
                        print(f"Datetime: {message_data.get('datetime', 'N/A')}")
                        print(f"Room: {message_data.get('room', 'N/A')}")
                        print(f"Online Status: {message_data.get('online_status', 'N/A')}")
                        print(f"Sensitivity: {message_data.get('sensitivity', 'N/A')}")
                        print(f"Presence State: {message_data.get('presence_state', 'N/A')}")
                        print("----------------------------------------")

                    # Delete message from queue after processing
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg['ReceiptHandle']
                    )

                except json.JSONDecodeError as e:
                    print(f"Error parsing message: {e}")
                except Exception as e:
                    print(f"Error processing message: {e}")
        else:
            print("No messages received. Polling again...")

    except KeyboardInterrupt:
        print("\nStopping subscriber...")
        break
    except Exception as e:
        print(f"Error receiving messages: {e}")
        time.sleep(5)

import threading
import boto3
import json
import time
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_building.settings')
django.setup()
from raw_data.models import RawData

def save_raw_data(timestamp, dt, device_id, datapoint, value):
    RawData.objects.create(
        timestamp=timestamp,
        datetime=dt,
        device_id=device_id,
        datapoint=datapoint,
        value=str(value)
    )

def iaq_subscriber():
    sqs = boto3.client('sqs', region_name='ap-southeast-1')
    sns = boto3.client('sns', region_name='ap-southeast-1')
    queue_name = 'MyPythonSNSQueue'
    topic_name = 'IAQ_sensor_topic'

    # Get topic ARN (assuming it was created by the publisher)
    try:
        response = sns.list_topics()
        topic_arn = next(topic['TopicArn'] for topic in response['Topics'] if topic_name in topic['TopicArn'])
    except StopIteration:
        print(f"Error: SNS Topic '{topic_name}' not found. Please run the publisher script first.")
        exit()

    # Create an SQS queue
    try:
        queue_response = sqs.create_queue(QueueName=queue_name)
        queue_url = queue_response['QueueUrl']
        print(f"Queue URL: {queue_url}")
    except sqs.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'QueueAlreadyExists':
            queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
            print(f"Queue '{queue_name}' already exists. URL: {queue_url}")
        else:
            raise e

    # Get queue ARN
    queue_attributes = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['QueueArn']
    )
    queue_arn = queue_attributes['Attributes']['QueueArn']

    # Set SQS queue policy to allow SNS to send messages
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AllowSNSSubscription",
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "SQS:SendMessage",
            "Resource": queue_arn,
            "Condition": {
                "ArnEquals": {
                    "aws:SourceArn": topic_arn
                }
            }
        }]
    }
    sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={'Policy': json.dumps(policy)}
    )

    # Subscribe the SQS queue to the SNS topic
    subscribe_response = sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint=queue_arn
    )
    print(f"Subscription ARN: {subscribe_response['SubscriptionArn']}")

    print("Waiting for messages...")
    while True:
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        if 'Messages' in messages:
            for msg in messages['Messages']:
                body = json.loads(msg['Body'])
                try:
                    data = json.loads(body['Message']) if isinstance(body['Message'], str) else body['Message']
                    device_id = data.get('room', 'unknown')
                    for key in ['co2', 'humidity', 'temperature']:
                        if key in data:
                            save_raw_data(
                                timestamp=int(time.mktime(datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M:%S.%f").timetuple())),
                                dt=datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M:%S.%f"),
                                device_id=device_id,
                                datapoint=key,
                                value=data[key]
                            )
                    print(f"[IAQ] Saved data for device {device_id} at {data['datetime']}")
                except Exception as e:
                    print(f"[IAQ] Error saving data: {e}")
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg['ReceiptHandle']
                )
        else:
            print("No messages received. Polling again...")

def life_being_subscriber():
    sqs = boto3.client('sqs', region_name='ap-southeast-1')
    queue_name = 'LifeBeing_sensor_queue'
    print(f"[LifeBeing] Starting LifeBeing sensor data receiver...")
    try:
        queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
        print(f"[LifeBeing] Connected to queue: {queue_url}")
    except sqs.exceptions.ClientError as e:
        print(f"[LifeBeing] Error: Queue '{queue_name}' not found. Please run the publisher first to create the queue.")
        return
    print("[LifeBeing] Waiting for LifeBeing sensor messages...")
    while True:
        try:
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
                        if 'Body' in msg:
                            data = json.loads(msg['Body'])
                            device_id = data.get('room', 'unknown')
                            for key in ['online_status', 'sensitivity', 'presence_state']:
                                if key in data:
                                    save_raw_data(
                                        timestamp=int(time.mktime(datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M:%S.%f").timetuple())),
                                        dt=datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M:%S.%f"),
                                        device_id=device_id,
                                        datapoint=key,
                                        value=data[key]
                                    )
                            print(f"[LifeBeing] Saved data for device {device_id} at {data['datetime']}")
                        sqs.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=msg['ReceiptHandle']
                        )
                    except Exception as e:
                        print(f"[LifeBeing] Error saving data: {e}")
            else:
                print("[LifeBeing] No messages received. Polling again...")
        except KeyboardInterrupt:
            print("[LifeBeing] Stopping LifeBeing subscriber...")
            break
        except Exception as e:
            print(f"[LifeBeing] Error receiving messages: {e}")
            time.sleep(5)

if __name__ == "__main__":
    t1 = threading.Thread(target=iaq_subscriber)
    t2 = threading.Thread(target=life_being_subscriber)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

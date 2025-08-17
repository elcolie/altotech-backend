import boto3
import csv
import time
import json
import os

# Create SQS client instead of SNS
sqs = boto3.client('sqs', region_name='ap-southeast-1')

# Define queue name
queue_name = 'LifeBeing_sensor_queue'

# Get or create the SQS queue
try:
    queue_response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'VisibilityTimeout': '60',
            'MessageRetentionPeriod': '1209600'  # 14 days
        }
    )
    queue_url = queue_response['QueueUrl']
    print(f"Queue URL: {queue_url}")
except sqs.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'QueueAlreadyExists':
        queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
        print(f"Queue '{queue_name}' already exists. URL: {queue_url}")
    else:
        raise e

# Path to the CSV file
csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'sample_presence_sensor_data_Room101.csv')

print(f"Starting LifeBeing data publisher - reading from {csv_file_path}")
print("Publishing sensor data every 5 seconds...")

try:
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        row_count = 0

        for row in reader:
            row_count += 1

            # Skip empty rows
            if not row or len(row) < 4:
                print(f"Skipping row {row_count}: insufficient data")
                continue

            # Check if this is a header row (contains non-numeric data in sensitivity column)
            try:
                # Try to convert the third column (index 2) to float
                sensitivity_value = float(row[2])
            except ValueError:
                print(f"Skipping row {row_count}: appears to be header or invalid data - {row}")
                continue

            # Extract data from CSV row (no header, so use indices)
            data = {
                "datetime": row[0],
                "room": "Room101",
                "online_status": row[1],
                "sensitivity": sensitivity_value,
                "presence_state": row[3]
            }

            # Send message directly to SQS queue
            message_response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(data, indent=2),
                MessageAttributes={
                    'room': {
                        'StringValue': 'Room101',
                        'DataType': 'String'
                    },
                    'sensor_type': {
                        'StringValue': 'LifeBeing',
                        'DataType': 'String'
                    }
                }
            )

            print(f"Row {row_count}: Published data - Online: {data['online_status']}, Sensitivity: {data['sensitivity']}, Presence: {data['presence_state']}")
            print(f"MessageId: {message_response['MessageId']}")

            # Wait 5 seconds before reading next row
            time.sleep(5)

        print(f"Finished processing all valid rows from the CSV file.")

except FileNotFoundError:
    print(f"Error: CSV file not found at {csv_file_path}")
except Exception as e:
    print(f"Error reading CSV file or publishing data: {e}")


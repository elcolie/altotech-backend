import boto3
import csv
import time
import json
import os

# Create an SNS client
sns = boto3.client('sns', region_name='ap-southeast-1',)

# Define topic name
topic_name = 'IAQ_sensor_topic'

try:
    # Create an SNS topic
    response = sns.create_topic(Name=topic_name)
    topic_arn = response['TopicArn']
    print(f"Topic ARN: {topic_arn}")
except sns.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'TopicLimitExceeded':
        print("Topic limit exceeded. Please delete unused topics or request a limit increase.")
    else:
        # If topic already exists, get its ARN
        response = sns.list_topics()
        for topic in response['Topics']:
            if topic_name in topic['TopicArn']:
                topic_arn = topic['TopicArn']
                print(f"Topic '{topic_name}' already exists. ARN: {topic_arn}")
                break
        else:
            raise e # Re-raise if topic not found and it's not a TopicLimitExceeded error

# Path to the CSV file
csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'sample_iaq_data_Room101.csv')

print(f"Starting IAQ data publisher - reading from {csv_file_path}")
print("Publishing sensor data every 5 seconds...")

try:
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        row_count = 0

        for row in reader:
            row_count += 1

            # Extract data from CSV row
            data = {
                "datetime": row['datetime'],
                "room": "101",
                "co2": float(row['co2']),
                "humidity": float(row['humidity']),
                "temperature": float(row['temperature'])
            }

            # Create message content
            message = json.dumps(data, indent=2)
            subject = f"IAQ Sensor Data - Room101 - Row {row_count}"

            # Publish the message
            publish_response = sns.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=subject
            )

            print(f"Row {row_count}: Published data - CO2: {data['co2']}, Humidity: {data['humidity']}, Temperature: {data['temperature']}")
            print(f"MessageId: {publish_response['MessageId']}")

            # Wait 5 seconds before reading next row
            time.sleep(5)

        print(f"Finished processing all {row_count} rows from the CSV file.")

except FileNotFoundError:
    print(f"Error: CSV file not found at {csv_file_path}")
except Exception as e:
    print(f"Error reading CSV file or publishing data: {e}")

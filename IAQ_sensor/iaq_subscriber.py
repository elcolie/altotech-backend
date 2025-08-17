import boto3
import json

# Create SQS and SNS clients
sqs = boto3.client('sqs', region_name='ap-southeast-1')
sns = boto3.client('sns', region_name='ap-southeast-1')

# Define queue and topic names
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
            print(f"Received message: {body['Message']}")
            # Delete message from queue after processing
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
    else:
        print("No messages received. Polling again...")

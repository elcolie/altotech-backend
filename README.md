# IAQ_sensor/iaq_publisher.py
1. Run `export.sh` to export the AWS credential
2. Run the `iaq_publisher.py` to publish the message
3. Run the `iaq_subscriber.py` to subscribe the message

# LifeBeing Sensor
Run into SNS error then use direct SQS to bypass the problem.
1. Run `export.sh` to export the AWS credential
1. Run [life_being_publisher.py](LifeBeing_sensor/life_being_publisher.py) to publish the message
2. Run [life_being_subscriber.py](LifeBeing_sensor/life_being_subscriber.py) to subscribe the message


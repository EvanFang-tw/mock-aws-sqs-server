import boto3

# boto3.set_stream_logger(name='botocore')

client = boto3.client(
    "sqs",
    region_name="ap-southeast-1",
    endpoint_url="http://localhost:8866",
    aws_access_key_id="test_key",
    aws_secret_access_key="test_secret",
)

response = client.get_queue_url(QueueName="q1")

print(response["QueueUrl"])

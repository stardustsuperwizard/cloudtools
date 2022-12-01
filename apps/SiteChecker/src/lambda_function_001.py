import boto3
import csv
import io
import os


def ip_list(data):
    spamreader = csv.reader(io.StringIO(data), delimiter-',', quotechar='|')
    for row in spamreader:
        yield row[0].strip()


def lambda_handler(event, context):
    print(event)
    s3 = boto3.client('s3')
    sqs = boto3.resource('sqs')
    queue = sqs.Queue(f"https://sqs.{os.environ['AWS_REGION']}.amazonaws.com/{os.environ['APP_ACCOUNT']}/{os.environ['APP_ENV']}-sitechecker")

    remote_object_data = s3.get_object(
        Bucket=os.environ['S3_Bucket'],
        Key=f"{os.environ['APP_ENV']}-ip_list.csv",
    )

    data = remote_object_data['Body'].read().decode('utf-8')
    for ip in ip_list(data):
        response = queue.send_message(MessageBody=ip)
        print(response)

    return
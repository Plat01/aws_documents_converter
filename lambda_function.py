import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv(dotenv_path='lambda.env')

# Initialize AWS clients
sqs = boto3.client('sqs')
ec2 = boto3.client('ec2')

# Get environment variables
QUEUE_URL = os.environ['SQS_QUEUE_URL']
INSTANCE_AMI = os.environ['EC2_AMI_ID']
INSTANCE_TYPE = os.environ['EC2_INSTANCE_TYPE']
MAX_INSTANCES = 2

def get_running_instances() -> list[str]:
    """Get list of running conversion instances"""
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            },
            {
                'Name': 'tag:Role',
                'Values': ['pdf-converter']
            }
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return instances

def get_queue_length() -> int:
    """Get number of messages in SQS queue"""
    response = sqs.get_queue_attributes(
        QueueUrl=QUEUE_URL,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    return int(response['Attributes']['ApproximateNumberOfMessages'])

def start_new_instance():
    """Start a new EC2 instance for conversion"""
    ec2.run_instances(
        ImageId=INSTANCE_AMI,
        InstanceType=INSTANCE_TYPE,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Role',
                    'Value': 'pdf-converter'
                }
            ]
        }]
    )

def stop_idle_instance(instance_id: str):
    """Stop an idle EC2 instance"""
    ec2.stop_instances(InstanceIds=[instance_id])

def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        # Get current state
        queue_length = get_queue_length()
        running_instances = get_running_instances()
        running_count = len(running_instances)

        # Logic for managing instances
        if queue_length > 0 and running_count < MAX_INSTANCES:
            # Start new instance if there are tasks and capacity
            start_new_instance()
            return {
                'statusCode': 200,
                'body': json.dumps('Started new conversion instance')
            }
        
        elif queue_length == 0 and running_count > 0:
            # Stop instance if queue is empty
            stop_idle_instance(running_instances[0])
            return {
                'statusCode': 200,
                'body': json.dumps('Stopped idle conversion instance')
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps('No action needed')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        } 
    
if __name__ == '__main__':
    lambda_handler({}, {})

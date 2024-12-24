import os
import json
import boto3
import subprocess
from botocore.exceptions import NoCredentialsError

sqs = boto3.client('sqs')
s3 = boto3.client('s3')

QUEUE_URL = os.environ['SQS_QUEUE_URL']
BUCKET_NAME = os.environ['S3_BUCKET']

def get_task_from_sqs():
    """Retrieve a task from SQS."""
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )
    messages = response.get('Messages', [])
    if not messages:
        return None, None

    message = messages[0]
    receipt_handle = message['ReceiptHandle']
    body = json.loads(message['Body'])
    return body, receipt_handle

def delete_task_from_sqs(receipt_handle):
    """Delete a task from SQS."""
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )

def download_file_from_s3(document_id):
    """Download a PDF file from S3."""
    pdf_file = f"{document_id}.pdf"
    s3.download_file(BUCKET_NAME, f"{document_id}/{pdf_file}", pdf_file)
    return pdf_file

def upload_file_to_s3(document_id, doc_file):
    """Upload a DOC file to S3."""
    s3.upload_file(doc_file, BUCKET_NAME, f"{document_id}/{doc_file}")

def convert_pdf_to_doc(pdf_file):
    """Convert a PDF file to DOC format using LibreOffice."""
    doc_file = pdf_file.replace('.pdf', '.doc')
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'doc', pdf_file])
    return doc_file

def main():
    while True:
        task, receipt_handle = get_task_from_sqs()
        if not task:
            print("No tasks in queue. Exiting.")
            break

        document_id = task['document_id']

        try:
            pdf_file = download_file_from_s3(document_id)

            doc_file = convert_pdf_to_doc(pdf_file)

            upload_file_to_s3(document_id, doc_file)

            delete_task_from_sqs(receipt_handle)

            os.remove(pdf_file)
            os.remove(doc_file)

            print(f"Successfully processed document {document_id}")

        except Exception as e:
            print(f"Failed to process document {document_id}: {str(e)}")

if __name__ == "__main__":
    main()
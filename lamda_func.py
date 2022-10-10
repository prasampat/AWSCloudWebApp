import os
import boto3
import json
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
configFile = open('AppConfig.json')
configData=json.load(configFile)

s3 = boto3.client(
    's3',
   aws_access_key_id = configData['AWS_ACCESS_KEY_ID'],
	aws_secret_access_key =configData['AWS_SECRET_ACCESS_KEY'],
	region_name =configData['REGION_NAME']
    )
    
ses_client = boto3.client(
    'ses',
    aws_access_key_id = configData['AWS_ACCESS_KEY_ID'],
	aws_secret_access_key =configData['AWS_SECRET_ACCESS_KEY'],
	region_name =configData['REGION_NAME']
    )

def send_email(sender,recipient,file_path):
  
    BODY = """\
    <html>
    <body>
    <h1>File Uploader</h1>
    <p>Hi. You've received file attachments from student file uploader application. Enjoy viewing the files</p>
    </body>
    </html>
    """

 
    msg = MIMEMultipart('mixed')
    msg['Subject'] = "You're received files. please see attachments"
    msg['From'] = sender
    msg['To'] = recipient

    msg_body = MIMEMultipart('alternative')
    htmlpart = MIMEText(BODY.encode("utf-8"), 'html', "utf-8")
  
    msg_body.attach(htmlpart)
    att = MIMEApplication(open(file_path, 'rb').read())

    att.add_header('Content-Disposition','attachment',filename=os.path.basename(file_path))

    msg.attach(msg_body)

    msg.attach(att)
    #print(msg)
    try:
        response = ses_client.send_raw_email(
            Source=sender,
            Destinations=[
                recipient
            ],
            RawMessage={
                'Data':msg.as_string(),
            }

        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent")


def lambda_handler(event, context):
    record = event['Records'][0]
    s3object = record['s3']['object']['key']
      
    s3.download_file(configData['BUCKET_EMAIL'], "emails.json", '/tmp/emails.json')

    s3object_path=f'/tmp/{s3object}'
    s3.download_file(configData['BUCKET_NAME'], s3object, s3object_path)
            
    file_path=s3object_path

    emailsfile=json.load(open('/tmp/emails.json'))
    recipients= emailsfile['recipients']
      
    for recipient in recipients:
        send_email(emailsfile['sender'],recipient,file_path)

    return {
        'statusCode': 200,
        'body': json.dumps({"reponse":"Emails sent succesfuly"})
    }

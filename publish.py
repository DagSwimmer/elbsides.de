#!env python3
import os
import boto3
from datetime import datetime

REGION = "eu-west-1"
PROFILE = "personal.iam"

print("auto-commit on publish")
os.system("git commit -a -m \"auto-commit on publish\"")

session = boto3.Session(profile_name=PROFILE, region_name=REGION)
s3_client = session.client('s3')

# files and where they go

www = [
    {'file': 'www/index.html', 'bucket':'elbsides.de', 'key': 'index.html', 'ct':'text/html'},
    {'file': 'www/images/favicon.ico', 'bucket':'elbsides.de', 'key': 'favicon.ico', 'ct':'image/png'},
    {'file': 'www/images/dfn-cert.gif', 'bucket':'elbsides.de', 'key': 'images/dfn-cert.gif', 'ct':'image/gif'},
    {'file': 'www/images/ElbSides_Circuit_V2.png', 'bucket':'elbsides.de', 'key': 'images/ElbSides_Circuit_V2.png', 'ct':'image/png' },
    {'file': 'www/css/normalize.css', 'bucket':'elbsides.de', 'key': 'css/normalize.css', 'ct':'text/css' },
    {'file': 'www/css/styles.css', 'bucket':'elbsides.de', 'key': 'css/styles.css', 'ct':'text/css'} ]
c2019 = [
    {'file': '2019/index.html', 'bucket':'2019.elbsides.de', 'key': 'index.html', 'ct':'text/html'},
    {'file': '2019/images/favicon.ico', 'bucket':'2019.elbsides.de', 'key': 'favicon.ico', 'ct':'image/png'},
    {'file': '2019/images/ElbSides_Circuit_V3.png', 'bucket':'2019.elbsides.de', 'key': 'images/ElbSides_Circuit_V3.png', 'ct':'image/png' },
    {'file': '2019/css/styles.css', 'bucket':'2019.elbsides.de', 'key': 'css/styles.css', 'ct':'text/css'} ]

# useful functions to stay DRY

def transfer(localFile, bucket, destKey, ct="application/html"):
    print("Getting S3 info from s3://{}/{}".format(bucket, destKey))
    try:
        response = s3_client.get_object(Bucket=bucket, Key=destKey)
        #print(response)
        file_datetime = datetime.fromtimestamp(os.path.getmtime(localFile)).astimezone()
        #print(file_datetime)
        if response['LastModified'] < file_datetime:
            with open(localFile, 'rb') as f:
                print("Transferring", bucket, destKey)
                s3_client.put_object(Bucket=bucket, Key=destKey, ContentType=ct, Body=f)
        else:
            print("No changes to", localFile, destKey)
    except s3_client.exceptions.NoSuchKey:
        with open(localFile, 'rb') as f:
            print("Transferring", bucket, destKey)
            s3_client.put_object(Bucket=bucket, Key=destKey, ContentType=ct, Body=f)

def transfer_all(file_list):
    for o in file_list:
        transfer(localFile=o['file'], bucket=o['bucket'], destKey=o['key'], ct=o['ct'])

def validate_file(html_file):
    return os.system("html5validator {}".format(html_file)) == 0

def validate_all(file_list):
    return all([validate_file(o['file']) for o in file_list if o['ct'] =='text/html'])

# Do actual stuff

if validate_all(www):
    transfer_all(www)
else:
    print("www didn't validate")
        
if validate_all(c2019):
    transfer_all(c2019)
else:
    print("c2019 didn't validate")


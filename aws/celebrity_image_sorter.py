import csv
import boto3
import os

def load_credentials(filepath):
    with open(filepath, 'r') as input_file:
        next(input_file)  # Skip header
        reader = csv.reader(input_file)
        for line in reader:
            return line[0], line[1]  # Return Access Key and Secret Key

def detect_folder(s3_resource, bucket_name, folder_path):
    bucket = s3_resource.Bucket(bucket_name)
    for object_summary in bucket.objects.filter(Prefix=folder_path):
        return True
    return False

def create_folder_if_not_exists(s3_client, bucket_name, folder_name):
    if not detect_folder(s3_resource, bucket_name, folder_name):
        s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))

def upload_images_to_s3(s3_client, local_path, bucket_name, folder_name):
    images = os.listdir(local_path)
    for image_name in images:
        image_path = os.path.join(local_path, image_name)
        with open(image_path, "rb") as image_file:
            s3_client.upload_fileobj(image_file, bucket_name, folder_name + '/' + image_name)

def get_celebrity_name(rekognition_client, bucket_name, image_key):
    response = rekognition_client.recognize_celebrities(
        Image={'S3Object': {'Bucket': bucket_name, 'Name': image_key}}
    )
    for celebrity in response['CelebrityFaces']:
        return celebrity['Name']
    return None

def sort_images(s3_resource, rekognition_client, bucket_name, unsorted_prefix, sorted_prefix):
    bucket = s3_resource.Bucket(bucket_name)
    for object_summary in bucket.objects.filter(Prefix=unsorted_prefix):
        if object_summary.key != unsorted_prefix:
            celebrity_name = get_celebrity_name(rekognition_client, bucket_name, object_summary.key)
            if celebrity_name:
                new_key = f"{sorted_prefix}/{celebrity_name}/{object_summary.key.replace(unsorted_prefix, '')}"
                s3_resource.Object(bucket_name, new_key).copy_from(
                    CopySource={'Bucket': bucket_name, 'Key': object_summary.key}
                )
                object_summary.delete()  # Delete after copying

# Main execution starts here
credentials_path = 'credentials.csv'
bucket_name = "aayushsfirstbucket"
region_name = 'us-west-2'
images_local_path = '../images/'
unsorted_folder = "unsorted/"
sorted_folder = "sorted/"

access_key_id, secret_access_key = load_credentials(credentials_path)

# Initialize boto3 resources and clients
s3_resource = boto3.resource('s3', region_name=region_name, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
s3_client = boto3.client('s3', region_name=region_name, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
rekognition_client = boto3.client('rekognition', region_name=region_name, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

# Create sorted and unsorted folders if they don't exist
create_folder_if_not_exists(s3_client, bucket_name, sorted_folder)
create_folder_if_not_exists(s3_client, bucket_name, unsorted_folder)

# Upload images to the unsorted folder in S3
upload_images_to_s3(s3_client, images_local_path, bucket_name, unsorted_folder)

# Sort images into celebrity-named folders within the sorted folder
sort_images(s3_resource, rekognition_client, bucket_name, unsorted_folder, sorted_folder)

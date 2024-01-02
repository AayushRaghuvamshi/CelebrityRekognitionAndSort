# Celebrity Image Sorter

The Celebrity Image Sorter is a Python script that automates the process of sorting images into folders named after celebrities. It utilizes AWS Rekognition to recognize celebrities in the images stored in an AWS S3 bucket.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.6 or later.
- You have an AWS account with access to AWS S3 and Rekognition services.
- You have installed `boto3`, which is the AWS SDK for Python.

## Setup

To run this project, follow these steps:

### AWS Configuration

1. Sign in to your AWS Management Console.
2. Navigate to the IAM (Identity and Access Management) dashboard.
3. Create a new IAM user with programmatic access and attach the `AmazonRekognitionFullAccess` and `AmazonS3FullAccess` policies.
4. Download the credentials CSV file after creating the user. It contains the Access Key ID and Secret Access Key.
5. Create an S3 bucket where your images will be stored and processed.

### Local Environment Setup

1. Create a virtual environment (optional but recommended):
   ```shell
   python -m venv .venv
   source .venv/bin/activate  # For Unix/macOS
   .venv\Scripts\activate  # For Windows
   ```

2. Install `boto3` using pip:

   ```shell
   pip install boto3
   ```
3. Place the credentials CSV file you downloaded from AWS in your project directory.

4. Update the bucket_name variable in the script to match the name of your S3 bucket.

5. Place the images you want to sort in a directory named `../images/` relative to the script or modify the images_local_path variable in the script accordingly.

## Running the Script

Execute the script from the command line:

```shell
python .\celebrity_image_sorter.py
```

The script will upload images from your specified directory to the S3 bucket, sort them into folders named after the recognized celebrities using AWS Rekognition, and move them into the sorted/ folder within your S3 bucket.



import csv
import boto3
# import requests
import os

# code for detectFolder obtained from:
# https://stackoverflow.com/questions/57957585/how-to-check-if-a-particular-directory-exists-in-s3-bucket-using-python-and-boto


# this function will check if "path" is an object in an s3 bucket.



with open('credentials.csv', 'r') as input:
    next(input)
    reader = csv.reader(input)
    for line in reader:
        access_key_id = line[0]
        secret_access_key = line[1]

bucket_name = "aayushsfirstbucket"
s3_resource = boto3.resource('s3', region_name='us-west-2', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
def detectFolder(path):
    bucket = s3_resource.Bucket(bucket_name)
    for object_summary in bucket.objects.filter(Prefix=path):
        return True
    return False


s3 = boto3.client('s3', region_name='us-west-2', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)

folder_name = "sorted"

# This bit of code exists to check whether a folder named sorted already exists, and only if it doesn't will we
# create it, this is to prevent hazards on consecutive runs of this program.
if not detectFolder("sorted"):
    s3.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
folder_name = "unsorted"
if not detectFolder("unsorted"):
    s3.put_object(Bucket=bucket_name, Key=(folder_name + '/'))

client = boto3.client('rekognition', region_name='us-west-2', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)

# first, let's write some code that will add all files in the images folder, into the unsorted folder.

images = os.listdir('../images/')
if len(images) != 0:
    for entry in images:
        entry = str(entry)
        with open('../images/' + entry, "rb") as f:
            s3.upload_fileobj(f, bucket_name, entry) # this puts the image into the bucket
        s3_resource.Object(bucket_name, "unsorted/" + entry).copy_from(
        CopySource=bucket_name + "/" + entry)           # copies into unsorted folder
        s3.delete_object(Bucket=bucket_name, Key=entry)        # deletes original from general bucket directory

# Now the plan is to iterate over each file in the unsorted folder, and recognize the celebrity in each image,
# and move the image into the folder named after the corresponding celebrity, if the folder isn't already there
# (i.e. on iteration 1) then we will create it.

my_bucket = s3_resource.Bucket(bucket_name)

for object_summary in my_bucket.objects.filter(Prefix="unsorted/"):
    if object_summary.key != "unsorted/":
        s = str(object_summary.key)
        s = s.replace("unsorted/", "")
        s3_resource.Object(bucket_name, "sorted/" + entry).copy_from(
            CopySource=bucket_name + "/" + str(object_summary.key))
        s3.delete_object(Bucket=bucket_name, Key=str(object_summary.key))

# now that files are in the sorted folder, we need to recognise the celebrity in each image and move them into their
# folder

# Now that files are in the sorted folder, we need to recognise the celebrity in each image and move them into
# their folder

def celebrityName(response):
    people = []

    for key, value in response.items():
        if key == 'CelebrityFaces':
            for celebrity in value:
                people.append(celebrity)

    names = []

    for celebrity in people:
        for key, value in celebrity.items():
            if key == 'Name':
                names.append(value)

    return names[0]


for object_summary in my_bucket.objects.filter(Prefix="sorted/"):
    if object_summary.key != "sorted/":
        s = str(object_summary.key)
        print(s)
        response = client.recognize_celebrities(Image={'S3Object': {
            'Bucket': bucket_name,
            'Name': s
        }})
        n = celebrityName(response)     # We now use this name to create a folder with that name.
        # TODO: create folder named after celeb
        s3.put_object(Bucket=bucket_name, Key=("sorted/" + n + "/"))
        s = s.replace("sorted/", "")
        s3_resource.Object(bucket_name, "sorted/" + n + "/" + s).copy_from(
            CopySource=bucket_name + "/" + str(object_summary.key))
        s3.delete_object(Bucket=bucket_name, Key=str(object_summary.key))


# just some ideas I had for using occupation from wikidata directory to create folders accordingly
# occupations = []
#
# parameters = {
#     'action': 'wbsearchentities',
#     'format': 'json',
#     'language': 'en',
#     'search': name[0]
# }
#
# r = requests.get("https://www.wikidata.org/w/api.php", params = parameters)
#
# print(r.json()['search'][0]['description'])
#
# s3_resource = boto3.resource('s3', region_name='us-west-2', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
# # Copy object A as object B
# s3_resource.Object("aayushsfirstbucket", "unsorted/cr7.jpeg").copy_from(
#  CopySource="aayushsfirstbucket/cr7.jpeg")
# # Delete the former object A
# # s3_resource.Object("aayushsfirstbucket", "aayushsfirstbucket/cr7.jpeg").delete()
# s3 = boto3.client('s3', region_name='us-west-2', aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key)
# s3.delete_object(Bucket="aayushsfirstbucket", Key="cr7.jpeg")


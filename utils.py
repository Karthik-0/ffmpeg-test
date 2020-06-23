import os

import boto3

from new import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME

bucket = "media.testpress.in"
destination = "institute/demo/upload_test/big_video_g4_4x_libx"

client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=REGION_NAME)


def delete(path):
    try:
        client.delete_object(Bucket=bucket, Key=path)
    except:
        print("Unable to delete %s..." % path)


def upload_dir(local_dir, exclude_files=[]):
    for root, dirs, files in os.walk(local_dir):
        for filename in files:

            if filename.endswith(".tmp") or filename in exclude_files:
                continue

            # construct the full local path
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, local_dir)
            s3_path = os.path.join(destination, relative_path)

            print('Searching "%s" in "%s"' % (s3_path, bucket))
            try:
                client.head_object(Bucket=bucket, Key=s3_path)
                os.remove(local_path)
                print("Path found on S3! Skipping %s..." % s3_path)

            except:
                print("Uploading %s..." % s3_path)
                client.upload_file(local_path, bucket, s3_path)
                os.remove(local_path)


if __name__ == "__main__":
    upload_dir("video")

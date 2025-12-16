import os
import boto3
from dotenv import load_dotenv

def test_aws_connection():
    load_dotenv()
    access_key=os.getenv("AWS_ACCESS_KEY_ID")
    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    region=os.getenv("AWS_DEFAULT_REGION")
    bucket_name=os.getenv("AWS_S3_BUCKET_NAME")

    print("TEST AWS CON")
    print(f"region :{region}")
    print(f"bucket :{bucket_name}")

    try:
        s3=boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        buckets=s3.list_buckets()
        print(f"connectected, {len(buckets["Buckets"])} s3 buckets")
        return True
    except Exception as e:
        print(f"connection failed {e}")
        print("check ur env")
        return False
    
if __name__ =="__main__":
    test_aws_connection()





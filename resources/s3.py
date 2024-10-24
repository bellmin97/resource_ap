import boto3
from datetime import datetime

def get_s3_buckets(session):
    s3 = session.client('s3')
    s3_buckets = []
    
    try:
        response = s3.list_buckets()
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            try:
                # 버킷의 위치와 버전 관리를 가져옵니다.
                location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint'] or 'us-east-1'
                versioning = s3.get_bucket_versioning(Bucket=bucket_name)
                
                s3_buckets.append({
                    'Name': bucket_name,
                    'CreationDate': bucket['CreationDate'].isoformat(),
                    'Region': location,
                    'Versioning': 'Enabled' if versioning.get('Status') == 'Enabled' else 'Disabled',
                    'LastUpdated': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error fetching details for bucket {bucket_name}: {str(e)}")
    except Exception as e:
        print(f"Error listing buckets: {str(e)}")
    
    return s3_buckets

import boto3

def get_ec2_instances(session):
    ec2 = session.client('ec2')
    instances = ec2.describe_instances()
    detailed_instances = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            # 인스턴스의 이름 태그를 가져옵니다.
            name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            detailed_instances.append({
                'Name': name_tag,
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name'],
                'PublicIpAddress': instance.get('PublicIpAddress', 'N/A'),
                'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                'VpcId': instance.get('VpcId', 'N/A'),
                'SubnetId': instance.get('SubnetId', 'N/A'),
                'LaunchTime': instance['LaunchTime'].isoformat(),
                'Tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                'SecurityGroups': [sg['GroupName'] for sg in instance.get('SecurityGroups', [])],
                'ImageId': instance.get('ImageId', 'N/A'),
                'KeyName': instance.get('KeyName', 'N/A'),
            })
    return detailed_instances

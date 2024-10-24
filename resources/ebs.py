import boto3

def get_ebs_volumes(session):
    ec2 = session.client('ec2')
    volumes = ec2.describe_volumes()
    detailed_volumes = []
    for volume in volumes['Volumes']:
        # 볼륨의 첨부 상태를 확인합니다.
        attachment_state = 'N/A'
        if volume.get('Attachments'):
            attachment_state = volume['Attachments'][0].get('State', 'N/A')
        
        detailed_volumes.append({
            'VolumeId': volume['VolumeId'],
            'Size': volume['Size'],
            'VolumeType': volume['VolumeType'],
            'State': volume['State'],
            'AvailabilityZone': volume['AvailabilityZone'],
            'CreateTime': volume['CreateTime'].isoformat(),
            'AttachmentState': attachment_state,
            'Encrypted': volume['Encrypted'],
            'Iops': volume.get('Iops', 'N/A'),
            'Tags': {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
        })
    return detailed_volumes

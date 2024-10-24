import boto3

def get_vpcs(session):
    ec2 = session.client('ec2')
    vpcs = []
    
    try:
        response = ec2.describe_vpcs()
        for vpc in response['Vpcs']:
            # VPC의 이름 태그를 가져옵니다.
            name_tag = next((tag['Value'] for tag in vpc.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            
            vpcs.append({
                'Name': name_tag,
                'VpcId': vpc['VpcId'],
                'CidrBlock': vpc['CidrBlock'],
                'State': vpc['State'],
                'IsDefault': vpc['IsDefault'],
                'InstanceTenancy': vpc['InstanceTenancy'],
                'DhcpOptionsId': vpc.get('DhcpOptionsId', 'N/A'),
                'Tags': {tag['Key']: tag['Value'] for tag in vpc.get('Tags', []) if tag['Key'] != 'Name'}
            })
    except Exception as e:
        print(f"Error fetching VPCs: {str(e)}")
    
    return vpcs

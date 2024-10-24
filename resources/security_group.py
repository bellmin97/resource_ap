import boto3

def get_security_groups(session):
    ec2 = session.client('ec2')
    security_groups = []
    
    try:
        response = ec2.describe_security_groups()
        for sg in response['SecurityGroups']:
            inbound_rules = []
            outbound_rules = []
            
            for rule in sg['IpPermissions']:
                if 'IpRanges' in rule:
                    for ip_range in rule['IpRanges']:
                        inbound_rules.append({
                            'Protocol': rule.get('IpProtocol', 'All'),
                            'Ports': f"{rule.get('FromPort', 'All')}-{rule.get('ToPort', 'All')}",
                            'Source': ip_range['CidrIp']
                        })
            
            for rule in sg['IpPermissionsEgress']:
                if 'IpRanges' in rule:
                    for ip_range in rule['IpRanges']:
                        outbound_rules.append({
                            'Protocol': rule.get('IpProtocol', 'All'),
                            'Ports': f"{rule.get('FromPort', 'All')}-{rule.get('ToPort', 'All')}",
                            'Destination': ip_range['CidrIp']
                        })
            
            security_groups.append({
                'GroupName': sg['GroupName'],
                'GroupId': sg['GroupId'],
                'Description': sg['Description'],
                'VpcId': sg.get('VpcId', 'N/A'),
                'InboundRules': inbound_rules,
                'OutboundRules': outbound_rules,
                'Tags': ', '.join([f"{tag['Key']}:{tag['Value']}" for tag in sg.get('Tags', [])])
            })
    except Exception as e:
        print(f"Error fetching security groups: {str(e)}")
    
    return security_groups

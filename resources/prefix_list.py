import boto3

def get_prefix_lists(session):
    ec2 = session.client('ec2')
    prefix_lists = []
    
    try:
        response = ec2.describe_prefix_lists()
        for pl in response['PrefixLists']:
            prefix_lists.append({
                'PrefixListId': pl['PrefixListId'],
                'PrefixListName': pl['PrefixListName'],
                'Cidrs': ', '.join(pl['Cidrs'])
            })
    except Exception as e:
        print(f"Error fetching prefix lists: {str(e)}")
    
    return prefix_lists

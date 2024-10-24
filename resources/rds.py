import boto3

def get_rds_instances(session):
    rds = session.client('rds')
    instances = rds.describe_db_instances()
    return instances['DBInstances']

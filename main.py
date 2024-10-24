from flask import Flask, render_template, request, jsonify
import configparser
import boto3  # boto3 모듈을 가져옵니다.
from resources.ec2 import get_ec2_instances
from resources.rds import get_rds_instances
from resources.ebs import get_ebs_volumes
from resources.s3 import get_s3_buckets
from resources.prefix_list import get_prefix_lists
from resources.vpc import get_vpcs
from resources.security_group import get_security_groups
from botocore.config import Config
from datetime import datetime

app = Flask(__name__)

# AWS 자격증명 및 설정 파일 경로
AWS_CREDENTIALS_PATH = "/root/.aws/credentials"
AWS_CONFIG_PATH = "/root/.aws/config"

# AWS 프로파일 목록 가져오기
def get_aws_profiles():
    config = configparser.ConfigParser()
    config.read(AWS_CREDENTIALS_PATH)
    return config.sections()

# 선택된 프로파일로 AWS 세션 생성
def create_aws_session(profile_name):
    boto_config = Config(
        region_name=None,
        signature_version='v4',
        retries={'max_attempts': 10, 'mode': 'standard'}
    )
    session = boto3.Session(profile_name=profile_name)
    return session

# 프로파일 선택 화면
@app.route('/')
def index():
    profiles = get_aws_profiles()
    return render_template('index.html', profiles=profiles)

# 리소스 선택 화면
@app.route('/resources', methods=['POST'])
def resources():
    profile = request.form['profile']
    session = create_aws_session(profile)
    
    ec2_instances = get_ec2_instances(session)
    rds_instances = get_rds_instances(session)
    ebs_volumes = get_ebs_volumes(session)
    s3_buckets = get_s3_buckets(session)
    prefix_lists = get_prefix_lists(session)
    vpcs = get_vpcs(session)
    security_groups = get_security_groups(session)
    
    return render_template('resources.html', 
                           ec2_instances=ec2_instances, 
                           rds_instances=rds_instances, 
                           ebs_volumes=ebs_volumes, 
                           s3_buckets=s3_buckets,
                           prefix_lists=prefix_lists,
                           vpcs=vpcs,
                           security_groups=security_groups,
                           profile=profile)

# S3 버킷 내 객체 목록 조회
@app.route('/list_objects/<bucket_name>')
def list_objects(bucket_name):
    session = create_aws_session(request.args.get('profile'))
    s3 = session.client('s3')
    objects = []

    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get('Contents', []):
                objects.append({
                    'Key': obj['Key'],
                    'Size': obj['Size'],
                    'LastModified': obj['LastModified'].isoformat(),
                    'StorageClass': obj['StorageClass']
                })
    except Exception as e:
        print(f"Error listing objects in bucket {bucket_name}: {str(e)}")
        return jsonify({'error': str(e)}), 400

    return jsonify(objects)

@app.route('/get_instances_for_sg/<sg_id>')
def get_instances_for_sg(sg_id):
    profile = request.args.get('profile')
    session = create_aws_session(profile)
    ec2 = session.client('ec2')
    
    try:
        response = ec2.describe_instances(Filters=[{'Name': 'instance.group-id', 'Values': [sg_id]}])
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'InstanceId': instance['InstanceId'],
                    'State': instance['State']['Name'],
                    'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                    'PublicIpAddress': instance.get('PublicIpAddress', 'N/A')
                })
        return jsonify(instances)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/instance_details_page')
def instance_details_page():
    profile = request.args.get('profile')
    session = create_aws_session(profile)
    ec2_instances = get_ec2_instances(session)
    return render_template('instance_details.html', ec2_instances=ec2_instances)

@app.route('/instance_details')
def instance_details():
    instance_id = request.args.get('instanceId')
    profile = request.args.get('profile')

    if not profile:
        return jsonify({'error': 'Profile is required'}), 400

    try:
        session = create_aws_session(profile)
        ec2 = session.client('ec2')

        # 인스턴스 정보 가져오기
        instance_info = ec2.describe_instances(InstanceIds=[instance_id])
        security_groups = instance_info['Reservations'][0]['Instances'][0]['SecurityGroups']
        network_interfaces = instance_info['Reservations'][0]['Instances'][0]['NetworkInterfaces']

        # 보안 그룹 정보 가져오기
        security_group_ids = [sg['GroupId'] for sg in security_groups]
        security_group_info = ec2.describe_security_groups(GroupIds=security_group_ids)

        # 라우팅 테이블 정보 가져오기
        route_table_ids = []
        for ni in network_interfaces:
            if 'Association' in ni and 'RouteTableId' in ni['Association']:
                route_table_ids.append(ni['Association']['RouteTableId'])

        route_table_info = ec2.describe_route_tables(RouteTableIds=route_table_ids)

        result = {
            'security_groups': security_group_info['SecurityGroups'],
            'route_tables': route_table_info['RouteTables']
        }

        return jsonify(result)

    except Exception as e:
        print(f"Error: {str(e)}")  # 서버 로그에 오류 출력
        return jsonify({'error': f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

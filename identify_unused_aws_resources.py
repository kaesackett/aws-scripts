#!/usr/bin/env python

"""Searches AWS for resources that are likely to
be not in use, legacy systems, or decommable (wasting
money!). Outputs an HTML report of its findings."""

import boto3
from jinja2 import Template

def get_regions():
    ec2 = boto3.client('ec2', 'us-east-1')
    resp = ec2.describe_regions(Filters=[{'Name': 'region-name', 'Values': [ '*us*' ]}])

    regions = []

    for endpoint in resp['Regions']:
        regions.append(endpoint['RegionName'])

    return regions


regions = get_regions()
filename = 'unused_resources'

def send_report():
    """Uses AWS SES to send the final HTML report."""

    with open (filename, "r") as output:
        data=output.read()

    client = boto3.client('ses', region_name='us-east-1')
    response = client.send_email(
        Source='sender@website.com',
        Destination={
            'ToAddresses':  ['recipient@website.com'
            ]
        },
        Message={
            'Subject': {
            'Data': 'Unused AWS EC2 Resources'
        },
        'Body': {
            'Html': {
                'Data': data
            }
        }

        }
    )

def save_cost():
    for region in regions:
        # Get EC2 boto3 client for specific region
        client = boto3.client('ec2', region_name=region)

        # Get all Elastic IPs
        response = client.describe_addresses()

        elastic_ips = []
        for address in response['Addresses']:
            if 'InstanceId' not in address:
                elastic_ips.append(address['PublicIp'])

        # Volumes
        response = client.describe_volumes()

        volumes = []
        for volume in response['Volumes']:
            if len(volume['Attachments']) == 0:
                volume_dict = {}
                volume_dict['VolumeId'] = volume['VolumeId']
                volume_dict['VolumeType'] = volume['VolumeType']
                volume_dict['VolumeSize'] = volume['Size']
                volumes.append(volume_dict)

        # Snapshots
        response = client.describe_snapshots()

        snapshots = []
        for snapshot in response['Snapshots']:
            if 'ami' not in snapshot['Description']:
                snapshots.append(snapshot['SnapshotId'])

        # Security Groups - Considered unused if it has not been assigned to any instances
        # Not that big of a deal. They don't cost anything, just make a mess of our console.
        response = client.describe_security_groups()
        all_sec_groups = []

        for SecGroup in response['SecurityGroups']:
            all_sec_groups.append(SecGroup['GroupName'])

        sec_groups_in_use = []
        response = client.describe_instances(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running', 'stopped']
                }
            ])

        for section in response['Reservations']:
            for inst in section['Instances']:
                if inst['SecurityGroups'][0]['GroupName'] not in sec_groups_in_use:
                    sec_groups_in_use.append(inst['SecurityGroups'][0]['GroupName'])

        unused_sec_groups = []
        for groups in all_sec_groups:
            if groups not in sec_groups_in_use:
                unused_sec_groups.append(groups)

        # ELBs
        client = boto3.client('elb', region_name=region)
        response = client.describe_load_balancers()

        elbs = []
        for ELB in response['LoadBalancerDescriptions']:
            if len(ELB['Instances']) == 0:
                elbs.append(ELB['LoadBalancerName'])

        # Autoscaling Groups
        client = boto3.client('autoscaling', region_name=region)
        response = client.describe_launch_configurations()

        LC_list=[]
        for LC in response['LaunchConfigurations']:
            LC_name = LC['LaunchConfigurationName']
            LC_list.append(LC_name)
        response1 = client.describe_auto_scaling_groups()

        for ASG in response1['AutoScalingGroups']:
            if ASG['LaunchConfigurationName'] in LC_list:
                    LC_list.remove(ASG['LaunchConfigurationName'])

        launch_configs = []
        for LC in LC_list:
            launch_configs.append(LC)

        response = client.describe_auto_scaling_groups()

        auto_scaling_groups = []
        for ASG in response['AutoScalingGroups']:
            if ASG['DesiredCapacity'] == 0:
                auto_scaling_groups.append(ASG['AutoScalingGroupName'])

        with open('templates/unused_resources.j2', 'r') as j2_file:
            template = Template(j2_file.read())
            rendered_template = template.render(
                region=region.capitalize(),
                elastic_ips=elastic_ips,
                volumes=volumes,
                snapshots=snapshots,
                unused_sec_groups=unused_sec_groups,
                elbs=elbs,
                launch_configs=launch_configs,
                auto_scaling_groups=auto_scaling_groups)

        # Write out rendered template
        with open('reports/'+"{0}_{1}.html".format(filename, region), 'w') as output:
            output.write(rendered_template)

if __name__ == "__main__":
    try:
        save_cost()
        #send_report()
    except Exception as err:
        print(err)

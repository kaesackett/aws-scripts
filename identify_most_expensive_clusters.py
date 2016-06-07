#!/usr/bin/env python

"""Script to identify the most expensive clusters in AWS
and return a table of results, listing them from most to
least expensive. Useful for making informed decisions
about purchasing reserved instances.

Pass command-line arguments to tailor output.
This script supports execution with both Python 2 and 3."""

import boto3, re

from optparse import OptionParser
from terminaltables import SingleTable

# Option Parser (allows custom output)
parser = OptionParser()
parser.add_option("-r", "--results", type="int", dest="results",
                  help="The number of results you'd like output.", default=10)
options, args = parser.parse_args()

# Map instance sizes to their hourly costs
sizes = {
    # Instance Type     # Hourly cost (USD)
    "x1.32xlarge"   :   13.338,
    "i2.8xlarge"    :   6.82,
    "d2.8xlarge"    :   5.52,
    "i2.4xlarge"    :   3.41,
    "d2.4xlarge"    :   2.76,
    "r3.8xlarge"    :   2.66,
    "g2.8xlarge"    :   2.60,
    "m4.10xlarge"   :   2.394,
    "i2.2xlarge"    :   1.705,
    "c3.8xlarge"    :   1.68,
    "c4.8xlarge"    :   1.675,
    "d2.2xlarge"    :   1.38,
    "r3.4xlarge"    :   1.33,
    "m4.4xlarge"    :   0.958,
    "i2.xlarge"     :   0.853,
    "c3.4xlarge"    :   0.84,
    "c4.4xlarge"    :   0.838,
    "d2.xlarge"     :   0.69,
    "r3.2xlarge"    :   0.665,
    "g2.2xlarge"    :   0.65,
    "m3.2xlarge"    :   0.532,
    "m4.2xlarge"    :   0.479,
    "c3.2xlarge"    :   0.42,
    "c4.2xlarge"    :   0.419,
    "m1.xlarge"     :   0.35,
    "r3.xlarge"     :   0.333,
    "m3.xlarge"     :   0.266,
    "m4.xlarge"     :   0.239,
    "c3.xlarge"     :   0.21,
    "c4.xlarge"     :   0.209,
    "m1.large"      :   0.175,
    "r3.large"      :   0.166,
    "m3.large"      :   0.133,
    "c1.medium"     :   0.13,
    "m4.large"      :   0.12,
    "c3.large"      :   0.105,
    "c4.large"      :   0.105,
    "t2.large"      :   0.104,
    "m1.medium"     :   0.087,
    "m3.medium"     :   0.067,
    "t2.medium"     :   0.052,
    "t2.small"      :   0.026,
    "t1.micro"      :   0.02,
    "t2.micro"      :   0.013,
    "t2.nano"       :   0.0065
}

# Get all EC2 Instance information
ec2 = boto3.client('ec2', 'us-east-1')
response = ec2.describe_instances()

instances = []

# Construct instance dictionary
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instances.append({
            'InstanceId': instance['InstanceId'],
            'InstanceType': instance['InstanceType'],
            'Name': [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'][0]
        })

### Get Top 10 Clusters by Member Count ###
cluster_hosts = []
cluster_size_mapping = {}

# Loop through each instance and see if it matches regex, add cluster name to list
# Create a dictionary that has cluster name keys and mappings
for instance in instances:
    cluster_name  = re.search("^(.*)-[0-9]{1,3}$", instance['Name'])
    if cluster_name:
        cluster_hosts.append(cluster_name.group(1))
        cluster_size_mapping[cluster_name.group(1)] = { 'InstanceType': instance['InstanceType'] }

# Convert to set to get all unique cluster names
unique_clusters = set(cluster_hosts)

# Construct cluster dictionary
# Loop through clusters and get count of members
cluster_counts = [{
        'ClusterName': unique_cluster,
        'MemberCount': cluster_hosts.count(unique_cluster),
        'MemberSize': cluster_size_mapping[unique_cluster]['InstanceType'],
        'MemberCost': sizes[cluster_size_mapping[unique_cluster]['InstanceType']],
        'ClusterCost': sizes[cluster_size_mapping[unique_cluster]['InstanceType']] * cluster_hosts.count(unique_cluster)
    } for unique_cluster in unique_clusters]

# Sort clusters by member count
clusters_sorted_by_count = sorted(cluster_counts, key=lambda k: k['ClusterCost'], reverse=True)[:options.results]

# Construct cluster output table
cluster_table_data = [
    ['Name', 'Member Count', 'Member Size', 'Member Cost (Hour)', 'Cluster Cost (Day)', 'Cluster Cost (Month)', 'Cluster Cost (Year)']
]

# Loop through sorted clusters and add them to output table
for cluster in clusters_sorted_by_count:
    cluster_table_data.append([
        cluster['ClusterName'],
        cluster['MemberCount'],
        cluster['MemberSize'],
        '${: ,.3f}'.format(cluster['MemberCost']),
        '${: ,.2f}'.format(cluster['ClusterCost'] * 24),
        '${: ,.2f}'.format(cluster['ClusterCost'] * 24 * 30),
        '${: ,.2f}'.format(cluster['ClusterCost'] * 24 * 30 * 12)])

# Output table
cluster_table = SingleTable(cluster_table_data, 'Top {} Clusters by Cost'.format(options.results))
print(cluster_table.table)

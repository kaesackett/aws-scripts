#!/usr/bin/python

"""Script to automatically create a DB Snapshot of every
RDS instance in the us-east-1 region. Each time it runs,
the script will also remove all snapshots it created during
its last run (keeps only the most current snapshots)."""

import re
import boto3
import datetime

def snapshot_all_rds_instances():
    """Creates logical snapshots of all RDS instances. Nomenclature: 'auto-<YYYY-MM-DD>-<RDS Instance Identifier>'"""

    client = boto3.client('rds', region_name='us-east-1')
    instances = client.describe_db_instances()

    for instance in instances['DBInstances']:
        response = client.create_db_snapshot(
        DBSnapshotIdentifier='auto-{0}-{1}'.format(str(datetime.date.today()), instance['DBInstanceIdentifier']),
        DBInstanceIdentifier=instance['DBInstanceIdentifier'],
        Tags=[
                {'Key': 'Description',
                'Value': 'Automated DB Snapshot for RDS instance: {0}'.format(instance['DBInstanceIdentifier'])},
            ]
        )

def delete_old_snapshots():
    """Everytime the script runs, clean out the snapshots it created last time it ran."""

    client = boto3.client('rds', region_name='us-east-1')
    snapshots = client.describe_db_snapshots()

    # Affect only the snapshots that were created by this script
    pattern = re.compile("^auto-[0-9]{4}-([0][0-9]|[1][0-2])-([0][0-9]|[1][0-9]|[2][0-9]|[3][0-1])-[a-zA-Z0-9_-]*$")

    for snapshot in snapshots['DBSnapshots']:
        if pattern.match(snapshot['DBSnapshotIdentifier']):
            if snapshot['SnapshotCreateTime'].date() <= datetime.date.today() - datetime.timedelta(days=7):
                response = client.delete_db_snapshot(DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier'])

if __name__ == "__main__":
    try:
        snapshot_all_rds_instances()
        delete_old_snapshots()
    except Exception as err:
        print(err)

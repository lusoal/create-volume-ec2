import boto3
import random
import sys

def list_snapshots(client, tag_value):
    response = client.describe_snapshots(
        Filters=[
            {
                'Name': 'tag:kubernetes.io/created-for/pv/name',
                'Values': [
                    tag_value,
                ]
            },
        ]
    )
    snapshots = response['Snapshots']
    
    snap_id = []
    snap_time = []
    tags = []
    for snap in snapshots:
        snap_id.append(snap['SnapshotId'])
        snap_time.append(snap['StartTime'])
        try:
            tags.append(snap['Tags'])
        except Exception as e:
            print(e)
            tags.append({'Tag':'None'})
        
    position = (max(snap_time))
    position_snap = (snap_time.index(position))
    
    snap_info = {}
    snap_info['Tags'] = tags[position_snap]
    snap_info['ID'] = snap_id[position_snap]
    
    return(snap_info)



def create_volume(client, snap_info, azs):
    az = random.choice(azs)
    print(f"Creating volume using {snap_info['ID']}, in az {az}")
    response = client.create_volume(
        AvailabilityZone=az,
        SnapshotId=snap_info['ID'],
    )
    
    response_tags = client.create_tags(
        Resources=[
            response['VolumeId']
        ],
        Tags=snap_info['Tags']
    )
    
    print(f"Print volume {response['VolumeId']} created!")

def main():
    # Change snapshot tag
    azs = ['sa-east-1a', 'sa-east-1b', 'sa-east-1c']
    region_name = "sa-east-1"
    
    file_pvcs = open(sys.argv[1], "r")
    
    for f in file_pvcs:
        tag_key = (f.strip())
        print(tag_key)
        try: 
            client = boto3.client('ec2', region_name=region_name)
            snap_info = list_snapshots(client, tag_key)
            create_volume(client, snap_info)
        except Exception as e:
            print(e)
            print(f"Error creating volume {tag_key}")
    
if __name__ == '__main__':
    main()
    
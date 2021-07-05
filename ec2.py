import boto3
import time
from datetime import datetime
import time
import sys
from botocore import config
from botocore.config import Config

# sts = boto3.client('sts')
# print(sts.get_caller_identity())

current_config = Config(
    region_name = sys.argv[2],
)


def send_termination_notification(instance_id):

    AWS_ACCOUNT_ID={'HVDSDMLAB':463423328685,'OPIS Control':218790088255,'OPIS Prod':530888451175,'OPIS PreProd':253049054146}
    AWS_ACCOUNT_REGION=sys.argv[2]
    TOPIC_NAME="bt3_topic"
    sns = boto3.client('sns',config=current_config)
    response = sns.publish(
        TopicArn='arn:aws:sns:'+AWS_ACCOUNT_REGION+":"+str(AWS_ACCOUNT_ID[sys.argv[1]])+":"+TOPIC_NAME,
        Message="REAN Cloud automation is terminatinng " + instance_id+" as it was running for more than than permitted time",
        Subject='[!] INSTANCE TERMINATION NOTIFICATION',
    )


ec2 = boto3.client('ec2',config=current_config)
response = ec2.describe_instances()
# print(response)

for groups in response["Reservations"]:
    for instances in groups["Instances"]:
        instance_id=instances["InstanceId"]
        if instances["State"]["Name"]=="terminated" or instances["State"]["Name"]=="shutting-down":
            print(instances["State"]["Name"])
            print(instance_id+" is terminated or is shutting down; no action required")
        else:
            print(instances["State"]["Name"])
            print(instance_id+" is not terminated; checking for termination tags")
            tag_response=ec2.describe_tags(
                Filters=[
                    {
                        'Name': 'resource-type',
                        'Values': [
                            'instance',
                        ]
                    }, 
                    {
                        'Name': 'resource-id',
                        'Values': [
                            instance_id,
                        ]  
                    },
                ]
            )
            tag_keys=[]
            tag_keys=[tag_description['Key']  for tag_description in tag_response["Tags"]]
            if "termination-date" in tag_keys :
                print("     termination-date tag is present:)")
                if time.strptime(tag_response["Tags"][tag_keys.index("termination-date")]["Value"],"%d-%m-%Y") < time.strptime(datetime.now().strftime("%d-%m-%Y"), "%d-%m-%Y"):
                    print("YOUR INSTANCE HAS BEEN RUNNING FOR MORE THAN THE PERMITTED TIME, HENCE TERMINATING IT, happy cloud computing:)")
                    send_termination_notification(instance_id)
                    response = ec2.terminate_instances(
                        InstanceIds=[
                            instance_id,
                        ],
                    )
                elif time.strptime(tag_response["Tags"][tag_keys.index("termination-date")]["Value"],"%d-%m-%Y") > time.strptime(datetime.now().strftime("%d-%m-%Y"), "%d-%m-%Y"):
                    break
            else:
                print("     termination-date not present,adding tag")
                create_tag_response=ec2.create_tags(
                    Resources=[
                    instance_id,
                    ],
                    Tags=[
                        {
                            'Key': 'termination-date',
                            'Value': str(datetime.now().strftime("%d-%m-%Y"))
                        },
                    ]           
                )
            if "termination-time" in tag_keys:
                print("     termination-time tag is present:)")
                if time.strptime(tag_response["Tags"][tag_keys.index("termination-time")]["Value"],"%H-%M-%S") <= time.strptime(datetime.now().strftime("%H-%M-%S"), "%H-%M-%S"):
                    print("YOUR INSTANCE HAS BEEN RUNNING FOR MORE THAN THE PERMITTED TIME, HENCE TERMINATING IT, happy cloud computing:)")
                    send_termination_notification(instance_id)
                    response = ec2.terminate_instances(
                        InstanceIds=[
                            instance_id,
                        ],
                    )
                elif time.strptime(tag_response["Tags"][tag_keys.index("termination-time")]["Value"],"%H-%M-%S") > time.strptime(datetime.now().strftime("%H-%M-%S"), "%H-%M-%S"):
                    break
            else:
                print("     termination-time not present,adding tag")
                create_tag_response=ec2.create_tags(
                    Resources=[
                    instance_id,
                    ],
                    Tags=[
                        {
                            'Key': 'termination-time',
                            'Value': str(datetime.now().strftime("%H-%M-%S"))
                        },
                    ]           
                )

from __future__ import print_function
import logging
import json
import boto3
import inspect
import pprint
import sys


config = { "dns_zone_public" : "XXXXXXXXXXX", "dns_zone_private" : "XXXXXXXXXXX" } 

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#AWS API
def get_instance_detail(instance_id):
    client = boto3.client('ec2')    
    return client.describe_instances(
        DryRun=False,
        InstanceIds=[
            instance_id,
        ]
    )['Reservations'][0]['Instances'][0]

#DNS MANAGE
def update_dns(fqdn, ip, hostedZoneId):
    logger.debug("updating dns name=" + fqdn + " ip=" + ip + " hostedZoneId=" + hostedZoneId)
    client = boto3.client('route53')
    response = client.change_resource_record_sets(
        HostedZoneId = hostedZoneId,
        ChangeBatch={
            'Comment': 'comment',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': fqdn,
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': ip
                            },
                            ],
                        }
                },
                ]
        }
    )


#TAG FUNCTIONS
def TAG_DNS_PUBLIC(tag, instance_detail):
    logger.debug(tag['Key'])
    public_ip = instance_detail['PublicIpAddress']
    update_dns(tag['Value'], public_ip, config['dns_zone_public'])

def TAG_DNS_PRIVATE(tag, instance_detail):    
    logger.debug(tag['Key'])
    private_ip = instance_detail['PrivateIpAddress']
    update_dns(tag['Value'], private_ip, config['dns_zone_private'])


                
#EXEC TAG
def exec_tag(tag, instance_detail):
    buildin_functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    all_functions = dict(buildin_functions)
    tag_functions = {}
    for key in all_functions.keys():
        if key.startswith('TAG_'):
            tag_functions[key] = all_functions[key]    
    #print("TAG=" + tag)
    tag_name = tag['Key']
    method_name = "TAG_" + tag_name
    if method_name in tag_functions:
        method = tag_functions[method_name]
        if not method:
            print("Method %s not implemented" % tag_name)
        else:
            method(tag, instance_detail)
    else:
        print ("No function for TAG=" + tag_name)

def lambda_handler(event, context):
#    logger = logging.getLogger()
#    logger.setLevel(logging.DEBUG)
    logger.debug('Loading function TAG SET')
    logger.debug('got event{}'.format(event))
    
    if event["detail"]["state"] == "running":    
        instance_detail = get_instance_detail(event["detail"]["instance-id"])
        logger.debug('got response{}'.format(instance_detail))
        for tag in instance_detail['Tags']:
            exec_tag(tag, instance_detail)                    
   
    return 1
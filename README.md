# AWS_set_by_tag
Configure multiple AWS options automatically by taging your EC2 instances 

## Setup

1. Create Lambda function with AWS_set_by_tag.py contents (replace priv and pub DNS zones with zones from route53)
2. In Cloudwatch add a role that cals this Lambda function whenewer EC2 instance changes it's state (you can also call it on specific state changes) 

## How it works 
Whenewer instance changes state (ex. is started or restarted ) this lambda will walk through all instance TAGS and execute functions called TAG_<tag key>

### Example 
If you add a tak to EC2 instance named DNS_PRIVATE with alue "test.example.com" then on every instance start Lmmbda will update "test.example.com" entry in Route53 DNS with instance private IP , Same can be done with public IP with TAG DNS_PUBLIC


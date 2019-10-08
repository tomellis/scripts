import boto3
import json

client = boto3.client('servicediscovery')
response = client.list_instances(
            ServiceId='srv-sq5x7pbscwojdhay',
            MaxResults=5
            )

x = json.dumps(response)
y = json.loads(x)

for item in y['Instances']:
    instance_ip = item['Attributes']['AWS_INSTANCE_IPV4']
    instance_port = item['Attributes']['AWS_INSTANCE_PORT']
    print(instance_ip + ":" + instance_port)

#print("\n ###Debug###")
#print(y)

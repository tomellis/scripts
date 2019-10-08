import dns.resolver
query = dns.resolver.query('ecs-lab-api.local', 'SRV')
for result in query:
    print str(result)

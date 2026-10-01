# Blackhole pattern checklist

Write a negative test for each that applies to your system.

## Routing
- [ ] Route to a cluster/upstream that does not exist in the snapshot
- [ ] Upstream exists but has zero healthy endpoints
- [ ] Weighted routing where all weights are 0
- [ ] Catch-all route (`/` or `*`) placed before specific routes, shadowing them
- [ ] Two services claim the same host + path prefix
- [ ] Path rewrite produces an empty or double-slash path

## DNS / certificates
- [ ] CNAME to a hostname that does not resolve
- [ ] Record points to a load balancer in a different account/region than intended
- [ ] TTL so high that rollback takes hours
- [ ] Hostname requested without a matching certificate (SAN) available
- [ ] Certificate expiring within N days

## Listeners / network
- [ ] Two listeners bind the same port
- [ ] Security group or firewall change removes the edge's ingress
- [ ] Health check path that always fails (e.g. requires auth)

## Context / render
- [ ] Context source unavailable -> renders empty route/cluster list
- [ ] Template variable missing -> renders empty string instead of failing
- [ ] Diff deletes more than X% of routes in one change

## Ownership
- [ ] User modifies a hostname or route owned by another team
- [ ] User removes the last route to a production service

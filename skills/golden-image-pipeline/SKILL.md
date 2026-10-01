---
name: golden-image-pipeline
description: Use when building or reviewing how a fleet of servers or proxies is built and deployed - Packer images, Salt/Ansible/Puppet configuration, AMIs, CloudFormation/Terraform stacks, or multi-region rollouts. Produces immutable golden images and wave-based IaC deployments with rollback.
---

# Golden Image Pipeline

## Overview

Build once, deploy everywhere, never patch in place.

```
base image ─> temp build VM ─> config mgmt (Salt/Ansible) ─> tests ─> snapshot = golden image (vN)
                                                                          │
IaC stack (VPC, subnets, SG, IAM, ASG, NLB, certs, DNS) ─ references vN ─> wave 1 region ─> wave 2 ... ─> all regions
```

In the source talk: Packer launches a temporary EC2 instance in a dev account,
SaltStack declaratively installs the Envoy proxy, logging agent, security hardening,
network (kernel) tuning, and observability agents, then the instance is snapshotted
into an AMI. CloudFormation then rolls that AMI out to 2,000+ proxies across 13 regions.

## When to Use

- Hosts are configured by SSH, ad-hoc scripts, or drift over time
- A fleet must run in many regions/accounts with identical configuration
- You need fast, safe rollback of OS/agent/proxy versions

## Process

1. **Declare the image contents** as config-management state (Salt states, Ansible
   roles), split into layers: runtime (proxy binary + config bootstrap), logging,
   observability, security hardening, network tuning.
2. **Build with Packer** from a pinned base image. Never use `latest` tags for base
   images or packages; pin versions so builds are reproducible.
3. **Test the image before publishing.** Boot it, run smoke tests (proxy starts,
   agents report, hardening checks pass e.g. CIS benchmark subset, sysctl values set).
   Fail the pipeline on any test failure.
4. **Version and tag.** Image name includes version + git SHA. Record the image ID per
   region in a manifest the IaC reads.
5. **Define infra as code.** One parameterized stack per region: network (VPC,
   subnets, IGW), security (SGs, IAM roles), compute (launch template + ASG pointing at
   the image), traffic (NLB, listeners, certificates, DNS records).
6. **Roll out in waves.** canary (1 AZ / small %) -> one region -> low-traffic regions
   -> remaining regions. Gate each wave on health metrics (5xx rate, latency, connection
   errors), not just "stack update complete".
7. **Roll back by redeploying the previous image ID**, never by patching hosts.

See `references/packer-salt-skeleton.md` for starter files.

## Red Flags

- Anyone has SSH'd into a production proxy to "quickly fix" something
- The image build installs from unpinned package repos
- All regions update in one stack operation
- Rollback plan is "fix forward"
- Secrets baked into the image (fetch at boot from a secret store instead)

## Common Mistakes

- Putting environment-specific config in the image; keep the image generic and inject
  environment at boot (user data / control plane)
- Skipping network tuning (file descriptors, conntrack, somaxconn) on proxy hosts
- Not deleting temporary build instances and old images (cost leak)

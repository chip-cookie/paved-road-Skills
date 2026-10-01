# Starter skeleton: Packer + Salt golden image

## `proxy.pkr.hcl`

```hcl
packer {
  required_plugins {
    amazon = { source = "github.com/hashicorp/amazon", version = ">= 1.3.0" }
  }
}

variable "version" { type = string }
variable "git_sha" { type = string }

source "amazon-ebs" "proxy" {
  region        = "us-east-1"
  instance_type = "c6i.large"
  ssh_username  = "ec2-user"
  ami_name      = "edge-proxy-${var.version}-${var.git_sha}"
  source_ami_filter {
    filters     = { name = "al2023-ami-2023.*-x86_64" }   # pin tighter in production
    owners      = ["amazon"]
    most_recent = true
  }
  ami_regions = ["us-west-2", "eu-west-1", "ap-northeast-2"]   # copy to rollout regions
  tags = { Version = var.version, GitSha = var.git_sha }
}

build {
  sources = ["source.amazon-ebs.proxy"]

  provisioner "salt-masterless" {
    local_state_tree = "./salt"
    skip_bootstrap   = false
  }

  provisioner "shell" { script = "tests/smoke.sh" }   # fail build on non-zero exit
}
```

## `salt/top.sls`

```yaml
base:
  '*':
    - proxy        # envoy binary + systemd unit + bootstrap pointing at control plane
    - logging      # log shipper agent
    - observability
    - hardening    # CIS subset, ssh lockdown, auditd
    - net_tuning   # sysctl: somaxconn, conntrack, file-max, tcp buffers
```

## `salt/net_tuning/init.sls`

```yaml
net.core.somaxconn:            { sysctl.present: [{ value: 65535 }] }
net.netfilter.nf_conntrack_max: { sysctl.present: [{ value: 1048576 }] }
fs.file-max:                   { sysctl.present: [{ value: 2097152 }] }
```

## `tests/smoke.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
systemctl is-enabled envoy
envoy --version
[ "$(sysctl -n net.core.somaxconn)" -ge 65535 ]
! grep -q '^PermitRootLogin yes' /etc/ssh/sshd_config
```

## Rollout waves (example)

| Wave | Scope | Gate |
|------|-------|------|
| 0 | 1 ASG instance in 1 AZ, 1 region | 30 min, 5xx < baseline + 0.1% |
| 1 | Full canary region | 1 h, p99 latency within 5% |
| 2 | Low-traffic regions | 2 h |
| 3 | Remaining regions, 2 at a time | per-region health |

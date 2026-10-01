---
name: edge-architecture-review
description: Use when reviewing or designing a platform, infrastructure, or edge/proxy architecture - self-service provisioning, load balancers, API gateways, proxies, config control planes, or fleet rollouts. Runs a structured review against six edge-platform principles and routes to the detailed skill for each gap.
---

# Edge Architecture Review

## Overview

A checklist-driven review for internal platforms that sit in front of many services
(load balancers, proxies, gateways, provisioning APIs). It distills six principles from
a large-scale edge migration: an async self-service broker, a template/context config
control plane, golden-image fleet builds, centralized cross-cutting concerns, input
guardrails, and churn-aware maintenance.

**Core principle:** A platform is good when product teams can provision safely without
talking to the platform team, and a bad input cannot take traffic down.

## When to Use

- Someone shares a design doc, RFC, diagram, or repo for a platform/infra component
- "Should we build our own LB / gateway / proxy layer?"
- Migrating many services behind a shared edge
- Before a large rollout (many regions, many hosts)

Do NOT use for: single-service application code reviews with no infra surface.

## Process

Work through the six lenses **in order**. For each, record: current state, gap, severity
(blocker / major / minor), and the follow-up skill.

| # | Lens | Key question | Follow-up skill |
|---|------|--------------|-----------------|
| 1 | Self-service | Can a product team provision without a ticket? Is long work async with pollable status? | `async-provisioning-broker` |
| 2 | Dynamic config | Can config change at runtime without restarts? Is it rendered from templates + context, not hand-edited? | `template-context-config` |
| 3 | Fleet build | Are hosts built from a versioned golden image and deployed via IaC? Can you roll out by wave and roll back? | `golden-image-pipeline` |
| 4 | Shift-left | Are authn/authz/rate-limit/access-logs/DoS handled once at the edge, not re-implemented per service? | `edge-sidecar-offload` |
| 5 | Guardrails | Can any user input produce a config that drops or misroutes traffic? | `guardrail-validation` |
| 6 | Maintainability | Where does the code churn most? Is complexity growing there? | `churn-hotspot-refactor` |

### Step-by-step

1. **Map the system.** List entry points, data stores, queues, config sources, and
   which team owns each. Draw the request path (client → edge → service) and the
   provisioning path (developer → API → worker → infra).
2. **Apply each lens.** Ask the key question. Cite the file, diagram box, or doc line
   that answers it. If nothing answers it, that is a finding.
3. **Find the blast radius.** For every finding, state what breaks and for whom if it
   goes wrong (one service? one region? all traffic?).
4. **Rank.** Blockers = can drop production traffic or leak access. Majors = forces
   manual toil or tickets. Minors = cost or ergonomics.
5. **Route.** For each blocker/major, name the follow-up skill and the first concrete step.

## Output Format

```markdown
## Edge Architecture Review: <system>

### System map
<request path, provisioning path, owners>

### Findings
| # | Lens | Finding | Evidence | Blast radius | Severity | Next step (skill) |

### Top 3 actions
1. ...
```

## Red Flags

- "Just file a ticket with the infra team" is the provisioning path
- Proxy/LB config changes require a restart or a full redeploy
- Hosts are patched in place (SSH, manual installs) instead of rebuilt from an image
- Every service has its own auth middleware copy
- The API accepts free-form config fragments with no semantic validation
- Nobody can name the three files that change most often

## Common Mistakes

- Reviewing only the happy path. Always ask "what does a typo in this field do?"
- Treating cost savings as the goal. Cost follows from self-service + shared concerns;
  review those, not the invoice.
- Recommending a rewrite. Prefer the smallest change that closes a blocker.

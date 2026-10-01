---
name: template-context-config
description: Use when proxy, load balancer, gateway, or other runtime config is hand-edited, duplicated across environments, or needs a restart to apply. Builds a control plane that renders config from templates plus dynamic context, validates it, and pushes it live (e.g. Envoy xDS) without restarts.
---

# Template + Context Config Control Plane

## Overview

Complex runtime config (Envoy clusters/routes/listeners, NGINX upstreams, gateway
routes) should not be written by hand. Split it into:

- **Templates** - the shape of the config, owned and reviewed by the platform team
- **Context** - dynamic facts pulled at render time (service registry, DynamoDB/S3
  records, secrets refs, region, environment)
- **Parameters** - the small set of values a developer is allowed to choose

```
templates (git) ─┐
context (DB/S3) ─┼─> render ─> validate ─> diff ─> push (xDS / hot reload) ─> proxies
params (API)    ─┘                 └─ reject: keep last-known-good
```

The source talk's implementation is **Sovereign**, an open-source Envoy management
server (bitbucket.org/atlassian/sovereign). Use it, or another xDS server
(go-control-plane, java-control-plane), before writing your own.

## When to Use

- Proxy config is copy-pasted per service or per environment
- Config changes need a process restart or full redeploy
- Developers ask the platform team to edit config on their behalf

## Process

1. **Inventory the config.** List every config object type and which fields actually
   vary between instances. Fields that never vary belong in the template; fields that
   vary by environment belong in context; fields a developer chooses are parameters.
   Aim for the smallest parameter surface possible.
2. **Write templates with a strict engine.** Jinja2/Go templates with undefined
   variables set to error (`StrictUndefined`, `missingkey=error`). No business logic
   beyond loops and simple conditionals.
3. **Define context sources with freshness rules.** For each source: where it lives,
   how often it refreshes, and what happens if it is unreachable (use cached value +
   alert; never render with empty context).
4. **Validate the rendered output, not just the inputs.** Schema-validate against the
   proxy's real schema (e.g. Envoy protobufs / `envoy --mode validate`), then run
   semantic checks from `guardrail-validation` (every route has a live cluster, no
   duplicate listeners, TLS certs exist).
5. **Diff before push.** Compute the diff against what proxies currently run. Log it.
   Large diffs (e.g. >N% of routes changed) require explicit approval.
6. **Push dynamically.** Use the proxy's dynamic API (Envoy xDS: CDS/EDS/LDS/RDS) or
   a hot-reload path. Version every snapshot so you can roll back to the previous one.
7. **Keep last-known-good.** If render or validation fails, proxies keep the previous
   version; the control plane alerts. A bad render must never become an empty config.

See `references/render-pipeline.md` for a minimal Python sketch.

## Red Flags

- Templates contain `if service == "jira"` style special cases (move to context)
- Missing context renders as an empty list, which proxies interpret as "no routes"
- Only input parameters are validated; rendered output is pushed unchecked
- No version numbers on pushed snapshots

## Common Mistakes

- Exposing raw config fragments as a "parameter" - that is not an abstraction
- Rendering per request instead of per change (cache by input hash)
- Coupling the control plane's uptime to the data plane: proxies must keep serving
  their last config if the control plane is down

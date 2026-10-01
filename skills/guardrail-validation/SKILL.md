---
name: guardrail-validation
description: Use when a self-service API, CLI, or config file lets users change routing, DNS, load balancer, proxy, or other traffic-affecting settings. Builds layered validation so no user input can render a config that blackholes, misroutes, or exposes traffic.
---

# Guardrail Validation (No Traffic Blackholes)

## Overview

An abstraction is only as safe as the validation behind it. If a typo in a hostname
or an empty list can render a valid-looking config that drops traffic, the platform
has a blackhole. Validate in layers, fail closed, and test the guardrails themselves.

## When to Use

- Building or reviewing any endpoint/CLI that changes how traffic is routed
- A past incident was caused by "valid but wrong" config
- Adding a new parameter to a platform abstraction

## The Five Layers

Apply all five. Each layer catches what the previous cannot.

| Layer | Checks | Example rejection |
|-------|--------|-------------------|
| 1. Syntax / schema | types, formats, required fields, enum values | `origin` is not a hostname |
| 2. Semantic | values make sense together | `weight` sums to 0; TLS on but no cert |
| 3. Referential | referenced things exist and are healthy *now* | upstream cluster has 0 healthy endpoints |
| 4. Ownership / policy | caller may touch this resource | hostname belongs to another team |
| 5. Rendered-output | the final config, after templating | a route points to a cluster not in the snapshot |

Then **impact analysis**: compute what share of traffic/routes changes. Above a
threshold, require approval or a staged rollout.

## Process

1. **List every user-supplied field.** For each, write its allowed values and the worst
   thing a wrong value could do. That list is your test plan.
2. **Minimize the surface.** Can a field be derived instead of supplied? Can a free-form
   string become an enum? Every field removed is a class of incident removed.
3. **Implement layers 1-4 at the API edge** (before enqueue - see
   `async-provisioning-broker`), and **layer 5 in the control plane** (after render - see
   `template-context-config`).
4. **Return actionable errors**: field, value, rule, how to fix.
5. **Write negative tests first.** For every "worst thing" from step 1, a test proving
   the input is rejected. Keep a regression test for every past incident.
6. **Fail closed.** If a validator cannot run (dependency down), reject the change
   rather than skipping the check.

See `references/blackhole-checklist.md` for common blackhole patterns to test.

## Red Flags

- Validation is only a JSON schema
- "We validate in the UI" (the API is the contract; the UI is optional)
- Validators that silently pass when a lookup fails
- No tests that assert rejections

## Common Mistakes

- Validating inputs but not the rendered output
- Checking that a target exists but not that it is healthy
- Treating guardrails as friction to remove instead of the product's main safety feature

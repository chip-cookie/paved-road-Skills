---
name: edge-sidecar-offload
description: Use when many services each re-implement authentication, authorization, rate limiting, access logging, or DoS protection, or when designing an API gateway, edge proxy, or sidecar layer. Decides what to centralize at the edge vs. a sidecar vs. the service, and defines the trust contract between them.
---

# Edge & Sidecar Offload (Shift-Left)

## Overview

Cross-cutting concerns should be solved **once**, as early in the request path as
possible, so product teams only write business logic.

```
client ─> CDN/WAF (DoS, geo, bot) ─> edge proxy (TLS, access log, routing)
                                        ├─ authn sidecar   (who are you?)
                                        ├─ authz sidecar   (may you do this?)
                                        └─ ratelimit sidecar
                                     ─> service (trusts verified identity headers)
```

In the source talk, Envoy ran with local sidecar containers on the same host/pod:
authentication (written in Rust), authorization and rate limiting (contributed by other
internal teams). Access logging used an Envoy network filter; DoS protection sat in
front via CloudFront.

## When to Use

- You find the same auth/rate-limit middleware copied across services
- Onboarding a service requires each team to integrate auth themselves
- Designing an API gateway or service mesh rollout

## Process

1. **Inventory concerns per service.** For each service, list how it does authn,
   authz, rate limiting, access logs, request size limits, and CORS. Duplication is the
   case for centralizing.
2. **Place each concern using this rule:**

   | Concern | Place | Why |
   |---------|-------|-----|
   | Volumetric DoS, bot, geo | CDN/WAF in front of edge | Cheapest place to drop traffic |
   | TLS termination, access logs | Edge proxy | Uniform format, one pipeline |
   | Authentication | Edge (ext_authz / sidecar) | Identity is service-agnostic |
   | Coarse authorization (can call this API?) | Edge sidecar | Policy is centralizable |
   | Fine-grained authz (can edit *this* object?) | Service | Needs domain data |
   | Rate limiting (per client/tenant) | Edge sidecar with shared counter store | Global view of traffic |
   | Business validation | Service | Domain logic |

3. **Define the trust contract.** The edge strips any incoming identity headers from
   clients, then sets verified ones (e.g. `x-auth-subject`, `x-auth-tenant`, or a
   signed internal JWT). Services must only accept traffic from the edge (network
   policy / mTLS) and must trust only those headers.
4. **Choose fail-open vs fail-closed per concern, explicitly.** Authn/authz: fail
   closed. Rate limiting: usually fail open with alerting. Write it down.
5. **Keep sidecars local.** Run them on the same host/pod (localhost / Unix socket) to
   keep latency low; set tight timeouts on the proxy-to-sidecar call.
6. **Migrate service by service** behind the edge, comparing before/after auth decisions
   in shadow mode before enforcing.

## Red Flags

- Services read identity from headers the client can set directly
- Services are reachable without going through the edge
- Authz sidecar needs to query every service's database (it is doing fine-grained authz;
  move that back to the service)
- No defined behavior when a sidecar is down

## Common Mistakes

- Centralizing everything, including domain-specific authorization
- Ignoring the edge's own blast radius: it now fronts everything, so it needs the
  strongest guardrails (`guardrail-validation`) and wave rollouts (`golden-image-pipeline`)

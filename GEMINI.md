# paved-road

This extension provides agent skills for designing and reviewing self-service
edge/platform infrastructure. Activate the matching skill when a task fits:

- `edge-architecture-review` - review a platform/proxy/gateway design end to end (start here)
- `async-provisioning-broker` - API -> queue -> worker -> state store -> polling
- `template-context-config` - render runtime config from templates + context, validate, push without restart
- `golden-image-pipeline` - Packer + config management golden images, wave-based IaC rollout
- `edge-sidecar-offload` - centralize authn/authz/rate limiting/logging at the edge or in sidecars
- `guardrail-validation` - layered validation so user input cannot blackhole traffic
- `churn-hotspot-refactor` - find churn x complexity hotspots in git history and plan refactors

# Source notes

Summary of the public YouTube video (May 2026) the skills are based on, and how each section maps to a skill. The speaker described it as architectural patterns and public tools, not internal source code or data.

**Speaker:** Vasilios Syrakis (8 years as a developer at Atlassian)

| Video section | Key points | Skill |
|--------------|-----------|-------|
| 1. Background & goals | Replace costly, license-bound enterprise load balancers with the open-source Envoy proxy; build a self-service platform so developers provision LB resources without the infra team | `edge-architecture-review` |
| 2. Open Service Broker | Python API (Flask -> FastAPI; started with connexion, an OpenAPI-spec route generator). Client sends JSON -> API enqueues to SQS -> worker provisions DNS / CloudFront / external APIs -> writes state to DynamoDB -> client polls | `async-provisioning-broker` |
| 3. Envoy control plane (Sovereign) | Templates + context model for clusters/routes/listeners; dynamic data from DynamoDB/S3 combined with developer parameters, validated, rendered, pushed without proxy restarts. Open source on Bitbucket | `template-context-config` |
| 4. Infra automation | Packer + SaltStack on a temporary EC2 build instance: Envoy, logging agent, hardening, network tuning, observability -> golden AMI. CloudFormation deploys 2,000+ proxies in 13 regions (VPC, subnets, IGW, SG, IAM, ASG, NLB, ACM, Route 53) | `golden-image-pipeline` |
| 5. Central edge & sidecars | Jira, Confluence, Bitbucket and other services migrated behind the edge. Shift-left: DoS defense (CloudFront), access logging (Envoy network filter). Sidecars on the same host: authn (written in Rust by the speaker), authz and rate limiting (other internal teams). Result: product teams focus on business logic; large cost savings and faster delivery | `edge-sidecar-offload` |
| 6. Maintenance philosophy | Strict validation of user parameters to prevent traffic blackholes; linting and churn management - find where code changes most and keep complexity from growing there | `guardrail-validation`, `churn-hotspot-refactor` |

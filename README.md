# Paved Road

[한국어 README](README.ko.md) · MIT License

**Paved Road** is a skill pack for coding agents that design, build, and review
**self-service platform infrastructure**: load balancers, proxies, API gateways,
provisioning APIs, and the fleets behind them.

It works in **Claude Code, Codex CLI, and Gemini CLI** from the same `skills/` folder,
and in any other agent that reads the `SKILL.md` format.

In platform engineering, a *paved road* (or golden path) is the supported, well-lit
route that product teams can follow without asking the platform team for help. These
skills teach your agent how to build one.

---

## How it works

Each skill is a folder with a `SKILL.md`: a short description that tells the agent
**when** to use it, plus a step-by-step process, red flags, and an output format.

1. When you start a session, the agent only loads each skill's name and description
   (a few hundred tokens in total).
2. When your request matches a description ("review this gateway design", "where is
   our tech debt?"), the agent loads that skill's full instructions and follows them.
3. Long examples and scripts live in `references/` and `scripts/` and are read only
   when needed.

You can also call any skill by name (see [Usage](#usage)).

## Skills

| Skill | Use it when |
|-------|-------------|
| `edge-architecture-review` | Reviewing a platform, proxy, or gateway design end to end. **Start here.** It checks six lenses and points to the skills below |
| `async-provisioning-broker` | Building a self-service API whose work is slow or can fail (API -> queue -> worker -> state store -> polling) |
| `template-context-config` | Runtime config is hand-edited or needs restarts. Render it from templates + context, validate it, and push it live |
| `golden-image-pipeline` | Building a fleet: Packer + Salt/Ansible golden images and wave-based multi-region IaC rollouts |
| `edge-sidecar-offload` | Every service re-implements auth, rate limiting, or logging. Move them to the edge or sidecars |
| `guardrail-validation` | Users can change routing, DNS, or LB settings. Make sure no input can blackhole traffic |
| `churn-hotspot-refactor` | Finding where tech debt actually costs you (git churn x complexity), with a bundled script |

---

## Installation

Pick your agent. Each method installs all 7 skills.

### Claude Code

Inside a Claude Code session:

```text
/plugin marketplace add chip-cookie/paved-road-Skills
/plugin install paved-road@paved-road
```

Or from your terminal:

```bash
claude plugin marketplace add chip-cookie/paved-road-Skills
claude plugin install paved-road@paved-road
```

**Verify:**

```bash
claude plugin details paved-road
```

The `Component inventory` should list `Skills (7)`. Start a new session (or run
`/reload-plugins`) to load them.

### Codex CLI

From your terminal:

```bash
codex plugin marketplace add chip-cookie/paved-road-Skills
codex plugin add paved-road@paved-road
```

Or, inside Codex, run `/plugins`, search for **Paved Road**, and install it.

**Verify:**

```bash
codex plugin list
```

`paved-road@paved-road` should show `installed, enabled`. Inside Codex, `/skills`
lists the 7 skills.

> Prefer plain skill folders instead of a plugin? Use the [install script](#manual-install-any-agent).

### Gemini CLI

```bash
gemini extensions install https://github.com/chip-cookie/paved-road-Skills
```

Gemini CLI asks you to confirm the install (add `--consent` to skip the prompt).

**Verify:**

```bash
gemini skills list
```

Or run `/skills list` inside Gemini CLI.

Gemini CLI asks for your permission the first time a skill activates in a session.

### Manual install (any agent)

Clone once, then let the script symlink the skills into each agent's folder:

```bash
git clone https://github.com/chip-cookie/paved-road-Skills ~/.paved-road
~/.paved-road/scripts/install.sh
```

| Option | What it does |
|--------|--------------|
| *(none)* | Installs for all agents, for your user, as symlinks |
| `--agent claude` / `codex` / `gemini` | Installs for one agent only |
| `--scope project` | Installs into the current project instead of your home folder |
| `--copy` | Copies files instead of symlinking |
| `--uninstall` | Removes what the script installed |

Where the skills end up:

| Agent | User scope | Project scope |
|-------|-----------|---------------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex CLI | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.agents/skills/` (shared with Codex) | `.agents/skills/` |

Codex CLI and Gemini CLI both read `~/.agents/skills`, so one install covers both.

For other agents that support `SKILL.md` (Cursor, OpenCode, and others), copy the
folders under `skills/` into that agent's skills directory.

---

## Usage

### Let the agent pick

Just describe the task. For example:

```text
Here's our design doc for a new internal load balancer service. Review it.
```

The agent matches the request to `edge-architecture-review` and follows it.

### Call a skill by name

| Agent | How |
|-------|-----|
| Claude Code | `/paved-road:edge-architecture-review` (any skill: `/paved-road:<skill>`) |
| Codex CLI | `$edge-architecture-review`, or pick it from `/skills` |
| Gemini CLI | Mention the skill name in your prompt, e.g. "use guardrail-validation" |
| Manual install (Claude Code) | `/edge-architecture-review` |

### Example prompts

```text
Review docs/edge-design.md with edge-architecture-review and give me the top 3 actions.

I need a self-service API that creates DNS records and CDN distributions.
Design it with async-provisioning-broker, using FastAPI, SQS, and DynamoDB.

Our NGINX config is copy-pasted for every service. Use template-context-config
to plan how to render it from templates instead.

Write a Packer + Ansible pipeline for our proxy hosts with golden-image-pipeline,
and a rollout plan for 4 regions.

Every service has its own JWT middleware. Use edge-sidecar-offload to plan moving
authentication to the gateway.

Here is our routing API schema. Run guardrail-validation and list every input
that could blackhole traffic.

Run churn-hotspot-refactor on this repo and give me the top 3 refactor targets.
```

### Suggested flow

```
edge-architecture-review  ->  finds gaps, ranks them
        |
        +-> async-provisioning-broker   (self-service is ticket-based or synchronous)
        +-> template-context-config     (config is hand-edited / needs restarts)
        +-> golden-image-pipeline       (hosts are patched in place)
        +-> edge-sidecar-offload        (auth/rate limits duplicated per service)
        +-> guardrail-validation        (bad input can break routing)
        +-> churn-hotspot-refactor      (maintenance is slowing down)
```

### Using the hotspot script directly

`churn-hotspot-refactor` ships a standalone script (Python 3, no dependencies):

```bash
python3 ~/.paved-road/skills/churn-hotspot-refactor/scripts/hotspots.py \
  --repo /path/to/repo --since "12 months ago" --top 20 \
  --exclude "tests/*,vendor/*,docs/*"
```

Add `--json` for machine-readable output.

---

## Updating

| Method | Command |
|--------|---------|
| Claude Code | `claude plugin marketplace update paved-road` then `claude plugin update paved-road@paved-road` |
| Codex CLI | `codex plugin marketplace upgrade paved-road` then `codex plugin add paved-road@paved-road` |
| Gemini CLI | `gemini extensions update paved-road` |
| Manual install | `git -C ~/.paved-road pull` (symlinks pick it up; re-run the script if you used `--copy`) |

## Uninstalling

| Method | Command |
|--------|---------|
| Claude Code | `claude plugin uninstall paved-road@paved-road` and optionally `claude plugin marketplace remove paved-road` |
| Codex CLI | `codex plugin remove paved-road@paved-road` and optionally `codex plugin marketplace remove paved-road` |
| Gemini CLI | `gemini extensions uninstall paved-road` |
| Manual install | `~/.paved-road/scripts/install.sh --uninstall` |

---

## Troubleshooting

**A skill doesn't trigger on its own.**
Call it by name (see [Usage](#call-a-skill-by-name)). Automatic matching depends on how
close your request is to the skill's description.

**Skills appear twice in Gemini CLI or Codex.**
You installed both the plugin/extension *and* the manual script. Keep one:
`~/.paved-road/scripts/install.sh --uninstall`.

**New skills don't show up after updating.**
Restart the agent. In Claude Code you can run `/reload-plugins`; in Gemini CLI,
`/skills reload`.

**Project-scope skills are ignored in Gemini CLI.**
Gemini CLI only loads workspace skills in trusted folders. Trust the folder, or install
for your user instead.

**`git clone` asks for a password.**
Check the URL: `https://github.com/chip-cookie/paved-road-Skills`.

---

## Repository layout

```
paved-road-Skills/
├── skills/                      # the skills (shared by every agent)
│   └── <skill>/
│       ├── SKILL.md             # name, description, process
│       ├── references/          # longer examples, read on demand
│       └── scripts/             # runnable helpers
├── .claude-plugin/              # Claude Code plugin + marketplace
├── .codex-plugin/               # Codex plugin manifest
├── .agents/plugins/             # Codex marketplace
├── gemini-extension.json        # Gemini CLI extension
├── GEMINI.md                    # skill index loaded by Gemini CLI
├── AGENTS.md                    # rules for contributors (human or agent)
├── scripts/install.sh           # manual installer
├── scripts/validate.py          # checks every skill before commit
└── docs/source-notes.md         # where the patterns come from
```

## Contributing

Issues and pull requests are welcome. Read [AGENTS.md](AGENTS.md), then run:

```bash
python3 scripts/validate.py
```

## License & attribution

MIT. See [LICENSE](LICENSE).

The patterns are summarized from a public YouTube video (May 2026) by Vasilios Syrakis
about Atlassian's edge platform. See [docs/source-notes.md](docs/source-notes.md).
This project is independent and not affiliated with or endorsed by Atlassian.
Sovereign is Atlassian's open-source Envoy control plane; it is referenced, not included.

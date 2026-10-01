# Reference: minimal render pipeline (Python)

Illustrative sketch showing the order of operations. Not a full xDS server.

```python
import hashlib, json
from jinja2 import Environment, FileSystemLoader, StrictUndefined

env = Environment(loader=FileSystemLoader("templates"), undefined=StrictUndefined)

class RenderError(Exception): ...

def load_context(sources) -> dict:
    ctx = {}
    for name, src in sources.items():
        value = src.fetch()                 # DynamoDB, S3, service registry...
        if value is None:
            value = src.cached()            # never render with empty context
            if value is None:
                raise RenderError(f"context '{name}' unavailable and no cache")
        ctx[name] = value
    return ctx

def render(template_name: str, params: dict, ctx: dict) -> dict:
    text = env.get_template(template_name).render(params=params, ctx=ctx)
    return json.loads(text)                 # or yaml.safe_load

def build_snapshot(templates, params, sources, validators, current):
    ctx = load_context(sources)
    config = {name: render(t, params, ctx) for name, t in templates.items()}
    for check in validators:                # schema first, then semantic guardrails
        check(config)                       # raises on failure
    version = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]
    diff = compute_diff(current.config if current else {}, config)
    if current and diff.change_ratio > 0.3:
        raise RenderError(f"diff touches {diff.change_ratio:.0%} of objects; needs approval")
    return Snapshot(version=version, config=config, diff=diff)

def reconcile(templates, params, sources, validators, current):
    try:
        snap = build_snapshot(templates, params, sources, validators, current)
    except Exception as e:
        alert(e)
        return current                      # last-known-good stays live
    push_xds(snap)                          # CDS/EDS/LDS/RDS with snap.version
    return snap
```

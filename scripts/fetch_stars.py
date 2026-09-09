#!/usr/bin/env python3
"""Fetch live star counts for every GitHub repo in the list, via batched GraphQL."""
import json
import re
import subprocess
import sys
from pathlib import Path

CACHE = Path("scripts/.stars_cache.json")
BATCH = 50


def repos_from(sections):
    seen = []
    for sec in sections:
        groups = [sec] + sec["subs"]
        for g in groups:
            for e in g["entries"]:
                src = e["meta"].get("stars_src")
                if src and src not in seen:
                    seen.append(src)
    return seen


def anon_rest(full):
    """Public REST fallback: our token can be blocked by an org's PAT policy."""
    import urllib.request
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{full}",
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": "awesome-ai-scientist-site-build"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        return {"stars": d["stargazers_count"], "pushed": d.get("pushed_at"),
                "created": d.get("created_at")}
    except Exception as exc:
        print(f"  anon fallback failed for {full}: {exc}", file=sys.stderr)
        return None


def graphql(repos):
    parts = []
    for i, full in enumerate(repos):
        owner, _, name = full.partition("/")
        parts.append(
            f'r{i}: repository(owner: "{owner}", name: "{name}") '
            "{ nameWithOwner stargazerCount pushedAt createdAt }"
        )
    query = "query { " + " ".join(parts) + " }"
    proc = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        print(f"  graphql failed: {proc.stderr[:300]}", file=sys.stderr)
        return {}
    payload = json.loads(proc.stdout)
    out = {}
    for key, node in (payload.get("data") or {}).items():
        if node:
            out[node["nameWithOwner"]] = {
                "stars": node["stargazerCount"],
                "pushed": node["pushedAt"],
                "created": node["createdAt"],
            }
    return out


def main():
    sections = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    repos = repos_from(sections)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [r for r in repos if r not in cache] if "--refresh" not in sys.argv else repos
    print(f"repos={len(repos)} to_fetch={len(todo)}", file=sys.stderr)

    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        got = graphql(chunk)
        if not got:  # a dead repo in the batch nulls only that alias; retry singly
            for one in chunk:
                got.update(graphql([one]))
        # Case in the list may differ from GitHub's canonical casing.
        lower = {k.lower(): v for k, v in got.items()}
        for full in chunk:
            hit = lower.get(full.lower()) or anon_rest(full)
            cache[full] = hit if hit else {"stars": None, "pushed": None}
        done = min(i + BATCH, len(todo))
        pct = 100 * done // max(len(todo), 1)
        print(f"  [{pct:3d}%] {done}/{len(todo)} resolved", file=sys.stderr)

    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))
    missing = [r for r in repos if not cache.get(r, {}).get("stars")]
    print(f"cached={len(cache)} unresolved={len(missing)}", file=sys.stderr)
    for m in missing[:20]:
        print(f"  unresolved: {m}", file=sys.stderr)


if __name__ == "__main__":
    main()

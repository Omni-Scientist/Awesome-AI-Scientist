#!/usr/bin/env python3
"""Check every URL in the README actually resolves.

Usage:  python3 scripts/check_links.py [README.md ...]
Exit code 1 if any link is dead. shields.io badge images are skipped.
"""
import concurrent.futures as cf
import re
import sys
import urllib.error
import urllib.request

SKIP_HOSTS = ("img.shields.io", "awesome.re", "api.star-history.com", "contrib.rocks")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
URL_RE = re.compile(r'https?://[^\s\)\]\}"\'<>]+')

# GitHub answers 404 to anonymous /stargazers; probe the repo root instead.
NORMALIZE = ((("/stargazers"), ""), (("/network/members"), ""))


def normalize(url):
    for suffix, repl in NORMALIZE:
        if url.endswith(suffix):
            return url[: -len(suffix)] + repl
    return url


def probe(url):
    clean = normalize(url.rstrip('.,;:'))
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(clean, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return clean, r.status, ""
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 429) and method == "HEAD":
                continue
            if method == "GET":
                return clean, e.code, e.reason
        except Exception as e:
            if method == "GET":
                return clean, 0, type(e).__name__ + ": " + str(e)[:80]
    return clean, 0, "unreachable"


def main(paths):
    urls = []
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            for u in URL_RE.findall(fh.read()):
                u = u.rstrip('.,;:')
                if any(h in u for h in SKIP_HOSTS):
                    continue
                if u not in urls:
                    urls.append(u)
    print(f"checking {len(urls)} unique urls\n", flush=True)
    bad = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for url, code, msg in ex.map(probe, urls):
            done += 1
            ok = 200 <= code < 400
            if not ok:
                bad.append((url, code, msg))
            print(f"[{done:>3}/{len(urls)}] {'ok ' if ok else 'BAD'} {code:>3}  {url}", flush=True)
    print("\n" + "=" * 70)
    if bad:
        print(f"{len(bad)} DEAD LINKS")
        for url, code, msg in bad:
            print(f"  {code:>3}  {url}  {msg}")
        return 1
    print("all links ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["README.md"]))

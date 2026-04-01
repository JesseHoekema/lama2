"""
LAMA Package Manager
Handles: lama install <name>, lama install (all from lama.json)
Packages are stored in ./modules/<name>.lama
lama.json tracks installed packages and their versions.

Install sources (tried in order):
  1. Built-in registry (ships with interpreter)
  2. GitHub: lama-packages/<name>  (official org)
  3. GitHub shorthand: user/repo  (e.g. lama install jesse/mymod)
  4. Full GitHub URL
"""

import os
import json
import urllib.request
import urllib.error

# ─────────────────────────────────────────────
# BUILT-IN REGISTRY
# ─────────────────────────────────────────────
BUILTIN_REGISTRY = {
    "colors": {
        "version": "1.0.0",
        "description": "ANSI color helpers for terminal output",
        "code": """\
# colors module for LAMA – provides ANSI escape codes for terminal coloring

fn red(text):
    return "\\033[31m" + text + "\\033[0m"

fn green(text):
    return "\\033[32m" + text + "\\033[0m"

fn yellow(text):
    return "\\033[33m" + text + "\\033[0m"

fn blue(text):
    return "\\033[34m" + text + "\\033[0m"

fn bold(text):
    return "\\033[1m" + text + "\\033[0m"

fn reset(text):
    return "\\033[0m" + text
""",
    },
    "utils": {
        "version": "1.0.0",
        "description": "Common utility helpers",
        "code": """\
# utils module for LAMA – handy helper functions

fn clamp(val, lo, hi):
    if val < lo:
        return lo
    elif val > hi:
        return hi
    else:
        return val

fn max(a, b):
    if a > b:
        return a
    return b

fn min(a, b):
    if a < b:
        return a
    return b

fn abs_val(n):
    if n < 0:
        return n * -1
    return n
""",
    },
    "counter": {
        "version": "1.0.0",
        "description": "A simple counter class",
        "code": """\
# counter module for LAMA

class Counter:
    fn init(self, start):
        self.value = start

    fn increment(self):
        self.value = self.value + 1

    fn decrement(self):
        self.value = self.value - 1

    fn get(self):
        return self.value

    fn reset(self):
        self.value = 0
""",
    },
}

LAMA_JSON = "lama.json"
MODULES_DIR = "modules"

# Official GitHub org where community packages live
GITHUB_ORG = "lama-packages"

# ─────────────────────────────────────────────
# lama.json helpers
# ─────────────────────────────────────────────

def load_manifest():
    if not os.path.exists(LAMA_JSON):
        return {"name": "my-lama-project", "version": "1.0.0", "dependencies": {}}
    with open(LAMA_JSON, "r") as f:
        return json.load(f)


def save_manifest(manifest):
    with open(LAMA_JSON, "w") as f:
        json.dump(manifest, f, indent=2)


def ensure_modules_dir():
    os.makedirs(MODULES_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# GitHub fetching
# ─────────────────────────────────────────────

def _fetch_url(url):
    """Fetch raw text from a URL. Returns (content, error_message)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "lama-lang/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return None, str(e.reason)
    except Exception as e:
        return None, str(e)


def _github_manifest_urls(name_string):
    """Yield candidates for lama.json in a repo. Returns (url, repo_name)."""
    name = name_string
    if name.startswith("http"):
        name = name.replace("https://github.com/", "").replace("http://github.com/", "")
        if "/tree/" in name: name = name.split("/tree/")[0]
        if name.endswith(".git"): name = name[:-4]
        name = name.strip("/")

    if "/" in name:
        parts = name.split("/")
        if len(parts) >= 2:
            return [(f"https://raw.githubusercontent.com/{parts[0]}/{parts[1]}/{b}/lama.json", parts[1]) 
                    for b in ("main", "master")]
    else:
        return [(f"https://raw.githubusercontent.com/{GITHUB_ORG}/{name}/{b}/lama.json", name) 
                for b in ("main", "master")]
    return []

def _github_raw_urls(name, manifest_main=None):
    """
    Yield candidate GitHub raw URLs to try.
    If manifest_main is provided, it tries that first.
    """
    # Clean up full URLs
    if name.startswith("http"):
        name = name.replace("https://github.com/", "").replace("http://github.com/", "")
        if "/tree/" in name: name = name.split("/tree/")[0]
        if name.endswith(".git"): name = name[:-4]
        name = name.strip("/")

    if "/" in name:
        parts = name.split("/")
        user, repo = parts[0], parts[1]
        mod_name = repo
        for branch in ("main", "master"):
            # 0. If we have a manifest main, try it exactly
            if manifest_main:
                yield (f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{manifest_main}", mod_name)
            
            # 1. Try multiple default filenames
            for filename in (f"{mod_name}.lama", "main.lama", "index.lama"):
                yield (f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{filename}", mod_name)
    else:
        mod_name = name
        for branch in ("main", "master"):
            if manifest_main:
                yield (f"https://raw.githubusercontent.com/{GITHUB_ORG}/{name}/{branch}/{manifest_main}", mod_name)
            for filename in (f"{name}.lama", "main.lama", "index.lama"):
                yield (f"https://raw.githubusercontent.com/{GITHUB_ORG}/{name}/{branch}/{filename}", mod_name)


def fetch_from_github(name):
    """
    Try to download a package from GitHub.
    Returns (code_str, mod_name, source_url) or raises RuntimeError.
    """
    print(f"  🌐  Searching GitHub for '{name}'…")
    
    # 1. Try to find a lama.json manifest first
    manifest_main = None
    mod_name_override = None
    for m_url, repo_name in _github_manifest_urls(name):
        m_content, _ = _fetch_url(m_url)
        if m_content:
            try:
                m_data = json.loads(m_content)
                manifest_main = m_data.get("main")
                mod_name_override = m_data.get("name")
                print(f"  📜  Found manifest at {m_url}")
                break
            except: pass

    # 2. Try to find the .lama file
    tried = []
    for url, default_mod_name in _github_raw_urls(name, manifest_main):
        tried.append(url)
        code, err = _fetch_url(url)
        if code is not None:
            final_name = mod_name_override or default_mod_name
            print(f"  📦  Found code at {url}")
            return code, final_name, url
    
    # If we got here, we failed
    error_msg = f"Package '{name}' not found on GitHub.\n"
    error_msg += "       Tried the following locations:\n"
    for t in tried[:3]: # Show first 3
        error_msg += f"         - {t}\n"
    if len(tried) > 3:
        error_msg += f"         ... and {len(tried)-3} more.\n"
    error_msg += "       Tip: Ensure the repo is public and contains a .lama file (e.g. main.lama or repo_name.lama)."
    raise RuntimeError(error_msg)


# ─────────────────────────────────────────────
# Install a single package
# ─────────────────────────────────────────────

def install_package(name, verbose=True):
    ensure_modules_dir()
    name = name.strip()

    # 1. Built-in registry
    if name in BUILTIN_REGISTRY and "/" not in name:
        pkg = BUILTIN_REGISTRY[name]
        dest = os.path.join(MODULES_DIR, f"{name}.lama")
        with open(dest, "w") as f:
            f.write(pkg["code"])
        manifest = load_manifest()
        manifest["dependencies"][name] = pkg["version"]
        save_manifest(manifest)
        if verbose:
            print(f"  ✅  Installed {name}@{pkg['version']} → modules/{name}.lama")
        return True

    # 2. GitHub fetch
    try:
        code, mod_name, source_url = fetch_from_github(name)
        dest = os.path.join(MODULES_DIR, f"{mod_name}.lama")
        with open(dest, "w") as f:
            f.write(code)
        manifest = load_manifest()
        manifest["dependencies"][mod_name] = {"source": source_url}
        save_manifest(manifest)
        if verbose:
            print(f"  ✅  Installed {mod_name} from GitHub → modules/{mod_name}.lama")
        return True
    except RuntimeError as e:
        if verbose:
            print(f"  ❌  {e}")
        return False


# ─────────────────────────────────────────────
# Install all from lama.json
# ─────────────────────────────────────────────

def install_all(verbose=True):
    manifest = load_manifest()
    deps = manifest.get("dependencies", {})
    if not deps:
        print("  Nothing to install (no dependencies in lama.json).")
        return
    print(f"  Installing {len(deps)} package(s)…")
    for name in deps:
        install_package(name, verbose=verbose)


# ─────────────────────────────────────────────
# Uninstall a package
# ─────────────────────────────────────────────

def uninstall_package(name):
    dest = os.path.join(MODULES_DIR, f"{name}.lama")
    if os.path.exists(dest):
        os.remove(dest)
        manifest = load_manifest()
        manifest["dependencies"].pop(name, None)
        save_manifest(manifest)
        print(f"  🗑️   Uninstalled {name}")
    else:
        print(f"  Package '{name}' is not installed.")


# ─────────────────────────────────────────────
# List packages
# ─────────────────────────────────────────────

def list_packages():
    manifest = load_manifest()
    deps = manifest.get("dependencies", {})
    if not deps:
        print("  No packages installed.")
        return
    print(f"  Installed packages ({len(deps)}):")
    for name, ver in deps.items():
        ver_str = ver if isinstance(ver, str) else ver.get("source", "github")
        print(f"    • {name}  {ver_str}")


def list_available():
    print("  Built-in packages:")
    for name, info in BUILTIN_REGISTRY.items():
        print(f"    • {name}  v{info['version']}  – {info['description']}")
    print()
    print("  You can also install any GitHub repo:")
    print("    lama install <user>/<repo>")

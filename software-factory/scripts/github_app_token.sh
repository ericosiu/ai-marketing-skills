#!/usr/bin/env bash
# Mint a GitHub App installation token for FACTORY_GH_ORG.
# Prints the token to stdout only, for command substitution. Never prints
# the PEM or writes the token to a file.
set -euo pipefail
APP_DIR="${FACTORY_GH_APP_DIR:-$HOME/.config/factory/github-app}"
ORG="${FACTORY_GH_ORG:-}"
APP_ID_FILE="$APP_DIR/app-id"
PEM_FILE="$APP_DIR/private-key.pem"

die() { echo "github_app_token: $*" >&2; exit 5; }

[ -n "$ORG" ] || die "set FACTORY_GH_ORG to the account that has the App installed"
[ -d "$APP_DIR" ] || die "credentials dir missing ($APP_DIR)"
perm_dir=$(stat -c %a "$APP_DIR")
[ "$perm_dir" = 700 ] || die "$APP_DIR must be mode 700 (is $perm_dir)"
[ -f "$APP_ID_FILE" ] && [ -f "$PEM_FILE" ] || die "app-id or private-key.pem missing in $APP_DIR"
for f in "$APP_ID_FILE" "$PEM_FILE"; do
  perm=$(stat -c %a "$f")
  [ "$perm" = 600 ] || die "$f must be mode 600 (is $perm)"
done

# All minting in Python so the token only ever hits stdout of this script.
FACTORY_GH_ORG="$ORG" FACTORY_GH_APP_DIR="$APP_DIR" python3 - <<'PY'
import base64, json, os, sys, time, urllib.error, urllib.request

app_dir = os.environ["FACTORY_GH_APP_DIR"]
org = os.environ["FACTORY_GH_ORG"]
ua = "software-factory-github-app/1.0"

def die(msg, code=5):
    print(f"github_app_token: {msg}", file=sys.stderr)
    sys.exit(code)

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
except ImportError:
    die("install the cryptography package to mint a GitHub App token")

app_id = open(os.path.join(app_dir, "app-id")).read().strip()
if not app_id.isdigit():
    die("app-id must contain only digits")
pem = open(os.path.join(app_dir, "private-key.pem"), "rb").read()
try:
    key = serialization.load_pem_private_key(pem, password=None)
finally:
    del pem

now = int(time.time())
header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
payload = b64url(json.dumps({"iat": now - 60, "exp": now + 540, "iss": app_id}, separators=(",", ":")).encode())
signing_input = f"{header}.{payload}".encode()
sig = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
jwt = f"{signing_input.decode()}.{b64url(sig)}"

def api(method, url, token):
    req = urllib.request.Request(
        url,
        method=method,
        data=b"" if method != "GET" else None,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": ua,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        # Never print response bodies; they can include tokens.
        die(f"GitHub HTTP {e.code} on {method} {url.split('github.com', 1)[-1].split('?')[0]}", 5)
    except urllib.error.URLError:
        die("network error talking to GitHub", 5)

status, installs = api("GET", "https://api.github.com/app/installations", jwt)
if not isinstance(installs, list):
    die("installations response was not a list")
inst = None
for row in installs:
    acct = (row or {}).get("account") or {}
    if acct.get("login") == org:
        inst = row
        break
if inst is None:
    die(f"no installation for account {org}")
inst_id = inst.get("id")
if not inst_id:
    die("installation id missing")
status, tok = api("POST", f"https://api.github.com/app/installations/{inst_id}/access_tokens", jwt)
token = (tok or {}).get("token")
if not token:
    die("installation token missing")
sys.stdout.write(token)
sys.stdout.write("\n")
PY

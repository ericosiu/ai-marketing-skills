#!/usr/bin/env bash
# gh wrapper for every factory write.
# Uses, in order:
#   1. a GitHub App installation token minted from $FACTORY_GH_APP_DIR
#      (preferred; default ~/.config/factory/github-app/)
#   2. else a non-admin machine token from $FACTORY_GH_ENV
#      (default ~/.config/factory/github-bot.env, mode 600)
# Never prints a token. Write actions fail closed when neither credential
# works. They never fall back to a personal admin login. Read-only calls
# may fall back to the ambient gh login.
set -euo pipefail
ENV_FILE="${FACTORY_GH_ENV:-$HOME/.config/factory/github-bot.env}"
APP_DIR="${FACTORY_GH_APP_DIR:-$HOME/.config/factory/github-app}"
TOKEN_SH="$(cd "$(dirname "$0")" && pwd)/github_app_token.sh"
is_write() {
  case "${1:-} ${2:-}" in
    "pr create"|"pr merge"|"pr edit"|"pr comment"|"pr review"|"pr close"|"pr reopen"|"pr ready"|"pr revert"|"repo clone"|"issue create"|"issue comment"|"release "*|"workflow run") return 0;;
  esac
  if [ "${1:-}" = api ]; then
    for a in "$@"; do case "$a" in -X|--method|-f|-F|--field|--raw-field|--input) return 0;; esac; done
  fi
  return 1
}
refuse_write() {
  echo "factory_gh: REFUSED '$1 ${2:-}': $3 Writes never use a personal admin login." >&2
  exit 6
}
app_creds() { [ -f "$APP_DIR/private-key.pem" ] && [ -f "$APP_DIR/app-id" ]; }
try_app_token() {
  local tok=""
  if tok="$("$TOKEN_SH")" && [ -n "$tok" ]; then
    export GH_TOKEN="$tok"
    unset tok
    return 0
  fi
  unset tok
  return 1
}
use_bot_env() {
  local perm
  perm=$(stat -c %a "$ENV_FILE"); [ "$perm" = 600 ] || { echo "factory_gh: $ENV_FILE must be mode 600 (is $perm)" >&2; exit 5; }
  # shellcheck disable=SC1090
  set -a; . "$ENV_FILE"; set +a
  [ -n "${GH_TOKEN:-}" ] || { echo "factory_gh: GH_TOKEN missing in $ENV_FILE" >&2; exit 5; }
  export GH_TOKEN
}

if app_creds; then
  if try_app_token; then
    exec gh "$@"
  fi
fi
if [ -f "$ENV_FILE" ]; then
  use_bot_env
  exec gh "$@"
fi
if is_write "$@"; then
  if app_creds; then
    refuse_write "$1" "${2:-}" "GitHub App token mint failed and bot token not staged ($ENV_FILE)."
  else
    refuse_write "$1" "${2:-}" "GitHub App credentials absent ($APP_DIR) and bot token not staged ($ENV_FILE)."
  fi
fi
exec gh "$@"

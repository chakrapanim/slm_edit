#!/bin/bash
# Push slm_edit to GitHub. Run this in your terminal.
# GitHub requires a Personal Access Token (PAT), not your account password.
# Create a PAT: GitHub → Settings → Developer settings → Personal access tokens.

set -e
cd "$(dirname "$0")"

if [ -z "$GITHUB_USER" ] || [ -z "$GITHUB_TOKEN" ]; then
  echo "Usage:"
  echo "  export GITHUB_USER=your_github_username"
  echo "  export GITHUB_TOKEN=your_personal_access_token"
  echo "  ./push_to_github.sh"
  echo ""
  echo "For adobe/slm_edit use GITHUB_USER=your_adobe_github_username"
  echo "Create a token at: https://github.com/settings/tokens"
  exit 1
fi

# Push using token; use whatever remote URL is set for origin (e.g. chakrapanim/slm_edit)
origin_url=$(git remote get-url origin)
push_url="${origin_url#https://}"
push_url="https://${GITHUB_USER}:${GITHUB_TOKEN}@${push_url#https://}"
git push "$push_url" main
echo "Push completed."

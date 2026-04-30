#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="bddstudio"
VISIBILITY="--public"
REMOTE_URL=""
TAG="v0.8.0"
TITLE="BDD Studio v0.8.0"

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/publish_to_github.sh [--repo NAME] [--public|--private] [--remote URL] [--tag TAG]

Examples:
  ./scripts/publish_to_github.sh --repo bddstudio --public
  ./scripts/publish_to_github.sh --remote https://github.com/YOUR_USERNAME/bddstudio.git
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_NAME="$2"; shift 2 ;;
    --public)
      VISIBILITY="--public"; shift ;;
    --private)
      VISIBILITY="--private"; shift ;;
    --remote)
      REMOTE_URL="$2"; shift 2 ;;
    --tag)
      TAG="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if [[ ! -f "pyproject.toml" || ! -d "bddstudio" ]]; then
  echo "Run this script from the root of the BDD Studio repository."
  exit 1
fi

git init

git add .
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "Initial release of BDD Studio"
fi

git branch -M main

if [[ -n "$REMOTE_URL" ]]; then
  if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$REMOTE_URL"
  else
    git remote add origin "$REMOTE_URL"
  fi
else
  if ! command -v gh >/dev/null 2>&1; then
    echo "GitHub CLI 'gh' is not installed."
    echo "Install it with: brew install gh"
    echo "Then run: gh auth login"
    echo "Or use: --remote https://github.com/YOUR_USERNAME/bddstudio.git"
    exit 1
  fi

  if ! gh auth status >/dev/null 2>&1; then
    echo "GitHub CLI is not authenticated."
    echo "Run: gh auth login"
    exit 1
  fi

  if gh repo view "$REPO_NAME" >/dev/null 2>&1; then
    echo "GitHub repository already exists: $REPO_NAME"
  else
    gh repo create "$REPO_NAME" "$VISIBILITY" --source=. --remote=origin --description "Local CAD-style BDD/ROBDD teaching workbench"
  fi
fi

git push -u origin main

git tag -f "$TAG"
git push -f origin "$TAG"

ARCHIVE="bddstudio_${TAG}.zip"
rm -f "$ARCHIVE"
git archive --format=zip --output="$ARCHIVE" HEAD

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  if gh release view "$TAG" >/dev/null 2>&1; then
    echo "Release $TAG already exists; uploading asset."
    gh release upload "$TAG" "$ARCHIVE" --clobber
  else
    gh release create "$TAG" "$ARCHIVE" \
      --title "$TITLE" \
      --notes "BDD Studio release with CAD-style GUI, example loader, file loader, full initial BDD diagrams, final ROBDD diagrams, reduction logs, truth tables, and Graphviz export."
  fi
else
  echo "Release ZIP created locally: $ARCHIVE"
  echo "Upload it manually in GitHub Releases."
fi

echo
echo "Done."
echo "Students can clone the repository with:"
echo "  git clone <your repo URL>"

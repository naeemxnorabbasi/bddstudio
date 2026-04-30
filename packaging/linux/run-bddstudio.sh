#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

export BDDSTUDIO_PORTABLE_HOME="$DIR"

if [ -x "$DIR/graphviz/bin/dot" ]; then
  export BDDSTUDIO_DOT="$DIR/graphviz/bin/dot"
  export LD_LIBRARY_PATH="$DIR/graphviz/lib:${LD_LIBRARY_PATH:-}"
fi

cd "$DIR"

URL="http://127.0.0.1:8765"
xdg-open "$URL" >/dev/null 2>&1 || true

if [ -x "$DIR/bddstudio" ]; then
  "$DIR/bddstudio" serve --host 127.0.0.1 --port 8765 --no-browser
elif [ -x "$DIR/bddstudio/bddstudio" ]; then
  "$DIR/bddstudio/bddstudio" serve --host 127.0.0.1 --port 8765 --no-browser
else
  echo "Could not find BDD Studio executable."
  echo "Expected either:"
  echo "  $DIR/bddstudio"
  echo "  $DIR/bddstudio/bddstudio"
  exit 1
fi

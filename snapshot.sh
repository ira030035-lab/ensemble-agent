#!/bin/bash
set -e

DIR=/opt/ensemble-agent
cd "$DIR"

sync

OUT="$DIR/SNAPSHOT.md"
echo "# Ensemble-agent snapshot" > "$OUT"
echo "" >> "$OUT"
echo "Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" >> "$OUT"
echo "" >> "$OUT"

while IFS= read -r f; do
    name=$(basename "$f")
    echo "## $name" >> "$OUT"
    echo '```python' >> "$OUT"
    cat "$f" >> "$OUT"
    echo '' >> "$OUT"
    echo '```' >> "$OUT"
    echo '' >> "$OUT"
done < <(find "$DIR" -maxdepth 1 -type f -name '*.py' | sort)

if [ -f "$DIR/.env" ]; then
    echo "## .env" >> "$OUT"
    echo '```' >> "$OUT"
    sed -E 's/^([A-Za-z_][A-Za-z0-9_]*)=.*/\1=***/' "$DIR/.env" >> "$OUT"
    echo '' >> "$OUT"
    echo '```' >> "$OUT"
    echo '' >> "$OUT"
fi

git add SNAPSHOT.md
if ! git diff --cached --quiet; then
    git commit -m "auto snapshot"
    git pull --rebase origin snapshot >/dev/null 2>&1 || true
    git push origin snapshot
else
    echo "no changes"
fi

#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/.claude/skills}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/skills/latex-review-materials"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "找不到 skills/latex-review-materials/SKILL.md，请在仓库根目录运行。" >&2
  exit 1
fi

mkdir -p "$TARGET"
DEST="$TARGET/latex-review-materials"

if [ -e "$DEST" ]; then
  BACKUP="$DEST.bak-$(date +%Y%m%d-%H%M%S)"
  mv "$DEST" "$BACKUP"
  echo "已备份旧版本到 $BACKUP"
fi

cp -R "$SRC" "$DEST"
echo "已安装到 $DEST"
echo "重启会话后即可使用。"

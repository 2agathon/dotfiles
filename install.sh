#!/bin/bash
set -e

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$DOTFILES/skills"

log() { echo "[dotfiles] $1"; }

link_skills() {
  local dst=$1
  mkdir -p "$dst"
  ln -sf "$SKILLS" "$dst/skills"
  log "linked: $dst/skills → $SKILLS"
}

# Claude Code
link_skills ~/.claude
ln -sf "$DOTFILES/AGENTS.md" ~/.claude/CLAUDE.md
log "linked: ~/.claude/CLAUDE.md → AGENTS.md"

# Codex CLI
link_skills ~/.codex
ln -sf "$DOTFILES/AGENTS.md" ~/.codex/AGENTS.md
log "linked: ~/.codex/AGENTS.md → AGENTS.md"

# Gemini CLI
link_skills ~/.gemini
ln -sf "$DOTFILES/AGENTS.md" ~/.gemini/AGENTS.md
log "linked: ~/.gemini/AGENTS.md → AGENTS.md"

# OpenCode（skill 单数，路径不同）
mkdir -p ~/.config/opencode
ln -sf "$SKILLS" ~/.config/opencode/skill
ln -sf "$DOTFILES/AGENTS.md" ~/.config/opencode/AGENTS.md
log "linked: ~/.config/opencode → AGENTS.md + skills"

# GLM [OPEN QUESTION: 确认 GLM 的全局配置路径后补充]

log "Done."
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

# Codex CLI
link_skills ~/.codex

# Gemini CLI
link_skills ~/.gemini

# OpenCode（路径不同，且是 skill 单数）
mkdir -p ~/.config/opencode
ln -sf "$SKILLS" ~/.config/opencode/skill
log "linked: ~/.config/opencode/skill → $SKILLS"

# GLM [OPEN QUESTION: 确认 GLM 的全局 skills 路径]

log "Done."
# install.ps1

$DOTFILES = Split-Path -Parent $MyInvocation.MyCommand.Path
$SKILLS = "$DOTFILES\skills"

function Link-Skills {
    param($dst)
    $skillsDst = "$dst\skills"
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    if (Test-Path $skillsDst) { Remove-Item $skillsDst -Recurse -Force }
    New-Item -ItemType Junction -Path $skillsDst -Target $SKILLS | Out-Null
    Write-Host "[dotfiles] linked: $skillsDst -> $SKILLS"
}

# Claude Code
Link-Skills "$env:USERPROFILE\.claude"

# Codex CLI
Link-Skills "$env:USERPROFILE\.codex"

# Gemini CLI
Link-Skills "$env:USERPROFILE\.gemini"

# OpenCode（路径和其他不一样）
$opencodePath = "$env:USERPROFILE\.config\opencode"
New-Item -ItemType Directory -Force -Path $opencodePath | Out-Null
$opencodeSkill = "$opencodePath\skill"
if (Test-Path $opencodeSkill) { Remove-Item $opencodeSkill -Recurse -Force }
New-Item -ItemType Junction -Path $opencodeSkill -Target $SKILLS | Out-Null
Write-Host "[dotfiles] linked: $opencodeSkill -> $SKILLS"

# GLM [OPEN QUESTION: 确认 GLM 的全局 skills 路径后补充]
Write-Host "[dotfiles] GLM path not confirmed, skipping."

Write-Host "[dotfiles] Done."
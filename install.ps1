param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$NoPause,
    [switch]$Uninstall,
    [string]$ConfigPath,
    [string[]]$Target
)

$ErrorActionPreference = "Stop"

$script:INTERACTIVE = $PSBoundParameters.Count -eq 0

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DOTFILES = $SCRIPT_DIR
$SKILLS = Join-Path $DOTFILES "skills"
$AGENTS = Join-Path $DOTFILES "AGENTS.md"

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $DOTFILES "targets.json"
}

$script:RESULTS = @()
$script:VERIFY_RESULTS = @()

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

function Add-Result {
    param(
        [string]$TargetName,
        [string]$Kind,
        [string]$Path,
        [string]$Status,
        [string]$Message
    )
    $script:RESULTS += [pscustomobject]@{
        Target  = $TargetName
        Kind    = $Kind
        Path    = $Path
        Status  = $Status
        Message = $Message
    }
}

function Add-VerifyResult {
    param(
        [string]$TargetName,
        [string]$Kind,
        [string]$Path,
        [string]$Status,
        [string]$Message
    )
    $script:VERIFY_RESULTS += [pscustomobject]@{
        Target  = $TargetName
        Kind    = $Kind
        Path    = $Path
        Status  = $Status
        Message = $Message
    }
}

function Normalize-Path {
    param([string]$PathValue)

    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return ""
    }

    try {
        $resolved = Resolve-Path -LiteralPath $PathValue -ErrorAction Stop
        return $resolved.ProviderPath.TrimEnd('\', '/')
    } catch {
        try {
            return [System.IO.Path]::GetFullPath($PathValue).TrimEnd('\', '/')
        } catch {
            return $PathValue.TrimEnd('\', '/')
        }
    }
}

function Expand-PathTemplate {
    param([string]$PathValue)

    $expanded = $PathValue.Replace("{HOME}", $HOME)
    $expanded = $expanded.Replace("{DOTFILES}", $DOTFILES)
    return $expanded
}

function Render-AgentsContent {
    $text = Get-Content -LiteralPath $AGENTS -Raw -Encoding UTF8
    $dotfilesAbs = (Normalize-Path $DOTFILES)
    return $text.Replace("{{DOTFILES_ABS_PATH}}", $dotfilesAbs)
}

function Test-RenderedAgentsCopy {
    param([string]$TargetPath)

    if (-not (Test-Path -LiteralPath $TargetPath -PathType Leaf)) {
        return $false
    }

    if (-not (Test-Path -LiteralPath $AGENTS -PathType Leaf)) {
        return $false
    }

    $actual = Get-Content -LiteralPath $TargetPath -Raw -Encoding UTF8
    $expected = Render-AgentsContent
    return $actual -eq $expected
}

function Write-RenderedAgentsFile {
    param([string]$TargetPath)

    if ($DryRun) {
        Write-Info "[预演] 将写入渲染后的 AGENTS：$TargetPath"
        return
    }

    $parent = Split-Path -Parent $TargetPath
    if ($parent) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    $content = Render-AgentsContent
    [System.IO.File]::WriteAllText($TargetPath, $content, [System.Text.UTF8Encoding]::new($false))
}

function Ensure-ParentDir {
    param([string]$PathValue)

    if ($DryRun) {
        if (-not (Test-Path -LiteralPath $PathValue)) {
            Write-Info "[预演] 将创建目录：$PathValue"
        }
        return
    }

    New-Item -ItemType Directory -Force -Path $PathValue | Out-Null
}

function Remove-ExistingPath {
    param([string]$PathValue)

    if (-not (Test-Path -LiteralPath $PathValue)) {
        return
    }

    if ($DryRun) {
        Write-Info "[预演] 将删除：$PathValue"
        return
    }

    Remove-Item -LiteralPath $PathValue -Recurse -Force
}

function Get-BackupRoot {
    $root = Join-Path $HOME ".dotfiles-backup"
    if (-not (Test-Path -LiteralPath $root) -and -not $DryRun) {
        New-Item -ItemType Directory -Force -Path $root | Out-Null
    }
    return $root
}

function Backup-ExistingPath {
    param(
        [string]$PathValue,
        [string]$TargetName,
        [string]$Kind
    )

    if (-not (Test-Path -LiteralPath $PathValue) -and -not (Test-Path -LiteralPath $PathValue -PathType Leaf) -and -not (Test-Path -LiteralPath $PathValue -PathType Container)) {
        return
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = Get-BackupRoot
    $safeTarget = ($TargetName -replace '[\\/:*?"<>|]', '_')
    $safeKind = ($Kind -replace '[\\/:*?"<>|]', '_')
    $leaf = Split-Path -Leaf $PathValue
    $backupDir = Join-Path $backupRoot $timestamp
    $finalDir = Join-Path $backupDir "$safeTarget-$safeKind"
    $backupPath = Join-Path $finalDir $leaf

    if ($DryRun) {
        Write-Info "[预演] 将备份：$PathValue -> $backupPath"
        return
    }

    New-Item -ItemType Directory -Force -Path $finalDir | Out-Null
    Move-Item -LiteralPath $PathValue -Destination $backupPath -Force
    Write-Warn "[备份] 已备份：$PathValue -> $backupPath"
}

function Ensure-Elevated {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if ($isAdmin) {
        return
    }

    Write-Warn "[dotfiles] 当前不是管理员，准备请求提权。"

    $hostExe = (Get-Process -Id $PID).Path
    if (-not $hostExe) {
        $hostExe = "pwsh"
    }

    $argList = @(
        '-ExecutionPolicy', 'Bypass',
        '-File', "`"$($MyInvocation.MyCommand.Path)`""
    )

    if ($DryRun) { $argList += '-DryRun' }
    if ($Force) { $argList += '-Force' }
    if ($NoPause) { $argList += '-NoPause' }
    if ($Uninstall) { $argList += '-Uninstall' }
    if ($ConfigPath) { $argList += @('-ConfigPath', "`"$ConfigPath`"") }
    if ($Target) {
        foreach ($t in $Target) {
            $argList += @('-Target', "`"$t`"")
        }
    }

    Start-Process $hostExe -Verb RunAs -ArgumentList $argList
    exit 0
}

function Load-Targets {
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        throw "[dotfiles] 未找到配置文件：$ConfigPath"
    }

    $json = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    return $json.targets
}

function Get-SelectedTargets {
    $allTargets = Load-Targets

    if (-not $Target -or $Target.Count -eq 0) {
        return $allTargets
    }

    $selected = @()
    foreach ($entry in $allTargets) {
        if ($Target -contains $entry.name) {
            $selected += $entry
        }
    }

    return $selected
}

function Test-CorrectSkillsLink {
    param([string]$TargetPath)

    if (-not (Test-Path -LiteralPath $TargetPath)) {
        return $false
    }

    $item = Get-Item -LiteralPath $TargetPath -Force
    if (-not $item.Attributes.ToString().Contains("ReparsePoint")) {
        return $false
    }

    $expected = Normalize-Path $SKILLS
    try {
        $actual = Normalize-Path $item.Target
        return $actual -eq $expected
    } catch {
        return $false
    }
}

function Get-AgentsState {
    param([string]$TargetPath)

    if (-not (Test-Path -LiteralPath $TargetPath)) {
        return "Missing"
    }

    $item = Get-Item -LiteralPath $TargetPath -Force

    if ($item.Attributes.ToString().Contains("ReparsePoint")) {
        try {
            $actual = Normalize-Path $item.Target
            $expected = Normalize-Path $AGENTS
            if ($actual -eq $expected) {
                return "Linked"
            }
        } catch {
        }
    }

    if (Test-RenderedAgentsCopy $TargetPath) {
        return "Copied"
    }

    return "Other"
}

function Verify-SkillsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$SkillName
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $SkillName

    if (Test-CorrectSkillsLink $targetPath) {
        Write-Ok "[校验通过] $TargetName / skills：$targetPath"
        Add-VerifyResult $TargetName "skills" $targetPath "成功" "是预期链接"
    } else {
        Write-Err "[校验失败] $TargetName / skills：$targetPath"
        Add-VerifyResult $TargetName "skills" $targetPath "失败" "不是预期链接"
    }
}

function Verify-AgentsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$FileName
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $FileName
    $state = Get-AgentsState $targetPath

    if ($state -eq "Copied") {
        Write-Ok "[校验通过] $TargetName / agents：$targetPath"
        Add-VerifyResult $TargetName "agents" $targetPath "成功" "是当前环境下正确的渲染文件"
    } else {
        Write-Err "[校验失败] $TargetName / agents：$targetPath"
        Add-VerifyResult $TargetName "agents" $targetPath "失败" "不是当前环境下正确的渲染文件"
    }
}

function Install-SkillsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$SkillName
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $SkillName

    Ensure-ParentDir $dstExpanded

    if (Test-CorrectSkillsLink $targetPath) {
        Write-Ok "[跳过] $TargetName / skills 已正确存在：$targetPath"
        Add-Result $TargetName "skills" $targetPath "跳过" "已是正确链接"
        if (-not $DryRun) {
            Verify-SkillsEntry $TargetName $Dst $SkillName
        }
        return
    }

    if (Test-Path -LiteralPath $targetPath) {
        if (-not $Force) {
            Write-Warn "[跳过] $TargetName / skills 已存在非预期内容：$targetPath"
            Write-Warn "       如需接管，请使用 -Force（会先备份再替换）。"
            Add-Result $TargetName "skills" $targetPath "跳过" "已存在非预期内容；未使用 -Force"
            return
        }

        Backup-ExistingPath $targetPath $TargetName "skills"
    }

    if ($DryRun) {
        Write-Info "[预演] 将创建 skills Junction：$targetPath -> $SKILLS"
        Add-Result $TargetName "skills" $targetPath "预演" "将创建 Junction"
        return
    }

    New-Item -ItemType Junction -Path $targetPath -Target $SKILLS | Out-Null
    Write-Ok "[完成] $TargetName / skills：$targetPath -> $SKILLS"
    Add-Result $TargetName "skills" $targetPath "成功" "已创建 Junction"
    Verify-SkillsEntry $TargetName $Dst $SkillName
}

function Install-AgentsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$FileName
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $FileName

    Ensure-ParentDir $dstExpanded

    $state = Get-AgentsState $targetPath
    if ($state -eq "Copied") {
        Write-Ok "[跳过] $TargetName / agents 已存在受管渲染文件：$targetPath"
        Add-Result $TargetName "agents" $targetPath "跳过" "已是当前环境下正确的渲染文件"
        if (-not $DryRun) {
            Verify-AgentsEntry $TargetName $Dst $FileName
        }
        return
    }

    if ($state -eq "Linked") {
        if ($DryRun) {
            Write-Info "[预演] 将把旧版 AGENTS 链接迁移为渲染后的本地文件：$targetPath"
            Add-Result $TargetName "agents" $targetPath "预演" "将把旧版链接替换为渲染后的本地文件"
            return
        }

        Remove-Item -LiteralPath $targetPath -Force
        Write-RenderedAgentsFile $targetPath
        Write-Ok "[完成] $TargetName / agents：$targetPath"
        Add-Result $TargetName "agents" $targetPath "成功" "已将旧版链接迁移为渲染后的本地文件"
        Verify-AgentsEntry $TargetName $Dst $FileName
        return
    }

    if (Test-Path -LiteralPath $targetPath) {
        if (-not $Force) {
            Write-Warn "[跳过] $TargetName / agents 已存在非预期内容：$targetPath"
            Write-Warn "       如需接管，请使用 -Force（会先备份再替换）。"
            Add-Result $TargetName "agents" $targetPath "跳过" "已存在非预期内容；未使用 -Force"
            return
        }

        Backup-ExistingPath $targetPath $TargetName "agents"
    }

    if ($DryRun) {
        Write-Info "[预演] 将写入渲染后的 AGENTS：$targetPath"
        Add-Result $TargetName "agents" $targetPath "预演" "将写入渲染后的本地文件"
        return
    }

    Write-RenderedAgentsFile $targetPath
    Write-Ok "[完成] $TargetName / agents：$targetPath"
    Add-Result $TargetName "agents" $targetPath "成功" "已写入渲染后的本地文件"
    Verify-AgentsEntry $TargetName $Dst $FileName
}

function Uninstall-SkillsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$SkillName
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $SkillName

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Info "[跳过] $TargetName / skills 不存在：$targetPath"
        Add-Result $TargetName "skills" $targetPath "跳过" "目标不存在"
        return
    }

    if (-not (Test-CorrectSkillsLink $targetPath)) {
        if (-not $Force) {
            Write-Warn "[跳过] $TargetName / skills 存在，但不是当前脚本管理的目标：$targetPath"
            Write-Warn "       如需卸载并清理，请使用 -Force（会先备份再删除）。"
            Add-Result $TargetName "skills" $targetPath "跳过" "存在非受管内容；未使用 -Force"
            return
        }

        Backup-ExistingPath $targetPath $TargetName "skills-uninstall"
    } else {
        if ($DryRun) {
            Write-Info "[预演] 将卸载 skills：$targetPath"
            Add-Result $TargetName "skills" $targetPath "预演" "将删除"
            return
        }

        Remove-Item -LiteralPath $targetPath -Recurse -Force
        Write-Ok "[完成] 已卸载 $TargetName / skills：$targetPath"
        Add-Result $TargetName "skills" $targetPath "成功" "已删除"
        return
    }

    if ($DryRun) {
        Write-Info "[预演] 将卸载 skills：$targetPath"
        Add-Result $TargetName "skills" $targetPath "预演" "将删除"
        return
    }

    if (Test-Path -LiteralPath $targetPath) {
        Remove-Item -LiteralPath $targetPath -Recurse -Force
    }

    Write-Ok "[完成] 已卸载 $TargetName / skills：$targetPath"
    Add-Result $TargetName "skills" $targetPath "成功" "已删除"
}

function Uninstall-AgentsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$FileName
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $FileName

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Info "[跳过] $TargetName / agents 不存在：$targetPath"
        Add-Result $TargetName "agents" $targetPath "跳过" "目标不存在"
        return
    }

    $state = Get-AgentsState $targetPath
    if ($state -ne "Linked" -and $state -ne "Copied") {
        if (-not $Force) {
            Write-Warn "[跳过] $TargetName / agents 存在，但不是当前脚本管理的目标：$targetPath"
            Write-Warn "       如需卸载并清理，请使用 -Force（会先备份再删除）。"
            Add-Result $TargetName "agents" $targetPath "跳过" "存在非受管内容；未使用 -Force"
            return
        }

        Backup-ExistingPath $targetPath $TargetName "agents-uninstall"
    } else {
        if ($DryRun) {
            Write-Info "[预演] 将卸载 agents：$targetPath"
            Add-Result $TargetName "agents" $targetPath "预演" "将删除"
            return
        }

        Remove-Item -LiteralPath $targetPath -Force
        Write-Ok "[完成] 已卸载 $TargetName / agents：$targetPath"
        Add-Result $TargetName "agents" $targetPath "成功" "已删除"
        return
    }

    if ($DryRun) {
        Write-Info "[预演] 将卸载 agents：$targetPath"
        Add-Result $TargetName "agents" $targetPath "预演" "将删除"
        return
    }

    if (Test-Path -LiteralPath $targetPath) {
        Remove-Item -LiteralPath $targetPath -Force
    }

    Write-Ok "[完成] 已卸载 $TargetName / agents：$targetPath"
    Add-Result $TargetName "agents" $targetPath "成功" "已删除"
}

function Process-Target {
    param($TargetEntry)

    $targetName = $TargetEntry.name

    Write-Info ""
    Write-Info "[dotfiles] 正在处理：$targetName"

    if ($TargetEntry.skills) {
        foreach ($s in $TargetEntry.skills) {
            $dst = $s.path
            $name = if ($s.name) { $s.name } else { "skills" }

            try {
                if ($Uninstall) {
                    Uninstall-SkillsEntry $targetName $dst $name
                } else {
                    Install-SkillsEntry $targetName $dst $name
                }
            } catch {
                Add-Result $targetName "skills" "$(Join-Path (Expand-PathTemplate $dst) $name)" "失败" $_.Exception.Message
                Write-Err "[失败] $targetName / skills：$($_.Exception.Message)"
            }
        }
    }

    if ($TargetEntry.agents) {
        foreach ($a in $TargetEntry.agents) {
            $dst = $a.path
            $name = if ($a.name) { $a.name } else { "AGENTS.md" }

            try {
                if ($Uninstall) {
                    Uninstall-AgentsEntry $targetName $dst $name
                } else {
                    Install-AgentsEntry $targetName $dst $name
                }
            } catch {
                Add-Result $targetName "agents" "$(Join-Path (Expand-PathTemplate $dst) $name)" "失败" $_.Exception.Message
                Write-Err "[失败] $targetName / agents：$($_.Exception.Message)"
            }
        }
    }
}

function Show-Summary {
    Write-Host ""
    Write-Host "================ 执行结果汇总 ================" -ForegroundColor Magenta

    if (-not $script:RESULTS -or $script:RESULTS.Count -eq 0) {
        Write-Host "没有产生任何执行结果。" -ForegroundColor Yellow
    } else {
        $success = @($script:RESULTS | Where-Object { $_.Status -eq "成功" }).Count
        $skipped = @($script:RESULTS | Where-Object { $_.Status -eq "跳过" }).Count
        $preview = @($script:RESULTS | Where-Object { $_.Status -eq "预演" }).Count
        $failed  = @($script:RESULTS | Where-Object { $_.Status -eq "失败" }).Count

        Write-Host "成功：$success    跳过：$skipped    预演：$preview    失败：$failed"

        foreach ($r in $script:RESULTS) {
            $line = "[$($r.Status)] $($r.Target) / $($r.Kind)`n  路径：$($r.Path)`n  说明：$($r.Message)"
            switch ($r.Status) {
                "成功" { Write-Host $line -ForegroundColor Green }
                "跳过" { Write-Host $line -ForegroundColor Yellow }
                "预演" { Write-Host $line -ForegroundColor Cyan }
                "失败" { Write-Host $line -ForegroundColor Red }
                default { Write-Host $line }
            }
        }
    }

    Write-Host ""
    Write-Host "================ 校验结果汇总 ================" -ForegroundColor Magenta

    if (-not $script:VERIFY_RESULTS -or $script:VERIFY_RESULTS.Count -eq 0) {
        if ($DryRun -or $Uninstall) {
            Write-Host "当前模式不进行安装后校验。" -ForegroundColor Yellow
        } else {
            Write-Host "没有产生任何校验结果。" -ForegroundColor Yellow
        }
    } else {
        $verifyOk   = @($script:VERIFY_RESULTS | Where-Object { $_.Status -eq "成功" }).Count
        $verifyFail = @($script:VERIFY_RESULTS | Where-Object { $_.Status -eq "失败" }).Count

        Write-Host "通过：$verifyOk    失败：$verifyFail"

        foreach ($r in $script:VERIFY_RESULTS) {
            $line = "[$($r.Status)] $($r.Target) / $($r.Kind)`n  路径：$($r.Path)`n  说明：$($r.Message)"
            switch ($r.Status) {
                "成功" { Write-Host $line -ForegroundColor Green }
                "失败" { Write-Host $line -ForegroundColor Red }
                default { Write-Host $line }
            }
        }
    }

    Write-Host "============================================" -ForegroundColor Magenta
}

function Show-MainMenu {
    Write-Host ""
    Write-Host "================ dotfiles 安装器 ================" -ForegroundColor Magenta
    Write-Host "1) 安装"
    Write-Host "2) 卸载"
    Write-Host "3) 预演安装"
    Write-Host "4) 预演卸载"
    Write-Host "5) 退出"
    Write-Host "===============================================" -ForegroundColor Magenta

    while ($true) {
        $choice = Read-Host "请选择操作"
        switch ($choice) {
            "1" {
                $script:DryRun = $false
                $script:Uninstall = $false
                return
            }
            "2" {
                $script:DryRun = $false
                $script:Uninstall = $true
                return
            }
            "3" {
                $script:DryRun = $true
                $script:Uninstall = $false
                return
            }
            "4" {
                $script:DryRun = $true
                $script:Uninstall = $true
                return
            }
            "5" {
                exit 0
            }
            default {
                Write-Warn "请输入 1-5 之间的编号。"
            }
        }
    }
}

function Show-TargetMenu {
    param($AllTargets)

    Write-Host ""
    Write-Info "[dotfiles] 请选择目标，可多选（用逗号分隔）："

    for ($i = 0; $i -lt $AllTargets.Count; $i++) {
        Write-Host "$($i + 1)) $($AllTargets[$i].name)"
    }
    $allIndex = $AllTargets.Count + 1
    Write-Host "$allIndex) 全部"

    while ($true) {
        $inputValue = Read-Host "请输入编号"
        if ([string]::IsNullOrWhiteSpace($inputValue)) {
            Write-Warn "请输入至少一个编号。"
            continue
        }

        $parts = $inputValue.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
        $selectedNames = @()
        $chooseAll = $false
        $valid = $true

        foreach ($part in $parts) {
            if (-not ($part -match '^\d+$')) {
                $valid = $false
                break
            }

            $n = [int]$part
            if ($n -eq $allIndex) {
                $chooseAll = $true
                break
            }

            if ($n -lt 1 -or $n -gt $AllTargets.Count) {
                $valid = $false
                break
            }

            $name = $AllTargets[$n - 1].name
            if ($selectedNames -notcontains $name) {
                $selectedNames += $name
            }
        }

        if (-not $valid) {
            Write-Warn "输入格式不正确，请输入数字编号，例如：1,3"
            continue
        }

        if ($chooseAll) {
            $script:Target = @($AllTargets | ForEach-Object { $_.name })
            break
        }

        if (-not $selectedNames -or $selectedNames.Count -eq 0) {
            Write-Warn "请选择至少一个目标。"
            continue
        }

        $script:Target = $selectedNames
        break
    }
}

function Interactive-Mode {
    $allTargets = Load-Targets
    Show-MainMenu
    Show-TargetMenu $allTargets

    $forceAnswer = Read-Host "是否允许接管已存在的陌生目标？(y/N)"
    if ($forceAnswer -match '^(y|Y|yes|YES)$') {
        $script:Force = $true
    } else {
        $script:Force = $false
    }

    Write-Host ""
    Write-Info "[dotfiles] 本次执行配置："
    if ($Uninstall -and $DryRun) {
        Write-Host "  模式：预演卸载"
    } elseif ($Uninstall) {
        Write-Host "  模式：卸载"
    } elseif ($DryRun) {
        Write-Host "  模式：预演安装"
    } else {
        Write-Host "  模式：安装"
    }

    Write-Host "  接管陌生目标：$(if ($Force) { '是（会先备份再替换）' } else { '否' })"
    Write-Host "  目标：$($Target -join ', ')"

    $confirm = Read-Host "确认执行？(Y/n)"
    if ($confirm -match '^(n|N|no|NO)$') {
        Write-Warn "[dotfiles] 已取消。"
        exit 0
    }
}

function Main {
    Ensure-Elevated

    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        Write-Err "[dotfiles] 未找到配置文件：$ConfigPath"
        exit 1
    }

    if (-not $Uninstall) {
        if (-not (Test-Path -LiteralPath $SKILLS -PathType Container)) {
            Write-Err "[dotfiles] 未找到 skills 目录：$SKILLS"
            exit 1
        }
        if (-not (Test-Path -LiteralPath $AGENTS -PathType Leaf)) {
            Write-Err "[dotfiles] 未找到 AGENTS.md：$AGENTS"
            exit 1
        }
    }

    if ($script:INTERACTIVE) {
        Interactive-Mode
    }

    if ($DryRun) {
        if ($Uninstall) {
            Write-Info "[dotfiles] 当前为预演模式：只显示将卸载什么，不会真的删除。"
        } else {
            Write-Info "[dotfiles] 当前为预演模式：只显示将安装什么，不会真的修改。"
        }
    }

    if ($Force) {
        Write-Warn "[dotfiles] 已启用 -Force：遇到陌生目标时，会先备份到 $HOME\.dotfiles-backup 再替换。"
    }

    if ($Uninstall) {
        Write-Warn "[dotfiles] 当前为卸载模式。"
    }

    $selectedTargets = Get-SelectedTargets
    if (-not $selectedTargets -or $selectedTargets.Count -eq 0) {
        Write-Err "[dotfiles] 没有可执行的目标。"
        exit 1
    }

    foreach ($entry in $selectedTargets) {
        Process-Target $entry
    }

    Show-Summary

    if (-not $NoPause) {
        Write-Host ""
        Read-Host "按回车退出" | Out-Null
    }
}

Main
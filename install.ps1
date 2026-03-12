param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$NoPause,
    [switch]$NoElevation,
    [switch]$Uninstall,
    [string]$ConfigPath,
    [string[]]$TargetNames
)

$ErrorActionPreference = "Stop"

$SCRIPT_PATH = $MyInvocation.MyCommand.Path
if (-not $SCRIPT_PATH) {
    throw "[dotfiles] 无法确定脚本路径。请以脚本文件方式运行。"
}

$DOTFILES = Split-Path -Parent $SCRIPT_PATH
$SKILLS   = Join-Path $DOTFILES "skills"
$AGENTS   = Join-Path $DOTFILES "AGENTS.md"

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $DOTFILES "targets.json"
}

$script:Results = New-Object System.Collections.Generic.List[object]
$script:VerifyResults = New-Object System.Collections.Generic.List[object]
$script:WasElevatedRelaunch = $false

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-WarnMsg {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-ErrMsg {
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

    $script:Results.Add([pscustomobject]@{
        Target  = $TargetName
        Kind    = $Kind
        Path    = $Path
        Status  = $Status
        Message = $Message
    }) | Out-Null
}

function Add-VerifyResult {
    param(
        [string]$TargetName,
        [string]$Kind,
        [string]$Path,
        [string]$Status,
        [string]$Message
    )

    $script:VerifyResults.Add([pscustomobject]@{
        Target  = $TargetName
        Kind    = $Kind
        Path    = $Path
        Status  = $Status
        Message = $Message
    }) | Out-Null
}

function Normalize-Path {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }

    try {
        return [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    } catch {
        return $Path.TrimEnd('\', '/')
    }
}

function Quote-Arg {
    param([string]$Value)

    if ($null -eq $Value) {
        return '""'
    }

    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"', '\"') + '"'
    }

    return $Value
}

function Get-ForwardedArgs {
    $argsList = @()

    foreach ($entry in $PSBoundParameters.GetEnumerator()) {
        if ($entry.Key -eq 'NoElevation') {
            continue
        }

        if ($entry.Value -is [switch]) {
            if ($entry.Value.IsPresent) {
                $argsList += "-$($entry.Key)"
            }
        } elseif ($entry.Value -is [System.Array]) {
            foreach ($item in $entry.Value) {
                $argsList += "-$($entry.Key)"
                $argsList += [string]$item
            }
        } elseif ($null -ne $entry.Value -and $entry.Value -ne '') {
            $argsList += "-$($entry.Key)"
            $argsList += [string]$entry.Value
        }
    }

    if ($MyInvocation.UnboundArguments) {
        foreach ($arg in $MyInvocation.UnboundArguments) {
            $argsList += [string]$arg
        }
    }

    return $argsList
}

function Ensure-Elevated {
    if ($NoElevation) {
        $script:WasElevatedRelaunch = $true
        return
    }

    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if ($isAdmin) {
        return
    }

    Write-WarnMsg "[dotfiles] 检测到当前不是管理员权限。"
    Write-WarnMsg "[dotfiles] 将重新以管理员身份启动安装器，请在新打开的窗口中继续操作。"

    $forwarded = Get-ForwardedArgs
    $allArgs = @(
        "-NoProfile"
        "-ExecutionPolicy"
        "Bypass"
        "-File"
        $SCRIPT_PATH
        "-NoElevation"
    ) + $forwarded

    $argLine = ($allArgs | ForEach-Object { Quote-Arg $_ }) -join ' '

    Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList $argLine | Out-Null
    exit
}

function Ensure-ParentDir {
    param([string]$Path)

    if ($DryRun) {
        if (-not (Test-Path -LiteralPath $Path)) {
            Write-Info "[预演] 将创建目录：$Path"
        }
        return
    }

    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Remove-ExistingPath {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    if ($DryRun) {
        Write-Info "[预演] 将删除：$Path"
        return
    }

    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    } else {
        Remove-Item -LiteralPath $Path -Force
    }
}

function Get-PathState {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return @{
            Exists   = $false
            Item     = $null
            IsLink   = $false
            LinkType = $null
            Target   = $null
            IsDir    = $false
        }
    }

    $item = Get-Item -LiteralPath $Path -Force
    $isLink = (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)

    $linkType = $null
    if ($item.PSObject.Properties.Match('LinkType').Count -gt 0) {
        $linkType = [string]$item.LinkType
        if ($linkType) {
            $isLink = $true
        }
    }

    $target = $null
    if ($item.PSObject.Properties.Match('Target').Count -gt 0) {
        $target = $item.Target
    }
    if (-not $target -and $item.PSObject.Properties.Match('LinkTarget').Count -gt 0) {
        $target = $item.LinkTarget
    }
    if ($target -is [array]) {
        $target = $target[0]
    }

    return @{
        Exists   = $true
        Item     = $item
        IsLink   = $isLink
        LinkType = $linkType
        Target   = $target
        IsDir    = [bool]$item.PSIsContainer
    }
}

function Test-SameFileContent {
    param(
        [string]$PathA,
        [string]$PathB
    )

    if (-not (Test-Path -LiteralPath $PathA)) { return $false }
    if (-not (Test-Path -LiteralPath $PathB)) { return $false }

    $itemA = Get-Item -LiteralPath $PathA -Force
    $itemB = Get-Item -LiteralPath $PathB -Force

    if ($itemA.PSIsContainer -or $itemB.PSIsContainer) {
        return $false
    }

    $hashA = Get-FileHash -LiteralPath $PathA -Algorithm SHA256
    $hashB = Get-FileHash -LiteralPath $PathB -Algorithm SHA256

    return $hashA.Hash -eq $hashB.Hash
}

function Expand-PathTemplate {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $Path
    }

    $expanded = $Path.Replace('{HOME}', $env:USERPROFILE)
    $expanded = $expanded.Replace('{DOTFILES}', $DOTFILES)
    $expanded = $expanded -replace '/', '\'
    return $expanded
}

function Load-Targets {
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        throw "[dotfiles] 未找到配置文件：$ConfigPath"
    }

    $jsonText = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8
    $config = $jsonText | ConvertFrom-Json

    if (-not $config.targets) {
        throw "[dotfiles] 配置文件缺少 targets。"
    }

    return @($config.targets)
}

function Test-CorrectSkillsLink {
    param([string]$TargetPath)

    $state = Get-PathState $TargetPath
    if (-not $state.Exists) {
        return $false
    }

    if (-not $state.IsLink) {
        return $false
    }

    $actual = Normalize-Path $state.Target
    $expected = Normalize-Path $SKILLS

    return ($actual -eq $expected)
}

function Get-AgentsState {
    param([string]$TargetPath)

    $state = Get-PathState $TargetPath
    if (-not $state.Exists) {
        return "Missing"
    }

    $actual = Normalize-Path $state.Target
    $expected = Normalize-Path $AGENTS

    if ($state.IsLink -and $actual -eq $expected) {
        return "Linked"
    }

    if (-not $state.IsDir -and (Test-SameFileContent -PathA $TargetPath -PathB $AGENTS)) {
        return "Copied"
    }

    return "Other"
}

function Get-BackupRoot {
    $root = Join-Path $env:USERPROFILE ".dotfiles-backup"
    if (-not (Test-Path -LiteralPath $root) -and -not $DryRun) {
        New-Item -ItemType Directory -Force -Path $root | Out-Null
    }
    return $root
}

function Backup-ExistingPath {
    param(
        [string]$Path,
        [string]$TargetName,
        [string]$Kind
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = Get-BackupRoot
    $safeTarget = ($TargetName -replace '[\\/:*?"<>|]', '_')
    $safeKind = ($Kind -replace '[\\/:*?"<>|]', '_')
    $leaf = Split-Path -Leaf $Path
    $backupDir = Join-Path $backupRoot $timestamp
    $finalDir = Join-Path $backupDir "$safeTarget-$safeKind"
    $backupPath = Join-Path $finalDir $leaf

    if ($DryRun) {
        Write-Info "[预演] 将备份：$Path -> $backupPath"
        return $backupPath
    }

    New-Item -ItemType Directory -Force -Path $finalDir | Out-Null
    Move-Item -LiteralPath $Path -Destination $backupPath -Force
    Write-WarnMsg "[备份] 已备份：$Path -> $backupPath"
    return $backupPath
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
        Write-ErrMsg "[校验失败] $TargetName / skills：$targetPath"
        Add-VerifyResult $TargetName "skills" $targetPath "失败" "不是预期链接"
    }
}

function Verify-AgentsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$Name
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $Name
    $agentState = Get-AgentsState $targetPath

    if ($agentState -eq "Linked" -or $agentState -eq "Copied") {
        Write-Ok "[校验通过] $TargetName / agents：$targetPath"
        Add-VerifyResult $TargetName "agents" $targetPath "成功" "是预期链接或正确副本"
    } else {
        Write-ErrMsg "[校验失败] $TargetName / agents：$targetPath"
        Add-VerifyResult $TargetName "agents" $targetPath "失败" "不是预期链接或正确副本"
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
            Verify-SkillsEntry -TargetName $TargetName -Dst $Dst -SkillName $SkillName
        }
        return
    }

    $state = Get-PathState $targetPath
    if ($state.Exists) {
        if (-not $Force) {
            Write-WarnMsg "[跳过] $TargetName / skills 已存在非预期内容：$targetPath"
            Write-WarnMsg "       如需接管，请使用 -Force（会先备份再替换）。"
            Add-Result $TargetName "skills" $targetPath "跳过" "已存在非预期内容；未使用 -Force"
            return
        }

        Backup-ExistingPath -Path $targetPath -TargetName $TargetName -Kind "skills" | Out-Null
    }

    if ($DryRun) {
        Write-Info "[预演] 将创建 skills 链接：$targetPath -> $SKILLS"
        Add-Result $TargetName "skills" $targetPath "预演" "将创建 Junction"
        return
    }

    New-Item -ItemType Junction -Path $targetPath -Target $SKILLS | Out-Null
    Write-Ok "[完成] $TargetName / skills：$targetPath -> $SKILLS"
    Add-Result $TargetName "skills" $targetPath "成功" "已创建 Junction"
    Verify-SkillsEntry -TargetName $TargetName -Dst $Dst -SkillName $SkillName
}

function Install-AgentsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$Name
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $Name

    Ensure-ParentDir $dstExpanded

    $agentState = Get-AgentsState $targetPath
    if ($agentState -eq "Linked") {
        Write-Ok "[跳过] $TargetName / agents 已正确存在：$targetPath"
        Add-Result $TargetName "agents" $targetPath "跳过" "已是正确符号链接"
        if (-not $DryRun) {
            Verify-AgentsEntry -TargetName $TargetName -Dst $Dst -Name $Name
        }
        return
    }

    if ($agentState -eq "Copied") {
        Write-Ok "[跳过] $TargetName / agents 已存在受管副本：$targetPath"
        Add-Result $TargetName "agents" $targetPath "跳过" "已是正确副本"
        if (-not $DryRun) {
            Verify-AgentsEntry -TargetName $TargetName -Dst $Dst -Name $Name
        }
        return
    }

    $state = Get-PathState $targetPath
    if ($state.Exists) {
        if (-not $Force) {
            Write-WarnMsg "[跳过] $TargetName / agents 已存在非预期内容：$targetPath"
            Write-WarnMsg "       如需接管，请使用 -Force（会先备份再替换）。"
            Add-Result $TargetName "agents" $targetPath "跳过" "已存在非预期内容；未使用 -Force"
            return
        }

        Backup-ExistingPath -Path $targetPath -TargetName $TargetName -Kind "agents" | Out-Null
    }

    if ($DryRun) {
        Write-Info "[预演] 将创建 agents 链接：$targetPath -> $AGENTS"
        Add-Result $TargetName "agents" $targetPath "预演" "将优先创建 SymbolicLink，失败则复制"
        return
    }

    try {
        New-Item -ItemType SymbolicLink -Path $targetPath -Target $AGENTS | Out-Null
        Write-Ok "[完成] $TargetName / agents：$targetPath -> $AGENTS"
        Add-Result $TargetName "agents" $targetPath "成功" "已创建 SymbolicLink"
    } catch {
        Copy-Item -LiteralPath $AGENTS -Destination $targetPath -Force
        Write-WarnMsg "[完成] $TargetName / agents：符号链接失败，已改为复制：$targetPath"
        Add-Result $TargetName "agents" $targetPath "成功" "符号链接失败，已复制文件"
    }

    Verify-AgentsEntry -TargetName $TargetName -Dst $Dst -Name $Name
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

    $isManaged = Test-CorrectSkillsLink $targetPath
    if (-not $isManaged) {
        if (-not $Force) {
            Write-WarnMsg "[跳过] $TargetName / skills 存在，但不是当前脚本管理的目标：$targetPath"
            Write-WarnMsg "       如需卸载并清理，请使用 -Force（会先备份再删除）。"
            Add-Result $TargetName "skills" $targetPath "跳过" "存在非受管内容；未使用 -Force"
            return
        }

        Backup-ExistingPath -Path $targetPath -TargetName $TargetName -Kind "skills-uninstall" | Out-Null
    } else {
        Remove-ExistingPath $targetPath
    }

    if ($DryRun) {
        Write-Info "[预演] 将卸载 skills：$targetPath"
        Add-Result $TargetName "skills" $targetPath "预演" "将删除"
        return
    }

    if (Test-Path -LiteralPath $targetPath) {
        Remove-ExistingPath $targetPath
    }

    Write-Ok "[完成] 已卸载 $TargetName / skills：$targetPath"
    Add-Result $TargetName "skills" $targetPath "成功" "已删除"
}

function Uninstall-AgentsEntry {
    param(
        [string]$TargetName,
        [string]$Dst,
        [string]$Name
    )

    $dstExpanded = Expand-PathTemplate $Dst
    $targetPath = Join-Path $dstExpanded $Name

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Info "[跳过] $TargetName / agents 不存在：$targetPath"
        Add-Result $TargetName "agents" $targetPath "跳过" "目标不存在"
        return
    }

    $agentState = Get-AgentsState $targetPath
    $isManaged = @("Linked", "Copied") -contains $agentState

    if (-not $isManaged) {
        if (-not $Force) {
            Write-WarnMsg "[跳过] $TargetName / agents 存在，但不是当前脚本管理的目标：$targetPath"
            Write-WarnMsg "       如需卸载并清理，请使用 -Force（会先备份再删除）。"
            Add-Result $TargetName "agents" $targetPath "跳过" "存在非受管内容；未使用 -Force"
            return
        }

        Backup-ExistingPath -Path $targetPath -TargetName $TargetName -Kind "agents-uninstall" | Out-Null
    } else {
        Remove-ExistingPath $targetPath
    }

    if ($DryRun) {
        Write-Info "[预演] 将卸载 agents：$targetPath"
        Add-Result $TargetName "agents" $targetPath "预演" "将删除"
        return
    }

    if (Test-Path -LiteralPath $targetPath) {
        Remove-ExistingPath $targetPath
    }

    Write-Ok "[完成] 已卸载 $TargetName / agents：$targetPath"
    Add-Result $TargetName "agents" $targetPath "成功" "已删除"
}

function Process-Target {
    param(
        [pscustomobject]$Target,
        [switch]$DoUninstall
    )

    $targetName = [string]$Target.name

    Write-Info ""
    Write-Info "[dotfiles] 正在处理：$targetName"

    if ($Target.skills) {
        foreach ($skill in @($Target.skills)) {
            $skillName = if ($skill.name) { [string]$skill.name } else { "skills" }

            try {
                if ($DoUninstall) {
                    Uninstall-SkillsEntry -TargetName $targetName -Dst ([string]$skill.path) -SkillName $skillName
                } else {
                    Install-SkillsEntry -TargetName $targetName -Dst ([string]$skill.path) -SkillName $skillName
                }
            } catch {
                $targetPath = Join-Path (Expand-PathTemplate ([string]$skill.path)) $skillName
                Write-ErrMsg "[失败] $targetName / skills：$($_.Exception.Message)"
                Add-Result $targetName "skills" $targetPath "失败" $_.Exception.Message
            }
        }
    }

    if ($Target.agents) {
        foreach ($agent in @($Target.agents)) {
            $agentName = if ($agent.name) { [string]$agent.name } else { "AGENTS.md" }

            try {
                if ($DoUninstall) {
                    Uninstall-AgentsEntry -TargetName $targetName -Dst ([string]$agent.path) -Name $agentName
                } else {
                    Install-AgentsEntry -TargetName $targetName -Dst ([string]$agent.path) -Name $agentName
                }
            } catch {
                $targetPath = Join-Path (Expand-PathTemplate ([string]$agent.path)) $agentName
                Write-ErrMsg "[失败] $targetName / agents：$($_.Exception.Message)"
                Add-Result $targetName "agents" $targetPath "失败" $_.Exception.Message
            }
        }
    }
}

function Show-Summary {
    Write-Host ""
    Write-Host "================ 执行结果汇总 ================" -ForegroundColor Magenta

    if ($script:Results.Count -eq 0) {
        Write-Host "没有产生任何执行结果。" -ForegroundColor Yellow
    } else {
        $success = @($script:Results | Where-Object { $_.Status -eq "成功" }).Count
        $skipped = @($script:Results | Where-Object { $_.Status -eq "跳过" }).Count
        $preview = @($script:Results | Where-Object { $_.Status -eq "预演" }).Count
        $failed  = @($script:Results | Where-Object { $_.Status -eq "失败" }).Count

        Write-Host ("成功：{0}    跳过：{1}    预演：{2}    失败：{3}" -f $success, $skipped, $preview, $failed)

        foreach ($row in $script:Results) {
            $line = "[{0}] {1} / {2}`n  路径：{3}`n  说明：{4}" -f $row.Status, $row.Target, $row.Kind, $row.Path, $row.Message

            switch ($row.Status) {
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

    if ($script:VerifyResults.Count -eq 0) {
        if ($DryRun -or $Uninstall) {
            Write-Host "当前模式不进行安装后校验。" -ForegroundColor Yellow
        } else {
            Write-Host "没有产生任何校验结果。" -ForegroundColor Yellow
        }
    } else {
        $verifyOk = @($script:VerifyResults | Where-Object { $_.Status -eq "成功" }).Count
        $verifyFail = @($script:VerifyResults | Where-Object { $_.Status -eq "失败" }).Count
        Write-Host ("通过：{0}    失败：{1}" -f $verifyOk, $verifyFail)

        foreach ($row in $script:VerifyResults) {
            $line = "[{0}] {1} / {2}`n  路径：{3}`n  说明：{4}" -f $row.Status, $row.Target, $row.Kind, $row.Path, $row.Message
            switch ($row.Status) {
                "成功" { Write-Host $line -ForegroundColor Green }
                "失败" { Write-Host $line -ForegroundColor Red }
                default { Write-Host $line }
            }
        }
    }

    Write-Host "============================================" -ForegroundColor Magenta
}

function Show-TargetMenu {
    param([array]$Targets)

    Write-Host ""
    Write-Host "[dotfiles] 请选择目标，可多选（用逗号分隔）：" -ForegroundColor Cyan

    for ($i = 0; $i -lt $Targets.Count; $i++) {
        Write-Host ("{0}) {1}" -f ($i + 1), $Targets[$i].name)
    }

    Write-Host ("{0}) 全部" -f ($Targets.Count + 1))

    while ($true) {
        $inputText = Read-Host "请输入编号"
        if ([string]::IsNullOrWhiteSpace($inputText)) {
            Write-WarnMsg "请输入至少一个编号。"
            continue
        }

        $parts = $inputText.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
        $numbers = @()
        $valid = $true

        foreach ($part in $parts) {
            $n = 0
            if (-not [int]::TryParse($part, [ref]$n)) {
                $valid = $false
                break
            }
            $numbers += $n
        }

        if (-not $valid) {
            Write-WarnMsg "输入格式不正确，请输入数字编号，例如：1,3"
            continue
        }

        if ($numbers -contains ($Targets.Count + 1)) {
            return @($Targets)
        }

        $selected = @()
        foreach ($n in ($numbers | Select-Object -Unique)) {
            if ($n -lt 1 -or $n -gt $Targets.Count) {
                $valid = $false
                break
            }
            $selected += $Targets[$n - 1]
        }

        if (-not $valid -or $selected.Count -eq 0) {
            Write-WarnMsg "编号超出范围，请重新输入。"
            continue
        }

        return @($selected)
    }
}

function Invoke-InteractiveMode {
    param([array]$AllTargets)

    Write-Host ""
    Write-Host "================ dotfiles 安装器 ================" -ForegroundColor Magenta
    Write-Host "1) 安装"
    Write-Host "2) 卸载"
    Write-Host "3) 预演安装"
    Write-Host "4) 预演卸载"
    Write-Host "5) 退出"
    Write-Host "===============================================" -ForegroundColor Magenta

    $mode = $null
    while (-not $mode) {
        $choice = Read-Host "请选择操作"
        switch ($choice) {
            "1" { $mode = @{ Uninstall = $false; DryRun = $false } }
            "2" { $mode = @{ Uninstall = $true;  DryRun = $false } }
            "3" { $mode = @{ Uninstall = $false; DryRun = $true  } }
            "4" { $mode = @{ Uninstall = $true;  DryRun = $true  } }
            "5" { return $null }
            default { Write-WarnMsg "请输入 1-5 之间的编号。" }
        }
    }

    $selectedTargets = Show-TargetMenu -Targets $AllTargets

    $forceAnswer = Read-Host "是否允许接管已存在的陌生目标？(y/N)"
    $forceFlag = $false
    if ($forceAnswer -match '^(y|Y|yes|YES)$') {
        $forceFlag = $true
    }

    $targetNamesSelected = @($selectedTargets | ForEach-Object { [string]$_.name })

    Write-Host ""
    Write-Host "[dotfiles] 本次执行配置：" -ForegroundColor Cyan
    Write-Host ("  模式：{0}" -f ($(if ($mode.Uninstall) { if ($mode.DryRun) { "预演卸载" } else { "卸载" } } else { if ($mode.DryRun) { "预演安装" } else { "安装" } })))
    Write-Host ("  接管陌生目标：{0}" -f ($(if ($forceFlag) { "是（会先备份再替换）" } else { "否" })))
    Write-Host ("  目标：{0}" -f ($targetNamesSelected -join ", "))

    $confirm = Read-Host "确认执行？(Y/n)"
    if ($confirm -match '^(n|N|no|NO)$') {
        Write-WarnMsg "[dotfiles] 已取消。"
        return $null
    }

    return @{
        DryRun      = [bool]$mode.DryRun
        Force       = [bool]$forceFlag
        Uninstall   = [bool]$mode.Uninstall
        TargetNames = $targetNamesSelected
    }
}

try {
    Ensure-Elevated

    $allTargets = Load-Targets

    if (-not $TargetNames -and -not $PSBoundParameters.ContainsKey('DryRun') -and -not $PSBoundParameters.ContainsKey('Uninstall') -and -not $PSBoundParameters.ContainsKey('Force')) {
        $interactive = Invoke-InteractiveMode -AllTargets $allTargets
        if ($null -eq $interactive) {
            return
        }

        $DryRun = [bool]$interactive.DryRun
        $Force = [bool]$interactive.Force
        $Uninstall = [bool]$interactive.Uninstall
        $TargetNames = @($interactive.TargetNames)
    }

    if (-not $Uninstall) {
        if (-not (Test-Path -LiteralPath $SKILLS)) {
            throw "[dotfiles] 未找到 skills 目录：$SKILLS"
        }

        if (-not (Test-Path -LiteralPath $AGENTS)) {
            throw "[dotfiles] 未找到 AGENTS.md：$AGENTS"
        }
    }

    $selectedTargets = @($allTargets)

    if ($TargetNames -and $TargetNames.Count -gt 0) {
        $lookup = @{}
        foreach ($name in $TargetNames) {
            $lookup[$name] = $true
        }

        $selectedTargets = @($allTargets | Where-Object { $lookup.ContainsKey([string]$_.name) })

        foreach ($name in $TargetNames) {
            if (-not (@($selectedTargets | Where-Object { [string]$_.name -eq $name }).Count)) {
                Write-WarnMsg "[dotfiles] 配置中未找到目标：$name"
            }
        }
    }

    if ($selectedTargets.Count -eq 0) {
        throw "[dotfiles] 没有可执行的目标。"
    }

    if ($DryRun) {
        if ($Uninstall) {
            Write-Info "[dotfiles] 当前为预演模式：只显示将卸载什么，不会真的删除。"
        } else {
            Write-Info "[dotfiles] 当前为预演模式：只显示将安装什么，不会真的修改。"
        }
    }

    if ($Force) {
        Write-WarnMsg "[dotfiles] 已启用 -Force：遇到陌生目标时，会先备份到 $env:USERPROFILE\.dotfiles-backup 再替换。"
    }

    if ($Uninstall) {
        Write-WarnMsg "[dotfiles] 当前为卸载模式。"
    }

    foreach ($target in $selectedTargets) {
        Process-Target -Target $target -DoUninstall:$Uninstall
    }

    Show-Summary
} catch {
    Write-ErrMsg ""
    Write-ErrMsg "[dotfiles] 致命错误：$($_.Exception.Message)"
    Write-ErrMsg ""
} finally {
    if (-not $NoPause) {
        Write-Host ""
        Read-Host "按回车退出"
    }
}
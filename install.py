#!/usr/bin/env python3
"""dotfiles installer — links skills and copies AGENTS.md to AI tool directories."""

import argparse
import filecmp
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, IntPrompt, Prompt
    from rich.table import Table
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "rich", "-q"],
        stdout=subprocess.DEVNULL,
    )
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, IntPrompt, Prompt
    from rich.table import Table

# ---------------------------------------------------------------------------
# Path resolution — only assumption: install.py and skills/ are siblings
# ---------------------------------------------------------------------------

DOTFILES = Path(__file__).resolve().parent
SKILLS_DIR = DOTFILES / "skills"
AGENTS_FILE = DOTFILES / "AGENTS.md"
DEFAULT_CONFIG = DOTFILES / "targets.json"

IS_WINDOWS = platform.system() == "Windows"
HOME_STR = str(Path.home())

console = Console()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STATUS_OK = "ok"
STATUS_SKIP = "skip"
STATUS_PREVIEW = "preview"
STATUS_FAIL = "fail"

STATUS_LABEL = {
    STATUS_OK: "[green]OK[/green]",
    STATUS_SKIP: "[yellow]--[/yellow]",
    STATUS_PREVIEW: "[cyan]DRY[/cyan]",
    STATUS_FAIL: "[red]FAIL[/red]",
}


def short_path(p: str) -> str:
    """Replace home directory prefix with ~ for compact display."""
    if p.startswith(HOME_STR):
        return "~" + p[len(HOME_STR):].replace("\\", "/")
    return p


def get_skills() -> list[str]:
    """Enumerate installable skill directory names, excluding dot-prefixed dirs."""
    return sorted(
        d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
    )


def load_config(config_path: Path) -> list[dict]:
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)["targets"]


def expand_path(template: str) -> Path:
    return Path(template.replace("{HOME}", HOME_STR))


def create_dir_link(link: Path, target: Path):
    """Create a directory symlink (Linux/macOS) or junction (Windows)."""
    if IS_WINDOWS:
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=True,
            capture_output=True,
        )
    else:
        link.symlink_to(target)


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    if IS_WINDOWS:
        return getattr(path, "is_junction", lambda: False)()
    return False


def is_our_link(link: Path, expected_target: Path) -> bool:
    """Check if *link* is a symlink/junction pointing to *expected_target*."""
    try:
        if not _is_link_or_junction(link):
            return False
        return link.resolve() == expected_target.resolve()
    except (OSError, ValueError):
        return False


def backup(path: Path):
    """Rename *path* to .bak (append timestamp if .bak already exists)."""
    bak = path.with_suffix(path.suffix + ".bak")
    if bak.exists():
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = path.with_suffix(f"{path.suffix}.bak.{ts}")
    path.rename(bak)
    return bak


def is_our_agents_copy(target_path: Path) -> bool:
    """Check if *target_path* is a byte-identical copy of our AGENTS.md."""
    if not target_path.is_file() or not AGENTS_FILE.is_file():
        return False
    return filecmp.cmp(str(target_path), str(AGENTS_FILE), shallow=False)


def _emit(results: list, path: str, status: str, detail: str):
    """Append result AND print live if it's not a skip."""
    results.append((path, status, detail))
    if status != STATUS_SKIP:
        console.print(f"  {STATUS_LABEL[status]}  {short_path(path)}  [dim]{detail}[/dim]")


# ---------------------------------------------------------------------------
# Scan — detect conflicts before asking user about --force
# ---------------------------------------------------------------------------


def scan_conflicts(selected: list[dict], skills: list[str], *, uninstall: bool) -> list[str]:
    """Return list of paths with non-managed existing content."""
    conflicts = []
    for entry in selected:
        for s_entry in entry.get("skills", []):
            container = expand_path(s_entry["path"]) / s_entry.get("name", "skills")
            if _is_link_or_junction(container):
                try:
                    if container.resolve() == SKILLS_DIR.resolve():
                        continue
                except (OSError, ValueError):
                    pass

            for skill in skills:
                link = container / skill
                target = SKILLS_DIR / skill
                if (link.exists() or link.is_symlink()) and not is_our_link(link, target):
                    conflicts.append(str(link))

        if uninstall:
            for a_entry in entry.get("agents", []):
                dest = expand_path(a_entry["path"]) / a_entry.get("name", "AGENTS.md")
                if dest.exists() and not is_our_agents_copy(dest):
                    conflicts.append(str(dest))

    return conflicts


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def _migrate_old_junction(container: Path, dry_run: bool) -> str | None:
    """If *container* is a junction/symlink pointing to our SKILLS_DIR, replace it
    with a real directory (one-time migration from whole-dir junction to per-skill links)."""
    if not _is_link_or_junction(container):
        return None
    try:
        if container.resolve() != SKILLS_DIR.resolve():
            return None
    except (OSError, ValueError):
        return None

    if dry_run:
        return "旧版整目录链接 -> 逐 skill 链接"

    container.unlink()
    container.mkdir(parents=True, exist_ok=True)
    return "已迁移: 整目录链接 -> 逐 skill 链接"


def install_skills(entry: dict, skills: list[str], *, dry_run=False, force=False) -> list[tuple]:
    results = []
    for s_entry in entry.get("skills", []):
        container = expand_path(s_entry["path"]) / s_entry.get("name", "skills")

        migrating = _migrate_old_junction(container, dry_run)
        if migrating:
            status = STATUS_PREVIEW if dry_run else STATUS_OK
            _emit(results, str(container), status, migrating)

        if not dry_run:
            container.mkdir(parents=True, exist_ok=True)

        for skill in skills:
            link = container / skill
            target = SKILLS_DIR / skill

            if not migrating and is_our_link(link, target):
                _emit(results, str(link), STATUS_SKIP, "已是正确链接")
                continue

            if not migrating and (link.exists() or link.is_symlink()):
                if not force:
                    _emit(results, str(link), STATUS_SKIP, "已存在非受管内容")
                    continue
                if dry_run:
                    _emit(results, str(link), STATUS_PREVIEW, "将备份并替换")
                    continue
                bak = backup(link)
                create_dir_link(link, target)
                _emit(results, str(link), STATUS_OK, f"已备份到 {bak.name} 并重建")
                continue

            if dry_run:
                _emit(results, str(link), STATUS_PREVIEW, f"将创建链接")
                continue

            try:
                create_dir_link(link, target)
                _emit(results, str(link), STATUS_OK, "已创建链接")
            except Exception as e:
                _emit(results, str(link), STATUS_FAIL, str(e))

    return results


def install_agents(entry: dict, *, dry_run=False, force=False) -> list[tuple]:
    results = []
    for a_entry in entry.get("agents", []):
        dest = expand_path(a_entry["path"]) / a_entry.get("name", "AGENTS.md")

        if is_our_agents_copy(dest):
            _emit(results, str(dest), STATUS_SKIP, "已是最新副本")
            continue

        if dry_run:
            label = "将更新" if dest.exists() else "将写入"
            _emit(results, str(dest), STATUS_PREVIEW, label)
            continue

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(AGENTS_FILE), str(dest))
            _emit(results, str(dest), STATUS_OK, "已写入")
        except Exception as e:
            _emit(results, str(dest), STATUS_FAIL, str(e))

    return results


def uninstall_skills(entry: dict, skills: list[str], *, dry_run=False, force=False) -> list[tuple]:
    results = []
    for s_entry in entry.get("skills", []):
        container = expand_path(s_entry["path"]) / s_entry.get("name", "skills")

        for skill in skills:
            link = container / skill

            if not link.exists() and not link.is_symlink():
                _emit(results, str(link), STATUS_SKIP, "不存在")
                continue

            if is_our_link(link, SKILLS_DIR / skill):
                if dry_run:
                    _emit(results, str(link), STATUS_PREVIEW, "将删除")
                    continue
                if _is_link_or_junction(link):
                    link.unlink()
                else:
                    shutil.rmtree(str(link))
                _emit(results, str(link), STATUS_OK, "已删除")
                continue

            if not force:
                _emit(results, str(link), STATUS_SKIP, "非受管内容")
                continue

            if dry_run:
                _emit(results, str(link), STATUS_PREVIEW, "将备份并删除")
                continue

            bak = backup(link)
            _emit(results, str(link), STATUS_OK, f"已备份到 {bak.name} 并删除")

    return results


def uninstall_agents(entry: dict, *, dry_run=False, force=False) -> list[tuple]:
    results = []
    for a_entry in entry.get("agents", []):
        dest = expand_path(a_entry["path"]) / a_entry.get("name", "AGENTS.md")

        if not dest.exists():
            _emit(results, str(dest), STATUS_SKIP, "不存在")
            continue

        ours = is_our_agents_copy(dest)
        if not ours and not force:
            _emit(results, str(dest), STATUS_SKIP, "非受管内容")
            continue

        if dry_run:
            _emit(results, str(dest), STATUS_PREVIEW, "将删除")
            continue

        try:
            if not ours:
                backup(dest)
            dest.unlink()
            _emit(results, str(dest), STATUS_OK, "已删除")
        except Exception as e:
            _emit(results, str(dest), STATUS_FAIL, str(e))

    return results


# ---------------------------------------------------------------------------
# UX
# ---------------------------------------------------------------------------


def print_summary(results_by_target: dict[str, list[tuple]]):
    """Compact summary: per-target counts, only list FAIL items explicitly."""
    console.print()

    grand = {STATUS_OK: 0, STATUS_SKIP: 0, STATUS_PREVIEW: 0, STATUS_FAIL: 0}
    failures = []

    for target_name, results in results_by_target.items():
        counts = {STATUS_OK: 0, STATUS_SKIP: 0, STATUS_PREVIEW: 0, STATUS_FAIL: 0}
        for path, status, detail in results:
            counts[status] = counts.get(status, 0) + 1
            grand[status] = grand.get(status, 0) + 1
            if status == STATUS_FAIL:
                failures.append((target_name, path, detail))

        parts = []
        for s, label in [(STATUS_OK, "[green]OK[/green]"), (STATUS_PREVIEW, "[cyan]DRY[/cyan]"),
                         (STATUS_SKIP, "[yellow]skip[/yellow]"), (STATUS_FAIL, "[red]FAIL[/red]")]:
            if counts.get(s):
                parts.append(f"{label} {counts[s]}")
        console.print(f"  [bold]{target_name}[/bold]  {'  '.join(parts)}")

    if failures:
        console.print()
        table = Table(title="[red]Failed[/red]", show_lines=True)
        table.add_column("Target", style="bold")
        table.add_column("Path")
        table.add_column("Error")
        for tname, path, detail in failures:
            table.add_row(tname, short_path(path), detail)
        console.print(table)

    total_parts = []
    for s, label in [(STATUS_OK, "OK"), (STATUS_PREVIEW, "DRY"), (STATUS_SKIP, "skip"), (STATUS_FAIL, "FAIL")]:
        if grand.get(s):
            total_parts.append(f"{label}: {grand[s]}")
    console.print(f"\n  [dim]{'    '.join(total_parts)}[/dim]\n")


def interactive_mode(all_targets: list[dict], skills: list[str]) -> dict:
    """Numeric prompts, lazy force detection."""
    console.print(Panel(
        f"[bold]dotfiles[/bold]  {DOTFILES}\n"
        f"skills: {len(skills)} 个    targets: {len(all_targets)} 个",
        title="dotfiles installer",
    ))

    # --- mode ---
    modes = ["安装", "卸载", "预演安装", "预演卸载"]
    console.print()
    for i, m in enumerate(modes, 1):
        console.print(f"  {i}) {m}")
    choice = IntPrompt.ask("\n操作", default=1)
    while choice < 1 or choice > len(modes):
        choice = IntPrompt.ask("请输入 1-4", default=1)
    mode = modes[choice - 1]

    # --- targets ---
    console.print()
    for i, t in enumerate(all_targets, 1):
        console.print(f"  {i}) {t['name']}")
    all_idx = len(all_targets) + 1
    console.print(f"  {all_idx}) 全部")
    selection = Prompt.ask("\n选择目标 (逗号分隔)", default=str(all_idx))
    parts = [p.strip() for p in selection.split(",") if p.strip()]
    selected = []
    for p in parts:
        if not p.isdigit():
            continue
        n = int(p)
        if n == all_idx:
            selected = list(all_targets)
            break
        if 1 <= n <= len(all_targets):
            t = all_targets[n - 1]
            if t not in selected:
                selected.append(t)
    if not selected:
        selected = list(all_targets)

    uninstall = mode in ("卸载", "预演卸载")
    dry_run = mode in ("预演安装", "预演卸载")

    # --- lazy force: only ask if conflicts detected ---
    force = False
    conflicts = scan_conflicts(selected, skills, uninstall=uninstall)
    if conflicts:
        console.print(f"\n[yellow]发现 {len(conflicts)} 个非受管内容：[/yellow]")
        shown = conflicts[:5]
        for c in shown:
            console.print(f"  [dim]{short_path(c)}[/dim]")
        if len(conflicts) > 5:
            console.print(f"  [dim]...还有 {len(conflicts) - 5} 个[/dim]")
        force = Confirm.ask("\n覆盖这些内容？(先备份)", default=False)

    # --- confirm ---
    console.print(Panel(
        f"模式: {'卸载' if uninstall else '安装'}{'  (预演)' if dry_run else ''}\n"
        f"目标: {', '.join(t['name'] for t in selected)}"
        + (f"\n覆盖: 是" if force else ""),
        title="确认",
    ))

    if not Confirm.ask("执行？", default=True):
        console.print("[yellow]已取消。[/yellow]")
        sys.exit(0)

    return {
        "selected": selected,
        "uninstall": uninstall,
        "dry_run": dry_run,
        "force": force,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="dotfiles installer")
    parser.add_argument("--dry-run", action="store_true", help="预演，不真正修改")
    parser.add_argument("--uninstall", action="store_true", help="卸载模式")
    parser.add_argument("--force", action="store_true", help="覆盖非受管内容（先备份）")
    parser.add_argument("--target", action="append", dest="targets", help="指定目标名称，可重复")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="配置文件路径")
    args = parser.parse_args()

    if not SKILLS_DIR.is_dir():
        console.print(f"[red]未找到 skills 目录：{SKILLS_DIR}[/red]")
        sys.exit(1)
    if not args.uninstall and not AGENTS_FILE.is_file():
        console.print(f"[red]未找到 AGENTS.md：{AGENTS_FILE}[/red]")
        sys.exit(1)
    if not args.config.is_file():
        console.print(f"[red]未找到配置文件：{args.config}[/red]")
        sys.exit(1)

    all_targets = load_config(args.config)
    skills = get_skills()
    is_interactive = len(sys.argv) == 1

    if is_interactive:
        cfg = interactive_mode(all_targets, skills)
        selected = cfg["selected"]
        uninstall = cfg["uninstall"]
        dry_run = cfg["dry_run"]
        force = cfg["force"]
    else:
        if args.targets:
            selected = [t for t in all_targets if t["name"] in args.targets]
            if not selected:
                console.print("[red]未匹配到任何目标。[/red]")
                sys.exit(1)
        else:
            selected = all_targets
        uninstall = args.uninstall
        dry_run = args.dry_run
        force = args.force

    if dry_run:
        console.print("[cyan]预演模式：不会真正修改。[/cyan]")

    console.print()
    results_by_target: dict[str, list[tuple]] = {}

    for entry in selected:
        name = entry["name"]
        console.print(f"[bold]{name}[/bold]")
        results = []

        if uninstall:
            results += uninstall_skills(entry, skills, dry_run=dry_run, force=force)
            results += uninstall_agents(entry, dry_run=dry_run, force=force)
        else:
            results += install_skills(entry, skills, dry_run=dry_run, force=force)
            results += install_agents(entry, dry_run=dry_run, force=force)

        results_by_target[name] = results
        console.print()

    print_summary(results_by_target)


if __name__ == "__main__":
    main()

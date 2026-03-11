#!/usr/bin/env python3
"""
Notion Manager - Core Operations
Commands: snapshot, snapshot-info, wordlist, resolve,
          structure, read, search,
          create, append, move
"""

import argparse
import sys
import re
import json
import os
from datetime import datetime, timezone
import requests

BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
DEFAULT_SNAPSHOT_PATH = os.path.expanduser("~/.notion_workspace_snapshot.json")


# ── HTTP ──────────────────────────────────────────────────────────────────────

def get_headers(token):
    return {
        "Authorization": f"Bearer {token.strip()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def api_get(token, path):
    r = requests.get(f"{BASE_URL}{path}", headers=get_headers(token))
    r.raise_for_status()
    return r.json()

def api_post(token, path, body):
    r = requests.post(f"{BASE_URL}{path}", headers=get_headers(token), json=body)
    r.raise_for_status()
    return r.json()

def api_patch(token, path, body):
    r = requests.patch(f"{BASE_URL}{path}", headers=get_headers(token), json=body)
    r.raise_for_status()
    return r.json()


# ── 基础工具 ──────────────────────────────────────────────────────────────────

def looks_like_id(s):
    return bool(re.fullmatch(r"[a-f0-9\-]{32,36}", s.strip()))

def looks_like_url(s):
    return "notion.so" in s

def format_page_id(raw_id):
    url_match = re.search(r"notion\.so/(?:[^/]+/)?(?:[^-]+-)?([a-f0-9]{32})", raw_id)
    if url_match:
        clean = url_match.group(1)
    else:
        clean = raw_id.replace("-", "").strip()
        match = re.search(r"([a-f0-9]{32})", clean)
        if match:
            clean = match.group(1)
    if len(clean) != 32:
        raise ValueError(f"无法识别 page ID: {raw_id}")
    return f"{clean[0:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:32]}"

def get_page_title(page):
    props = page.get("properties", {})
    for key in ["title", "Name", "标题"]:
        if key in props:
            arr = props[key].get("title", [])
            if arr:
                return "".join(t.get("plain_text", "") for t in arr)
    if "child_page" in page:
        return page["child_page"].get("title", "(无标题)")
    return "(无标题)"

def rich_text_to_str(arr):
    return "".join(t.get("plain_text", "") for t in arr)


# ── 分页获取所有子块 ──────────────────────────────────────────────────────────

def get_all_children(token, block_id):
    results = []
    cursor = None
    while True:
        path = f"/blocks/{block_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        try:
            data = api_get(token, path)
        except Exception as e:
            print(f"[warning] 获取块出错 ({block_id}): {e}", file=sys.stderr)
            break
        results.extend(data.get("results", []))
        if data.get("has_more") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            break
    return results


# ── 📌 Callout 提取 ───────────────────────────────────────────────────────────

def extract_pin_callout(token, page_id):
    """
    读取页面前几个块，找 📌 emoji 的 callout，
    提取"不可替代性"和"边界"字段。
    返回 {"indispensable": str, "boundary": str} 或 None
    """
    try:
        # 只取前 10 个块，容器页的 callout 都在顶部
        data = api_get(token, f"/blocks/{page_id}/children?page_size=10")
    except Exception:
        return None

    for block in data.get("results", []):
        if block.get("type") != "callout":
            continue
        callout = block.get("callout", {})
        icon = callout.get("icon", {})
        emoji = icon.get("emoji", "") if icon.get("type") == "emoji" else ""
        if emoji != "📌":
            continue

        # 找到了 📌 callout，提取正文
        text = rich_text_to_str(callout.get("rich_text", []))

        # 解析字段（格式：不可替代性：xxx\n边界：xxx）
        indispensable = ""
        boundary = ""
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("不可替代性"):
                indispensable = re.sub(r"^不可替代性[：:]\s*", "", line)
            elif line.startswith("边界"):
                boundary = re.sub(r"^边界[：:]\s*", "", line)

        return {
            "indispensable": indispensable,
            "boundary": boundary,
            "raw": text,
        }

    return None  # 没有 📌 callout → 内容页


# ── 快照 ──────────────────────────────────────────────────────────────────────

def load_snapshot(path=DEFAULT_SNAPSHOT_PATH):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_snapshot(data, path=DEFAULT_SNAPSHOT_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cmd_snapshot(token, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    print("开始爬取工作区...", file=sys.stderr)

    # 拉取所有页面
    all_pages = []
    cursor = None
    while True:
        body = {"page_size": 100, "filter": {"value": "page", "property": "object"}}
        if cursor:
            body["start_cursor"] = cursor
        try:
            data = api_post(token, "/search", body)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr); sys.exit(1)
        all_pages.extend(data.get("results", []))
        if data.get("has_more") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            break

    print(f"发现 {len(all_pages)} 个页面，构建索引中...", file=sys.stderr)

    page_index = {}
    for page in all_pages:
        pid = page.get("id", "")
        title = get_page_title(page)
        url = page.get("url", "")
        parent = page.get("parent", {})
        ptype = parent.get("type", "")
        parent_id = parent.get("page_id", "") if ptype == "page_id" else "__workspace__"

        page_index[pid] = {
            "title": title,
            "parent_id": parent_id,
            "url": url,
            "depth": 0,
            "children": [],
            "callout": None,   # 待填充
            "is_container": False,
        }

    # 建父子关系
    for pid, info in page_index.items():
        par = info["parent_id"]
        if par and par != "__workspace__" and par in page_index:
            if pid not in page_index[par]["children"]:
                page_index[par]["children"].append(pid)

    # 计算 depth
    def calc_depth(pid, visited=None):
        if visited is None:
            visited = set()
        if pid in visited:
            return 0
        visited.add(pid)
        info = page_index.get(pid)
        if not info:
            return 0
        par = info["parent_id"]
        if not par or par == "__workspace__" or par not in page_index:
            info["depth"] = 0
            return 0
        d = calc_depth(par, visited) + 1
        info["depth"] = d
        return d

    for pid in page_index:
        calc_depth(pid)

    # 提取 📌 Callout（只对有子页面的页面检测，降低 API 请求量）
    container_candidates = [
        pid for pid, info in page_index.items()
        if info["children"] or info["depth"] <= 2
    ]
    print(f"检测容器页 Callout（{len(container_candidates)} 个候选）...", file=sys.stderr)

    for pid in container_candidates:
        callout = extract_pin_callout(token, pid)
        if callout:
            page_index[pid]["callout"] = callout
            page_index[pid]["is_container"] = True

    snapshot = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(page_index),
        "pages": page_index,
    }
    save_snapshot(snapshot, snapshot_path)

    container_count = sum(1 for p in page_index.values() if p["is_container"])
    print(f"\n✅ 快照完成")
    print(f"   共索引 {len(page_index)} 个页面")
    print(f"   其中容器页（含 📌 Callout）: {container_count} 个")
    print(f"   保存至: {snapshot_path}")


def cmd_snapshot_info(snapshot_path=DEFAULT_SNAPSHOT_PATH):
    snap = load_snapshot(snapshot_path)
    if not snap:
        print(f"快照不存在：{snapshot_path}")
        print("请先运行: python notion_ops.py snapshot")
        return
    container_count = sum(1 for p in snap["pages"].values() if p.get("is_container"))
    print(f"快照状态")
    print(f"  路径:     {snapshot_path}")
    print(f"  更新时间: {snap.get('updated_at', '未知')}")
    print(f"  页面总数: {snap.get('total', len(snap.get('pages', {})))}")
    print(f"  容器页数: {container_count}")


# ── 词表 ──────────────────────────────────────────────────────────────────────

def cmd_wordlist(snapshot_path=DEFAULT_SNAPSHOT_PATH):
    """
    输出所有容器页的词表，供 AI 执行归类协议用。
    格式设计为对 AI 友好的结构化文本。
    """
    snap = load_snapshot(snapshot_path)
    if not snap:
        print("快照不存在，请先运行 snapshot。")
        return

    containers = [
        (pid, info) for pid, info in snap["pages"].items()
        if info.get("is_container") and info.get("callout")
    ]

    if not containers:
        print("暂无容器页（没有找到含 📌 Callout 的页面）。")
        return

    # 按 depth 排序，骨架层在前
    containers.sort(key=lambda x: (x[1]["depth"], x[1]["title"]))

    print(f"# 工作区词表\n")
    print(f"更新时间: {snap.get('updated_at', '未知')}")
    print(f"容器页共 {len(containers)} 个\n")
    print("---\n")

    for pid, info in containers:
        callout = info["callout"]
        indent = "  " * info["depth"]
        print(f"{indent}## {info['title']}")
        print(f"{indent}ID: {pid}")
        print(f"{indent}URL: {info.get('url', '')}")
        print(f"{indent}不可替代性: {callout.get('indispensable', '（未填写）')}")
        print(f"{indent}边界: {callout.get('boundary', '（未填写）')}")
        # 列出直接子容器（帮 AI 理解层级）
        child_containers = [
            snap["pages"][cid]["title"]
            for cid in info.get("children", [])
            if snap["pages"].get(cid, {}).get("is_container")
        ]
        if child_containers:
            print(f"{indent}子容器: {', '.join(child_containers)}")
        print()


# ── 名字解析 ──────────────────────────────────────────────────────────────────

def resolve_title_to_id(title_query, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    snap = load_snapshot(snapshot_path)
    if not snap:
        return []
    query = title_query.strip().lower()
    results = []
    for pid, info in snap["pages"].items():
        t = info["title"].lower()
        if t == query:
            results.append((0, pid, info["title"], info.get("url", ""), info.get("depth", 0)))
        elif query in t or t in query:
            results.append((1, pid, info["title"], info.get("url", ""), info.get("depth", 0)))
    results.sort(key=lambda x: (x[0], x[4]))
    return results

def cmd_resolve(title_query, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    results = resolve_title_to_id(title_query, snapshot_path)
    if not results:
        snap = load_snapshot(snapshot_path)
        print("快照不存在，请先运行 snapshot。" if not snap else f'未找到匹配 "{title_query}" 的页面。')
        return
    print(f'匹配 "{title_query}" 的页面：\n')
    for score, pid, title, url, depth in results:
        tag = "✦ 精确" if score == 0 else "  模糊"
        print(f"{tag}  📄 {title}  (depth={depth})")
        print(f"        ID:  {pid}")
        print(f"        URL: {url}\n")

def smart_resolve_id(raw, snapshot_path=DEFAULT_SNAPSHOT_PATH, token=None):
    if looks_like_url(raw):
        return format_page_id(raw)
    if looks_like_id(raw):
        return format_page_id(raw)

    results = resolve_title_to_id(raw, snapshot_path)
    if not results:
        if token:
            print(f'快照中未找到 "{raw}"，尝试在线搜索...', file=sys.stderr)
            body = {"query": raw, "page_size": 5, "filter": {"value": "page", "property": "object"}}
            try:
                data = api_post(token, "/search", body)
                items = data.get("results", [])
                if len(items) == 1:
                    return items[0]["id"]
                elif len(items) > 1:
                    print(f'找到多个匹配，请指定：')
                    for item in items:
                        print(f"  📄 {get_page_title(item)}  [{item['id']}]")
                    sys.exit(1)
            except Exception:
                pass
        print(f'无法解析 "{raw}"，请提供 page ID 或 URL，或先运行 snapshot。', file=sys.stderr)
        sys.exit(1)

    if len(results) == 1 or results[0][0] == 0:
        chosen = results[0]
        print(f'解析 "{raw}" → {chosen[2]}  [{chosen[1]}]', file=sys.stderr)
        return chosen[1]

    print(f'"{raw}" 有多个匹配，请指定：\n')
    for _, pid, title, url, depth in results[:8]:
        print(f"  📄 {title}  (depth={depth})  [{pid}]")
    sys.exit(1)


# ── Structure / Read / Search ─────────────────────────────────────────────────

def list_children_tree(token, block_id, indent=0, max_depth=3):
    if indent >= max_depth:
        return ["  " * indent + "  [...] (更深层级，用 structure 单独展开)"]
    lines = []
    for block in get_all_children(token, block_id):
        btype = block.get("type", "")
        bid = block.get("id", "")
        if btype == "child_page":
            title = block["child_page"].get("title", "(无标题)")
            lines.append(f"{'  ' * indent}📄 {title}  [{bid}]")
            lines += list_children_tree(token, bid, indent + 1, max_depth)
        elif btype == "child_database":
            title = block["child_database"].get("title", "(无标题)")
            lines.append(f"{'  ' * indent}🗃️  {title} (Database)  [{bid}]")
    return lines

def cmd_structure(token, page_ref, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    page_id = smart_resolve_id(page_ref, snapshot_path, token)
    try:
        page = api_get(token, f"/pages/{page_id}")
        title = get_page_title(page)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)
    print(f"📄 {title}  [{page_id}]")
    lines = list_children_tree(token, page_id, indent=1)
    print("\n".join(lines) if lines else "  (没有子页面)")

def block_to_markdown(block, indent=0):
    btype = block.get("type", "")
    content = block.get(btype, {})
    prefix = "  " * indent

    def rt(arr):
        return rich_text_to_str(arr)

    if btype == "paragraph":
        return prefix + rt(content.get("rich_text", []))
    elif btype in ("heading_1", "heading_2", "heading_3"):
        return prefix + "#" * int(btype[-1]) + " " + rt(content.get("rich_text", []))
    elif btype == "bulleted_list_item":
        return prefix + "- " + rt(content.get("rich_text", []))
    elif btype == "numbered_list_item":
        return prefix + "1. " + rt(content.get("rich_text", []))
    elif btype == "to_do":
        checked = "x" if content.get("checked") else " "
        return prefix + f"- [{checked}] " + rt(content.get("rich_text", []))
    elif btype == "code":
        return f"```{content.get('language', '')}\n{rt(content.get('rich_text', []))}\n```"
    elif btype == "quote":
        return prefix + "> " + rt(content.get("rich_text", []))
    elif btype == "divider":
        return "---"
    elif btype == "child_page":
        return prefix + f"📄 [{content.get('title', '子页面')}]  [{block.get('id', '')}]"
    elif btype == "child_database":
        return prefix + f"🗃️  {content.get('title', 'Database')} (Database)"
    elif btype == "callout":
        icon = content.get("icon", {}).get("emoji", "💡")
        return prefix + f"{icon} {rt(content.get('rich_text', []))}"
    elif btype == "toggle":
        return prefix + f"▶ {rt(content.get('rich_text', []))}"
    return ""

def cmd_read(token, page_ref, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    page_id = smart_resolve_id(page_ref, snapshot_path, token)
    try:
        page = api_get(token, f"/pages/{page_id}")
        title = get_page_title(page)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)
    print(f"# {title}\n")
    blocks = get_all_children(token, page_id)
    for block in blocks:
        line = block_to_markdown(block)
        if line:
            print(line)
    if len(blocks) >= 100:
        print(f"\n<!-- 共 {len(blocks)} 个块（完整分页获取） -->")

def cmd_search(token, query, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    snap_results = resolve_title_to_id(query, snapshot_path)
    if snap_results:
        print(f'快照搜索 "{query}"（{len(snap_results)} 条）：\n')
        for score, pid, title, url, depth in snap_results[:10]:
            tag = "✦" if score == 0 else "~"
            print(f"{tag} 📄 {title}  (depth={depth})\n   ID:  {pid}\n   URL: {url}\n")
        return
    body = {"query": query, "page_size": 20, "filter": {"value": "page", "property": "object"}}
    try:
        data = api_post(token, "/search", body)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)
    results = data.get("results", [])
    if not results:
        print(f'未找到匹配 "{query}" 的页面。')
        return
    print(f'在线搜索 "{query}"（{len(results)} 条）：\n')
    for item in results:
        title = get_page_title(item)
        hint = "顶层" if item.get("parent", {}).get("type") == "workspace" else "子页面"
        print(f"📄 {title}  ({hint})\n   ID:  {item['id']}\n   URL: {item.get('url', '')}\n")


# ── 内容工具 ──────────────────────────────────────────────────────────────────

def load_content(content_arg, content_file_arg):
    if content_file_arg:
        with open(content_file_arg, "r", encoding="utf-8") as f:
            return f.read()
    return content_arg or ""

def markdown_to_blocks(text):
    blocks = []
    for line in text.split("\n"):
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3",
                           "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}})
        elif line.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2",
                           "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}})
        elif line.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1",
                           "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}})
        elif line.startswith("- [x] "):
            blocks.append({"object": "block", "type": "to_do",
                           "to_do": {"rich_text": [{"type": "text", "text": {"content": line[6:]}}], "checked": True}})
        elif line.startswith("- [ ] "):
            blocks.append({"object": "block", "type": "to_do",
                           "to_do": {"rich_text": [{"type": "text", "text": {"content": line[6:]}}], "checked": False}})
        elif line.startswith("- "):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}})
        elif re.match(r"^\d+\. ", line):
            blocks.append({"object": "block", "type": "numbered_list_item",
                           "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": re.sub(r'^\d+\. ', '', line)}}]}})
        elif line.startswith("> "):
            blocks.append({"object": "block", "type": "quote",
                           "quote": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}})
        else:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}})
    return blocks

def write_blocks_in_batches(token, page_id, blocks):
    remaining = blocks
    total = 0
    while remaining:
        batch = remaining[:100]
        api_patch(token, f"/blocks/{page_id}/children", {"children": batch})
        total += len(batch)
        remaining = remaining[100:]
    return total

def update_snapshot_add(page_id, title, parent_id, url,
                        is_container=False, callout=None,
                        snapshot_path=DEFAULT_SNAPSHOT_PATH):
    snap = load_snapshot(snapshot_path)
    if not snap:
        return
    parent_depth = snap["pages"].get(parent_id, {}).get("depth", 0)
    snap["pages"][page_id] = {
        "title": title,
        "parent_id": parent_id,
        "url": url,
        "depth": parent_depth + 1,
        "children": [],
        "is_container": is_container,
        "callout": callout,
    }
    if parent_id in snap["pages"]:
        if page_id not in snap["pages"][parent_id]["children"]:
            snap["pages"][parent_id]["children"].append(page_id)
    snap["total"] = len(snap["pages"])
    snap["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_snapshot(snap, snapshot_path)


# ── Create ────────────────────────────────────────────────────────────────────

def make_pin_callout_block(indispensable, boundary):
    """生成标准 📌 Callout 块"""
    text = f"不可替代性：{indispensable}\n边界：{boundary}"
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": "📌"},
            "color": "gray_background",
        }
    }

def cmd_create(token, parent_ref, title, content="",
               is_container=False, indispensable="", boundary="",
               snapshot_path=DEFAULT_SNAPSHOT_PATH):
    parent_id = smart_resolve_id(parent_ref, snapshot_path, token)
    all_blocks = []

    # 容器页：顶部插入 📌 Callout
    if is_container:
        if not indispensable or not boundary:
            print("Error: 容器页必须提供 --indispensable 和 --boundary", file=sys.stderr)
            sys.exit(1)
        all_blocks.append(make_pin_callout_block(indispensable, boundary))

    if content:
        all_blocks.extend(markdown_to_blocks(content))

    body = {
        "parent": {"page_id": parent_id},
        "properties": {"title": {"title": [{"type": "text", "text": {"content": title}}]}},
    }
    if all_blocks:
        body["children"] = all_blocks[:100]

    try:
        result = api_post(token, "/pages", body)
        new_id = result["id"]
        url = result.get("url", "")
        if len(all_blocks) > 100:
            write_blocks_in_batches(token, new_id, all_blocks[100:])

        callout_data = {"indispensable": indispensable, "boundary": boundary} if is_container else None
        update_snapshot_add(new_id, title, parent_id, url,
                            is_container=is_container, callout=callout_data,
                            snapshot_path=snapshot_path)

        print(f"✅ 创建成功 {'（容器页）' if is_container else '（内容页）'}")
        print(f"   标题: {title}")
        print(f"   ID:   {new_id}")
        print(f"   URL:  {url}")
        if is_container:
            print(f"   不可替代性: {indispensable}")
            print(f"   边界: {boundary}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)


# ── Append / Move ─────────────────────────────────────────────────────────────

def cmd_append(token, page_ref, content, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    page_id = smart_resolve_id(page_ref, snapshot_path, token)
    all_blocks = markdown_to_blocks(content)
    if not all_blocks:
        print("内容为空，未追加任何内容。")
        return
    try:
        total = write_blocks_in_batches(token, page_id, all_blocks)
        print(f"✅ 已追加 {total} 个块到 [{page_id}]")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)

def cmd_move(token, page_ref, target_ref, snapshot_path=DEFAULT_SNAPSHOT_PATH):
    page_id = smart_resolve_id(page_ref, snapshot_path, token)
    target_parent_id = smart_resolve_id(target_ref, snapshot_path, token)
    try:
        page = api_get(token, f"/pages/{page_id}")
        title = get_page_title(page)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)

    raw_blocks = get_all_children(token, page_id)
    has_subpages = any(b.get("type") in ("child_page", "child_database") for b in raw_blocks)
    blocks = [{"object": "block", "type": b["type"], b["type"]: b.get(b["type"], {})}
              for b in raw_blocks if b.get("type") not in ("child_page", "child_database", "unsupported")]

    body = {
        "parent": {"page_id": target_parent_id},
        "properties": {"title": {"title": [{"type": "text", "text": {"content": title}}]}},
    }
    if blocks:
        body["children"] = blocks[:100]

    try:
        result = api_post(token, "/pages", body)
        new_id = result["id"]
        url = result.get("url", "")
        if len(blocks) > 100:
            write_blocks_in_batches(token, new_id, blocks[100:])
        update_snapshot_add(new_id, title, target_parent_id, url, snapshot_path=snapshot_path)
        print(f"✅ 已在目标位置创建: {title}  [{new_id}]")
        print(f"⚠️  原页面未删除，请在 Notion 界面手动确认后删除。")
        print(f"   原页面 ID: {page_id}")
        if has_subpages:
            print(f"⚠️  原页面含子页面，子页面不会被一并迁移（API 限制）。")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Notion Manager")
    parser.add_argument("command", choices=[
        "snapshot", "snapshot-info", "wordlist", "resolve",
        "structure", "read", "search",
        "create", "append", "move",
    ])
    parser.add_argument("--token")
    parser.add_argument("--page-id")
    parser.add_argument("--parent-id")
    parser.add_argument("--target-parent-id")
    parser.add_argument("--title")
    parser.add_argument("--content")
    parser.add_argument("--content-file")
    parser.add_argument("--query")
    parser.add_argument("--snapshot-path", default=DEFAULT_SNAPSHOT_PATH)
    # 容器页专用
    parser.add_argument("--container", action="store_true", help="创建为容器页（插入 📌 Callout）")
    parser.add_argument("--indispensable", default="", help="📌 Callout：不可替代性")
    parser.add_argument("--boundary", default="", help="📌 Callout：边界")
    args = parser.parse_args()

    # Token 优先级：--token > 环境变量 NOTION_TOKEN
    if not args.token:
        args.token = os.environ.get("NOTION_TOKEN")

    # 需要网络的命令必须有 token
    needs_token = {"snapshot", "structure", "read", "search", "create", "append", "move"}
    if args.command in needs_token and not args.token:
        print(
            "Error: 需要 Notion token。\n"
            "  方式一（推荐）：export NOTION_TOKEN=your_token_here\n"
            "  方式二：python notion_ops.py <command> --token your_token_here",
            file=sys.stderr,
        )
        sys.exit(1)

    sp = args.snapshot_path
    content = load_content(args.content, args.content_file)

    if args.command == "snapshot":
        cmd_snapshot(args.token, sp)
    elif args.command == "snapshot-info":
        cmd_snapshot_info(sp)
    elif args.command == "wordlist":
        cmd_wordlist(sp)
    elif args.command == "resolve":
        cmd_resolve(args.query or args.page_id, sp)
    elif args.command == "structure":
        cmd_structure(args.token, args.page_id, sp)
    elif args.command == "read":
        cmd_read(args.token, args.page_id, sp)
    elif args.command == "search":
        cmd_search(args.token, args.query, sp)
    elif args.command == "create":
        cmd_create(args.token, args.parent_id, args.title, content,
                   is_container=args.container,
                   indispensable=args.indispensable,
                   boundary=args.boundary,
                   snapshot_path=sp)
    elif args.command == "append":
        cmd_append(args.token, args.page_id, content, sp)
    elif args.command == "move":
        cmd_move(args.token, args.page_id, args.target_parent_id, sp)

if __name__ == "__main__":
    main()
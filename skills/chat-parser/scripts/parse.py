#!/usr/bin/env python3
"""
chat-parser: 把聊天导出文件转成标准会话数据对象

设计原则：代码只做客观统计，主观判断留给 AI。
- 做：格式适配、成员统计、时段分布、消息类型占比、@提及统计、完整原始消息
- 不做：词频分析、金句提取、关系判断、任何语义理解

输出：{会话名}_{开始日期}_{结束日期}_parsed.json
"""

import json
import re
import sys
from collections import Counter
from datetime import date as date_type
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_CN = timezone(timedelta(hours=8))

MSG_TYPE = {
    0:  "text",
    3:  "image",
    7:  "image_or_emoji",
    25: "quote_reply",
    34: "voice",
    43: "video",
    47: "emoji",
    49: "app",
    62: "short_video",
    80: "system",
    10000: "system",
    10002: "recall",
}

SYSTEM_KEYWORDS = (
    "recalled a message", "加入群聊", "撤回了一条消息",
    "修改群名", "拍了拍", "你已添加",
)


def ts_to_dt(ts):
    return datetime.fromtimestamp(ts, tz=TZ_CN)


def infer_chat_kind(meta):
    if meta.get("groupId") or meta.get("type") == "group":
        return "group"
    return "private"


def classify_msg_type(msg):
    t = msg.get("type", -1)
    if t == 7:
        content = msg.get("content", "")
        return "video" if "[视频]" in content else "image_or_emoji"
    return MSG_TYPE.get(t, "unknown_{}".format(t))


def is_system_msg(msg):
    t = msg.get("type", -1)
    if t in (80, 10000, 10002):
        return True
    sender = msg.get("sender", "")
    if "@chatroom" in sender and msg.get("accountName", "") == sender:
        return True
    content = msg.get("content", "") or ""
    return any(k in content for k in SYSTEM_KEYWORDS)


def extract_at_mentions(content):
    return re.findall(r"@([\w\u4e00-\u9fff\u2014\-]+)", content)


def parse_jsonl(filepath):
    meta = {}
    members = {}
    messages = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            t = row.get("_type")
            if t == "header":
                meta = row.get("meta", {})
            elif t == "member":
                pid = row.get("platformId", "")
                members[pid] = {
                    "id": pid,
                    "name": row.get("accountName", pid),
                    "avatar": row.get("avatar", ""),
                }
            elif t == "message":
                messages.append(row)

    return {"meta": meta, "members": members, "messages": messages}


def build_session_object(raw, declared_start=None, declared_end=None):
    meta = raw["meta"]
    members = raw["members"]
    messages = raw["messages"]

    chat_kind = infer_chat_kind(meta)
    chat_name = meta.get("name", "未知会话")

    valid_msgs = [m for m in messages if not is_system_msg(m)]
    system_count = len(messages) - len(valid_msgs)

    if not valid_msgs:
        raise ValueError("没有有效消息，无法生成会话对象")

    timestamps = [m["timestamp"] for m in valid_msgs]
    ts_start, ts_end = min(timestamps), max(timestamps)
    dt_start = ts_to_dt(ts_start)
    dt_end = ts_to_dt(ts_end)
    days = max(1, (dt_end.date() - dt_start.date()).days + 1)
    total = len(valid_msgs)

    # 用户声明的时间范围（覆盖代码推算的范围）
    if declared_end:
        try:
            d_end = date_type.fromisoformat(declared_end)
        except ValueError:
            d_end = dt_end.date()
    else:
        d_end = dt_end.date()

    if declared_start:
        try:
            d_start = date_type.fromisoformat(declared_start)
        except ValueError:
            d_start = dt_start.date()
    else:
        d_start = dt_start.date()

    declared_days = max(1, (d_end - d_start).days + 1)
    silent_days_at_start = max(0, (dt_start.date() - d_start).days)
    silent_days_at_end = max(0, (d_end - dt_end.date()).days)

    # 活跃度排行
    msg_count_by_sender = Counter(m.get("sender", "unknown") for m in valid_msgs)
    ranking = []
    for rank, (sender_id, count) in enumerate(msg_count_by_sender.most_common(), start=1):
        member = members.get(sender_id, {"id": sender_id, "name": sender_id, "avatar": ""})
        ranking.append({
            "rank": rank,
            "id": sender_id,
            "name": member["name"],
            "avatar": member["avatar"],
            "messageCount": count,
            "percentage": round(count / total * 100, 1),
        })

    # 时段分布
    hourly = [0] * 24
    daily = {}
    for m in valid_msgs:
        dt = ts_to_dt(m["timestamp"])
        hourly[dt.hour] += 1
        day_key = dt.strftime("%Y-%m-%d")
        daily[day_key] = daily.get(day_key, 0) + 1

    peak_hour = hourly.index(max(hourly))

    # 消息类型占比
    type_counter = Counter(classify_msg_type(m) for m in valid_msgs)
    type_ratio = {k: round(v / total, 3) for k, v in type_counter.items()}

    # @ 提及（客观事实）
    mentions = []
    for m in valid_msgs:
        content = m.get("content", "") or ""
        ats = extract_at_mentions(content)
        if ats:
            mentions.append({
                "sender": m.get("accountName", ""),
                "senderId": m.get("sender", ""),
                "mentioned": ats,
                "timestamp": m["timestamp"],
                "datetime": ts_to_dt(m["timestamp"]).isoformat(),
            })

    # ── 每人详细统计 ──
    from collections import defaultdict as _dd
    _ms = _dd(lambda: {
        'lengths': [], 'mediaCount': 0, 'textCount': 0,
        'activeDays': set(), 'firstTs': None, 'lastTs': None
    })
    for m in valid_msgs:
        s = m.get('accountName', '')
        length = len(m.get('content', '') or '')
        day = ts_to_dt(m['timestamp']).strftime('%Y-%m-%d')
        ts = m['timestamp']
        _ms[s]['lengths'].append(length)
        _ms[s]['activeDays'].add(day)
        if classify_msg_type(m) == 'text':
            _ms[s]['textCount'] += 1
        else:
            _ms[s]['mediaCount'] += 1
        if _ms[s]['firstTs'] is None or ts < _ms[s]['firstTs']:
            _ms[s]['firstTs'] = ts
        if _ms[s]['lastTs'] is None or ts > _ms[s]['lastTs']:
            _ms[s]['lastTs'] = ts

    member_stats = {}
    for name, st in _ms.items():
        lengths = st['lengths']
        total_m = len(lengths)
        member_stats[name] = {
            'avgMsgLength': round(sum(lengths) / total_m, 1) if total_m else 0,
            'maxMsgLength': max(lengths) if lengths else 0,
            'mediaRatio': round(st['mediaCount'] / total_m, 3) if total_m else 0,
            'activeDays': sorted(st['activeDays']),
            'firstDatetime': ts_to_dt(st['firstTs']).isoformat() if st['firstTs'] else None,
            'lastDatetime': ts_to_dt(st['lastTs']).isoformat() if st['lastTs'] else None,
        }

    # ── 对话段落划分（30分钟无消息 = 新段落）──
    SESSION_GAP = 30 * 60
    sessions = []
    if valid_msgs:
        current = [valid_msgs[0]]
        for m in valid_msgs[1:]:
            if m['timestamp'] - current[-1]['timestamp'] > SESSION_GAP:
                sessions.append(current)
                current = [m]
            else:
                current.append(m)
        sessions.append(current)

    conversation_sessions = []
    for i, s in enumerate(sessions):
        senders = list(dict.fromkeys(m.get('accountName', '') for m in s))
        conversation_sessions.append({
            'index': i + 1,
            'start': ts_to_dt(s[0]['timestamp']).isoformat(),
            'end': ts_to_dt(s[-1]['timestamp']).isoformat(),
            'messageCount': len(s),
            'participants': senders,
        })

    # ── 最长沉默间隔（Top 10，超过10分钟）──
    silence_gaps = []
    for i in range(1, len(valid_msgs)):
        gap_sec = valid_msgs[i]['timestamp'] - valid_msgs[i-1]['timestamp']
        if gap_sec > 600:
            silence_gaps.append({
                'beforeDatetime': ts_to_dt(valid_msgs[i-1]['timestamp']).isoformat(),
                'afterDatetime': ts_to_dt(valid_msgs[i]['timestamp']).isoformat(),
                'minutes': round(gap_sec / 60),
            })
    silence_gaps.sort(key=lambda x: -x['minutes'])
    silence_gaps = silence_gaps[:10]


    # ══════════════════════════════════════════════════════
    # 一次遍历完成所有新增客观统计
    # ══════════════════════════════════════════════════════
    from collections import defaultdict as _dd2

    # 状态变量
    night_count = _dd2(int)        # 夜猫子：深夜消息数
    night_total = _dd2(int)        # 夜猫子：起征用总消息数（复用 msg_count_by_sender）
    monologue_max = _dd2(int)      # 最爱独白：最长独白条数
    monologue_total = _dd2(int)    # 最爱独白：独白次数（>=3条算一次）
    _mono_cur_sender = None        # 独白当前发言者
    _mono_cur_count = 0            # 独白当前计数
    _mono_last_ts = 0              # 独白上条时间戳
    fastest_reply = None           # 最快回复记录
    _fastest_gap = 9999999
    active_hours = set()           # 群速：有消息的小时
    ice_breakers = _dd2(int)       # 首发：每个段落第一发言者
    session_closer = _dd2(int)     # 话题终结者：段落最后发言者
    last_seen_ts = {}              # 消失榜：最后在线时间戳

    # 预建段落首尾索引（用消息的 platformMessageId 或 index）
    session_first_set = set()
    session_last_set = set()
    for s in sessions:
        if s:
            session_first_set.add(id(s[0]))
            session_last_set.add(id(s[-1]))

    MONOLOGUE_MIN = 3       # 独白阈值
    MONOLOGUE_GAP = 300     # 独白时间窗口（5分钟）
    NIGHT_MIN_MSGS = 10     # 夜猫子起征点
    REPLY_MIN_GAP = 1       # 最快回复排除<1秒（机器人/同步）
    REPLY_MAX_GAP = 300     # 最快回复只看5分钟内的跟进

    for i, m in enumerate(valid_msgs):
        sid = m.get('sender', '')
        name = m.get('accountName', '')
        ts = m['timestamp']
        dt_m = ts_to_dt(ts)

        # 最后在线
        last_seen_ts[sid] = ts

        # 夜猫子（北京时间 23-3点）
        h = dt_m.hour
        if h >= 23 or h < 3:
            night_count[name] += 1

        # 群速：记录活跃小时
        hour_key = dt_m.strftime('%Y-%m-%d-%H')
        active_hours.add(hour_key)

        # 独白统计
        if name == _mono_cur_sender and (ts - _mono_last_ts) < MONOLOGUE_GAP:
            _mono_cur_count += 1
        else:
            # 结算上一段独白
            if _mono_cur_sender and _mono_cur_count >= MONOLOGUE_MIN:
                monologue_total[_mono_cur_sender] += 1
                if _mono_cur_count > monologue_max[_mono_cur_sender]:
                    monologue_max[_mono_cur_sender] = _mono_cur_count
            _mono_cur_sender = name
            _mono_cur_count = 1
        _mono_last_ts = ts

        # 最快回复（宽泛定义：不同人，1秒-5分钟内跟上）
        if i > 0:
            prev = valid_msgs[i - 1]
            gap = ts - prev['timestamp']
            if (REPLY_MIN_GAP <= gap <= REPLY_MAX_GAP and
                    m.get('sender') != prev.get('sender') and
                    classify_msg_type(m) != 'system' and
                    classify_msg_type(prev) != 'system'):
                if gap < _fastest_gap:
                    _fastest_gap = gap
                    fastest_reply = {
                        'replier': name,
                        'replyGapSeconds': gap,
                        'triggerSender': prev.get('accountName', ''),
                        'triggerContent': (prev.get('content', '') or '')[:60],
                        'replyContent': (m.get('content', '') or '')[:60],
                        'datetime': dt_m.isoformat(),
                    }

        # 首发 / 话题终结者
        if id(m) in session_first_set:
            ice_breakers[name] += 1
        if id(m) in session_last_set:
            session_closer[name] += 1

    # 结算最后一段独白
    if _mono_cur_sender and _mono_cur_count >= MONOLOGUE_MIN:
        monologue_total[_mono_cur_sender] += 1
        if _mono_cur_count > monologue_max[_mono_cur_sender]:
            monologue_max[_mono_cur_sender] = _mono_cur_count

    # ── 整理各指标结果 ──

    # 消失榜：在 members 里但这期没发言
    active_sender_ids = set(m.get('sender') for m in valid_msgs)
    ghost_list = []
    for sid, minfo in members.items():
        if sid not in active_sender_ids and '@chatroom' not in sid:
            last_ts = last_seen_ts.get(sid)
            ghost_list.append({
                'name': minfo['name'],
                'id': sid,
                'lastSeenDatetime': ts_to_dt(last_ts).isoformat() if last_ts else None,
                'label': '神秘新人' if not last_ts else '本期潜水',
            })

    # 夜猫子排行（起征点：总消息>=10条）
    night_owl_ranking = []
    for name, cnt in night_count.items():
        total_by_name = msg_count_by_sender.get(
            next((m.get('sender') for m in valid_msgs if m.get('accountName') == name), ''), 0
        )
        if total_by_name >= NIGHT_MIN_MSGS:
            night_owl_ranking.append({
                'name': name,
                'nightMessages': cnt,
                'totalMessages': total_by_name,
                'nightRatio': round(cnt / total_by_name * 100, 1),
            })
    night_owl_ranking.sort(key=lambda x: -x['nightRatio'])

    # 最爱独白排行
    monologue_ranking = []
    for name in set(list(monologue_total.keys()) + list(monologue_max.keys())):
        if monologue_total[name] > 0:
            monologue_ranking.append({
                'name': name,
                'monologueCount': monologue_total[name],
                'longestStreak': monologue_max[name],
            })
    monologue_ranking.sort(key=lambda x: -x['longestStreak'])

    # 群速
    active_hour_count = len(active_hours)
    group_velocity = {
        'totalMessages': total,
        'activeHours': active_hour_count,
        'avgPerActiveHour': round(total / active_hour_count, 1) if active_hour_count else 0,
        'avgPerDay': round(total / max(declared_days, 1), 1),
    }
    # 峰值分钟（消息密度最高的1分钟）
    minute_counter = _dd2(int)
    for m in valid_msgs:
        mk = ts_to_dt(m['timestamp']).strftime('%Y-%m-%d %H:%M')
        minute_counter[mk] += 1
    if minute_counter:
        peak_minute_key = max(minute_counter, key=minute_counter.get)
        group_velocity['peakMinute'] = peak_minute_key
        group_velocity['peakMinuteCount'] = minute_counter[peak_minute_key]

    # 首发排行
    ice_breaker_ranking = sorted(
        [{'name': n, 'count': c} for n, c in ice_breakers.items()],
        key=lambda x: -x['count']
    )

    # 话题终结者排行
    closer_ranking = sorted(
        [{'name': n, 'count': c} for n, c in session_closer.items()],
        key=lambda x: -x['count']
    )

    # 完整原始消息（AI 分析用，不做任何过滤）
    raw_messages = [
        {
            "sender": m.get("accountName", ""),
            "senderId": m.get("sender", ""),
            "timestamp": m["timestamp"],
            "datetime": ts_to_dt(m["timestamp"]).isoformat(),
            "type": classify_msg_type(m),
            "content": m.get("content", "") or "",
            "replyToId": m.get("replyToMessageId"),
        }
        for m in valid_msgs
    ]

    # 私聊专用
    private_extra = {}
    if chat_kind == "private" and len(ranking) >= 2:
        private_extra["talkRatio"] = {
            ranking[0]["name"]: ranking[0]["percentage"],
            ranking[1]["name"]: ranking[1]["percentage"],
        }
        private_extra["dailyAvgMessages"] = round(total / days, 1)

    return {
        "meta": {
            "name": chat_name,
            "type": chat_kind,
            "platform": meta.get("platform", "wechat"),
            "timeRange": {
                "declaredStart": d_start.isoformat() if declared_start else None,
                "declaredEnd": d_end.isoformat(),
                "start": dt_start.isoformat(),
                "end": dt_end.isoformat(),
                "days": declared_days,
                "actualDays": days,
                "silentDaysAtStart": silent_days_at_start,
                "silentDaysAtEnd": silent_days_at_end,
            },
            "totalMessages": total,
            "systemMessages": system_count,
            "activeMembers": len(msg_count_by_sender),
        },
        "members": ranking,
        "activity": {
            "ranking": ranking,
            "hourlyDistribution": hourly,
            "dailyDistribution": daily,
            "peakHour": peak_hour,
            "peakHourLabel": "{:02d}:00-{:02d}:00".format(peak_hour, (peak_hour + 1) % 24),
            "messageTypeRatio": type_ratio,
        },
        "interactions": {
            "mentions": mentions,
        },
        "memberStats": member_stats,
        "conversationSessions": conversation_sessions,
        "silenceGaps": silence_gaps,
        "insights": {
            "ghostList": ghost_list,
            "nightOwlRanking": night_owl_ranking,
            "monologueRanking": monologue_ranking,
            "fastestReply": fastest_reply,
            "groupVelocity": group_velocity,
            "iceBreakerRanking": ice_breaker_ranking,
            "closerRanking": closer_ranking,
        },
        "messages": raw_messages,
        **private_extra,
    }


SKILL_NAME = "chat-parser"


def build_output_filename(session_obj):
    name = session_obj["meta"]["name"]
    name_clean = re.sub(r"[^\w\u4e00-\u9fff]", "_", name)[:20]
    start = session_obj["meta"]["timeRange"]["start"][:10].replace("-", "")
    end = session_obj["meta"]["timeRange"]["end"][:10].replace("-", "")
    return "{}_{}_{}_{}_parsed.json".format(name_clean, start[:4], start[4:6]+start[6:], end[4:6]+end[6:])


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonl', help='WeFlow 导出的 JSONL 文件路径')
    parser.add_argument('--start', default=None, help='用户声明的起始日期，格式 YYYY-MM-DD')
    parser.add_argument('--end', default=None, help='用户声明的结束日期，格式 YYYY-MM-DD（强烈建议填写）')
    args = parser.parse_args()

    input_path = Path(args.jsonl)
    if not input_path.exists():
        print("[ERROR] 文件不存在: {}".format(input_path))
        sys.exit(1)

    declared_start = args.start
    declared_end = args.end

    print("[1/3] 解析文件: {}".format(input_path.name))
    raw = parse_jsonl(input_path)
    print("      成员: {} 人，消息: {} 条".format(len(raw["members"]), len(raw["messages"])))

    print("[2/3] 构建会话数据对象...")
    try:
        session_obj = build_session_object(raw, declared_start=declared_start, declared_end=declared_end)
    except ValueError as e:
        print("[ERROR] {}".format(e))
        sys.exit(1)

    filename = "{}_{}_{}_parsed.json".format(
        re.sub(r"[^\w\u4e00-\u9fff]", "_", session_obj["meta"]["name"])[:20],
        session_obj["meta"]["timeRange"]["start"][:10].replace("-", ""),
        session_obj["meta"]["timeRange"]["end"][:10].replace("-", ""),
    )
    out_dir = input_path.parent / SKILL_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    print("[3/3] 写入: {}".format(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session_obj, f, ensure_ascii=False, indent=2)

    m = session_obj["meta"]
    tr = m["timeRange"]
    print("\n完成")
    print("  会话: {} ({})".format(m["name"], m["type"]))
    print("  时间: {} ~ {} ({} 天)".format(tr["start"][:10], tr["end"][:10], tr["days"]))
    print("  消息: {} 条，活跃成员 {} 人".format(m["totalMessages"], m["activeMembers"]))
    print("  最活跃时段: {}".format(session_obj["activity"]["peakHourLabel"]))
    print("  原始消息: {} 条（供 AI 分析）".format(len(session_obj["messages"])))
    print("  对话段落: {} 个".format(len(session_obj["conversationSessions"])))
    print("  最长沉默: {} 分钟".format(session_obj["silenceGaps"][0]["minutes"] if session_obj["silenceGaps"] else 0))
    ins = session_obj["insights"]
    print("  消失榜: {} 人".format(len(ins["ghostList"])))
    print("  群速: {} 条/活跃小时".format(ins["groupVelocity"]["avgPerActiveHour"]))
    if ins["nightOwlRanking"]:
        top_owl = ins["nightOwlRanking"][0]
        print("  夜猫子: {} (深夜{}%)".format(top_owl["name"], top_owl["nightRatio"]))
    print("  输出: {}".format(out_path))

    print("\n---CHAT_PARSER_RESULT---")
    print(json.dumps(session_obj, ensure_ascii=False))
    print("---CHAT_PARSER_RESULT_END---")

    return str(out_path)


if __name__ == "__main__":
    main()

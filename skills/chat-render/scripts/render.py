#!/usr/bin/env python3
"""
chat-render v4
- 人物志弹性九宫格（最多9人，不留孤行）
- 时间轴改用 conversationSessions，合并沉默
- 气泡区不依赖 box-shadow
- 接入 insights 所有新字段
- 接入 AI 分析新字段：groupConsensus / topicTurningPoints / longestExchange / questionBoard / wordCloud
"""

import argparse
import json
import re
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone, timedelta, date as date_type

SKILL_NAME = "chat-render"
MEMBER_COLORS = ["#c8402a", "#2a5f8f", "#4a7c59", "#8b6a9b", "#c9a84c", "#d4763b", "#3b8fa6", "#a65d7a", "#6b6560"]

PERSONALITY_THEMES = {
    "热闹型": {"accent": "#c8402a", "accent2": "#e8845a", "bg_tint": "#fdf5f0"},
    "专业型": {"accent": "#2a5f8f", "accent2": "#4a85b5", "bg_tint": "#f0f4f8"},
    "温情型": {"accent": "#4a7c59", "accent2": "#6fa882", "bg_tint": "#f0f5f1"},
    "混合型": {"accent": "#7b5ea7", "accent2": "#a085c8", "bg_tint": "#f4f0f8"},
}

TYPE_LABELS = {
    'text': '文字', 'image_or_emoji': '图片', 'voice': '语音',
    'video': '视频', 'quote_reply': '引用', 'app': '链接',
}

def get_theme(p): return PERSONALITY_THEMES.get(p, PERSONALITY_THEMES["混合型"])
def ts_to_dt(ts): return datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=8)))

# ── 弹性九宫格布局计算 ──
def grid_layout(n):
    """返回每行列数列表，保证尾行不孤单"""
    if n <= 3: return [n]
    if n == 4: return [2, 2]
    if n == 5: return [3, 2]
    if n == 6: return [3, 3]
    if n == 7: return [4, 3]
    if n == 8: return [4, 4]
    if n == 9: return [3, 3, 3]
    # 超过9只取前9
    return [3, 3, 3]

# ── 时间轴：conversationSessions 合并版 ──
def build_timeline(sessions, silence_gaps, mc, messages):
    """
    把对话段落 + 段落间沉默合并成时间轴行
    超过15个段落时，合并连续活跃段落
    """
    if not sessions: return ''

    # 构建时间轴条目
    items = []
    for i, s in enumerate(sessions):
        start_dt = s['start'][:16].replace('T', ' ')
        date_str = s['start'][5:10]
        time_str = s['start'][11:16]
        count = s['messageCount']
        ps = s.get('participants', [])

        # 这段最活跃成员颜色
        dot_color = mc.get(ps[0], '#6b6560') if ps else '#6b6560'

        items.append({
            'type': 'session',
            'date': date_str,
            'time': time_str,
            'count': count,
            'participants': ps,
            'color': dot_color,
        })

        # 段落后的沉默
        if i < len(sessions) - 1:
            gap_sec = (datetime.fromisoformat(sessions[i+1]['start']) -
                      datetime.fromisoformat(s['end'])).total_seconds()
            gap_min = round(gap_sec / 60)
            if gap_min >= 60:  # 只显示超过1小时的沉默
                if gap_min >= 1440:
                    gap_label = f"沉默 {round(gap_min/1440)} 天"
                elif gap_min >= 60:
                    gap_label = f"沉默 {round(gap_min/60)} 小时"
                items.append({'type': 'silence', 'label': gap_label, 'minutes': gap_min})

    # 独角戏合并：连续多个只有同一个人的单人段落，合并成「XX 的独角戏」
    merged_solo = []
    solo_buf = []
    solo_name = None
    for item in items:
        if item['type'] == 'session' and len(item['participants']) == 1:
            name = item['participants'][0]
            if name == solo_name:
                solo_buf.append(item)
            else:
                if solo_buf and len(solo_buf) >= 2:
                    total = sum(b['count'] for b in solo_buf)
                    merged_solo.append({'type': 'solo', 'name': solo_name,
                                       'count': total, 'sessions': len(solo_buf),
                                       'color': solo_buf[0]['color']})
                elif solo_buf:
                    merged_solo.extend(solo_buf)
                solo_buf = [item]
                solo_name = name
        else:
            if solo_buf and len(solo_buf) >= 2:
                total = sum(b['count'] for b in solo_buf)
                merged_solo.append({'type': 'solo', 'name': solo_name,
                                   'count': total, 'sessions': len(solo_buf),
                                   'color': solo_buf[0]['color']})
            elif solo_buf:
                merged_solo.extend(solo_buf)
            solo_buf = []
            solo_name = None
            merged_solo.append(item)
    if solo_buf and len(solo_buf) >= 2:
        total = sum(b['count'] for b in solo_buf)
        merged_solo.append({'type': 'solo', 'name': solo_name,
                           'count': total, 'sessions': len(solo_buf),
                           'color': solo_buf[0]['color']})
    elif solo_buf:
        merged_solo.extend(solo_buf)
    items = merged_solo

    # 超过20行则合并：把连续的小段落（<3条）合并
    if len(items) > 20:
        merged = []
        buf = []
        for item in items:
            if item['type'] == 'session' and item['count'] < 3:
                buf.append(item)
            else:
                if buf:
                    total = sum(b['count'] for b in buf)
                    merged.append({'type': 'merged', 'count': total, 'sessions': len(buf)})
                    buf = []
                merged.append(item)
        if buf:
            total = sum(b['count'] for b in buf)
            merged.append({'type': 'merged', 'count': total, 'sessions': len(buf)})
        items = merged

    # 渲染
    html = ''
    for item in items:
        if item['type'] == 'session':
            ps_html = '·'.join(
                '<span style="color:' + mc.get(p,'#6b6560') + '">' + p + '</span>'
                for p in item['participants'][:3]
            )
            bar_w = min(100, max(8, item['count'] * 4))
            html += f'''<div class="tl-row">
  <div class="tl-dot" style="background:{item['color']}"></div>
  <div class="tl-date">{item['date']}<span class="tl-time">{item['time']}</span></div>
  <div class="tl-bar-wrap">
    <div class="tl-bar" style="width:{bar_w}%;background:{item['color']}"></div>
    <span class="tl-count">{item['count']}条</span>
  </div>
  <div class="tl-ps">{ps_html}</div>
</div>'''
        elif item['type'] == 'silence':
            html += f'''<div class="tl-row silence">
  <div class="tl-dot silent"></div>
  <div class="tl-date muted">——</div>
  <div class="tl-silence-label">{item['label']}</div>
</div>'''
        elif item['type'] == 'merged':
            html += f'''<div class="tl-row merged">
  <div class="tl-dot" style="background:#c0bab2"></div>
  <div class="tl-date muted">···</div>
  <div class="tl-silence-label">另 {item['sessions']} 段对话 · 共 {item['count']} 条</div>
</div>'''
    return html


def build_html(parsed, analysis):
    meta = parsed['meta']
    members = parsed['members'][:9]  # 最多9人
    activity = parsed['activity']
    member_stats = parsed.get('memberStats', {})
    sessions = parsed.get('conversationSessions', [])
    silence_gaps = parsed.get('silenceGaps', [])
    messages = parsed.get('messages', [])
    insights = parsed.get('insights', {})

    personality = analysis.get('groupPersonality', '混合型')
    theme = get_theme(personality)
    accent = theme['accent']
    bg_tint = theme['bg_tint']

    mc = analysis.get('memberColors', {})
    for i, m in enumerate(members):
        if m['name'] not in mc:
            mc[m['name']] = MEMBER_COLORS[i % len(MEMBER_COLORS)]

    tr = meta['timeRange']
    declared_end = tr.get('declaredEnd') or tr['end'][:10]
    declared_start = tr.get('declaredStart') or tr['start'][:10]
    days = tr.get('days', 1)
    date_range = f"{declared_start.replace('-', '.')} — {declared_end.replace('-', '.')}"
    file_suffix = f"{declared_start.replace('-','')}_{declared_end.replace('-','')}"

    # ── ① 封面 ──
    cover = f'''<div class="cover">
  <div class="cover-accent" style="background:{accent}"></div>
  <div class="cover-inner">
    <div class="eyebrow">群聊记录 · {date_range}</div>
    <h1 class="cover-title">{analysis.get('narrativeSummary', meta['name'])}</h1>
    <div class="cover-sub">{meta['name']}</div>
    <div class="cover-stats">
      <div class="cstat"><span class="cnum">{meta['totalMessages']}</span><span class="clabel">条消息</span></div>
      <div class="csep"></div>
      <div class="cstat"><span class="cnum">{days}</span><span class="clabel">天</span></div>
      <div class="csep"></div>
      <div class="cstat"><span class="cnum">{meta['activeMembers']}</span><span class="clabel">位活跃成员</span></div>
    </div>
    {"" if not analysis.get('groupConsensus') else f'<div class="consensus"><span class="consensus-label">群友共识</span>{analysis["groupConsensus"]}</div>'}
  </div>
</div>'''

    # ── ② 人物志（弹性九宫格） ──
    member_analysis = analysis.get('memberAnalysis', {})
    rows = grid_layout(len(members))
    cards_html = ''
    idx = 0
    for cols in rows:
        cards_html += f'<div class="medal-row" style="--cols:{cols}">'
        for _ in range(cols):
            if idx >= len(members): break
            m = members[idx]; idx += 1
            color = mc.get(m['name'], '#6b6560')
            ma = member_analysis.get(m['name'], {})
            avatar = m.get('avatar', '')
            quote = ma.get('quote', '')
            cards_html += f'''<div class="medal-card" style="--mcolor:{color}">
  <div class="medal-av-wrap"><img class="medal-av" src="{avatar}" onerror="this.style.background='#d8d2c8'" crossorigin="anonymous"/></div>
  <div class="medal-name">{m['name']}</div>
  <div class="medal-count">{m['messageCount']}条 {m['percentage']}%</div>
  <div class="medal-role">{ma.get('role','')}</div>
  {f'<div class="medal-quote">「{quote}」</div>' if quote else ''}
</div>'''
        cards_html += '</div>'

    # ── ③ 故事线 ──
    story_emojis = ['🎯', '💬', '🔥', '✨', '🎪', '💡', '🌀', '⚡']
    story_colors = [accent, '#2a5f8f', '#4a7c59', '#8b6a9b', '#c9a84c']
    stories_html = ''
    for i, s in enumerate(analysis.get('storyline', [])):
        color = story_colors[i % len(story_colors)]
        emoji = story_emojis[i % len(story_emojis)]
        dt = s.get('datetime', '')
        time_str = dt[5:10].replace('-', '/') if dt else ''
        ps_html = ''.join(
            '<span class="story-p" style="color:' + mc.get(p, '#6b6560') + '">' + p + '</span>'
            for p in s.get('participants', [])
        )
        # 内心独白
        voice_html = ''
        story_voices = analysis.get('storyVoices', [])
        for sv in story_voices:
            if sv.get('storyIndex') == i + 1 and sv.get('voice'):
                speaker = sv.get('speaker', '')
                sp_color = mc.get(speaker, '#6b6560')
                voice_html = (
                    '<div class="story-voice">'
                    '<span class="story-voice-speaker" style="color:' + sp_color + '">' + speaker + ' 心想</span>'
                    '<span class="story-voice-text">「' + sv['voice'] + '」</span>'
                    '</div>'
                )
                break

        stories_html += (
            '<div class="story-item">'
            '<div class="story-num" style="color:' + color + '">' + str(i+1).zfill(2) + '</div>'
            '<div class="story-body">'
            '<div class="story-title-row">'
            '<span class="story-emoji">' + emoji + '</span>'
            '<span class="story-title">' + s.get('title', '') + '</span>'
            '</div>'
            '<div class="story-meta">'
            '<span class="story-time">' + time_str + '</span>'
            '<span class="story-ps">' + ps_html + '</span>'
            '</div>'
            '<div class="story-desc">' + s.get('description', '') + '</div>'
            '<div class="story-quote" style="border-color:' + color + ';background:' + color + '0d">'
            '「' + s.get('keyMessage', '') + '」</div>'
            + voice_html +
            '</div>'
            '</div>'
        )

    # ── ④ 时间轴（对话段落版）──
    timeline_html = build_timeline(list(reversed(sessions)), silence_gaps, mc, messages)

    # ── ⑤ 数据双列 ──
    hourly = activity.get('hourlyDistribution', [0]*24)
    peak_hour = activity.get('peakHour', 0)
    peak_label = activity.get('peakHourLabel', '')

    # 消息类型
    type_bars = ''
    for k, v in activity.get('messageTypeRatio', {}).items():
        if k.startswith('unknown'): continue
        pct = round(v * 100, 1)
        type_bars += f'''<div class="type-row">
  <span class="type-label">{TYPE_LABELS.get(k, k)}</span>
  <div class="type-track"><div class="type-fill" style="width:{pct}%;background:{accent}88"></div></div>
  <span class="type-val">{pct}%</span>
</div>'''

    # ── ⑥ 活跃排行 ──
    max_cnt = members[0]['messageCount'] if members else 1
    ranking_html = ''
    for m in members:
        color = mc.get(m['name'], '#6b6560')
        bw = round(m['messageCount'] / max_cnt * 100)
        avatar = m.get('avatar', '')
        ranking_html += f'''<div class="rank-row">
  <span class="rank-n" style="color:{color}">{str(m['rank']).zfill(2)}</span>
  <img class="rank-av" src="{avatar}" onerror="this.style.background='#d8d2c8'" crossorigin="anonymous"/>
  <span class="rank-name">{m['name']}</span>
  <div class="rank-track"><div class="rank-bar" style="width:{bw}%;background:{color}"></div></div>
  <span class="rank-pct">{m['percentage']}%</span>
</div>'''

    # ── ⑦ 气泡对白（不依赖阴影） ──
    bubbles_html = ''
    quote_members = [m for m in members if member_analysis.get(m['name'], {}).get('quote')][:4]
    for i, m in enumerate(quote_members):
        color = mc.get(m['name'], '#6b6560')
        quote = member_analysis[m['name']]['quote']
        avatar = m.get('avatar', '')
        side = 'left' if i % 2 == 0 else 'right'
        if side == 'left':
            bubbles_html += f'''<div class="chat-row left">
  <img class="chat-av" src="{avatar}" onerror="this.style.background='#d8d2c8'" crossorigin="anonymous"/>
  <div><div class="chat-name" style="color:{color}">{m['name']}</div>
  <div class="chat-bubble lb" style="background:{color}18;border:1.5px solid {color}40">{quote}</div></div>
</div>'''
        else:
            bubbles_html += f'''<div class="chat-row right">
  <div style="text-align:right"><div class="chat-name" style="color:{color}">{m['name']}</div>
  <div class="chat-bubble rb" style="background:{color}18;border:1.5px solid {color}40">{quote}</div></div>
  <img class="chat-av" src="{avatar}" onerror="this.style.background='#d8d2c8'" crossorigin="anonymous"/>
</div>'''

    # ── ⑧ Insights 卡片组 — 深色勋章墙 ──
    ins = insights
    insight_cards = ''

    def ins_card(icon, label, val, sub, note='', light=False, watermark=''):
        cls = 'ins-card light' if light else 'ins-card'
        wm = f'<span class="watermark">{watermark}</span>' if watermark else ''
        n = f'<div class="ins-note">{note}</div>' if note else ''
        return (f'<div class="{cls}">{wm}'
                f'<div class="ins-icon">{icon}</div>'
                f'<div class="ins-label">{label}</div>'
                f'<div class="ins-val">{val}</div>'
                f'<div class="ins-sub">{sub}</div>{n}</div>')

    # 群速（深色）
    gv = ins.get('groupVelocity', {})
    if gv:
        peak_note = f'峰值 {gv["peakMinute"][11:]} · {gv["peakMinuteCount"]}条/分钟' if gv.get('peakMinute') else ''
        insight_cards += ins_card('⚡', 'GROUP SPEED',
            str(gv.get('avgPerActiveHour', 0)),
            '条/活跃小时', peak_note, light=False,
            watermark=str(gv.get('avgPerActiveHour', 0)))

    # 最快回复（深色）
    fr = ins.get('fastestReply')
    if fr:
        insight_cards += ins_card('🏃', 'FASTEST REPLY',
            f'{fr["replyGapSeconds"]}秒',
            f'{fr["replier"]} → {fr["triggerSender"]}',
            f'「{fr["triggerContent"][:15]}」',
            light=False, watermark=str(fr['replyGapSeconds']))

    # 首发冠军（浅色）
    ibr = ins.get('iceBreakerRanking', [])
    if ibr:
        top = ibr[0]
        insight_cards += ins_card('🔔', 'ICE BREAKER',
            top['name'], f'首发 {top["count"]} 次',
            light=True, watermark=str(top['count']))

    # 最爱独白（浅色）
    mr = ins.get('monologueRanking', [])
    if mr:
        top = mr[0]
        insight_cards += ins_card('🎙️', 'MONOLOGUE',
            top['name'], f'连发最长 {top["longestStreak"]} 条',
            light=True, watermark=str(top['longestStreak']))

    # 话题终结者（深色）
    cr = ins.get('closerRanking', [])
    if cr:
        top = cr[0]
        insight_cards += ins_card('🚪', 'CLOSER',
            top['name'], f'终结 {top["count"]} 次对话',
            light=False, watermark=str(top['count']))

    # 夜猫子 or 消失榜（浅色）
    nor = ins.get('nightOwlRanking', [])
    ghosts = ins.get('ghostList', [])
    if nor:
        top = nor[0]
        insight_cards += ins_card('🌙', 'NIGHT OWL',
            top['name'], f'深夜发言占 {top["nightRatio"]}%',
            light=True)
    elif ghosts:
        names = '、'.join(g['name'] for g in ghosts[:3])
        insight_cards += ins_card('👻', 'GHOST',
            names, f'本期潜水 {len(ghosts)} 人',
            light=True)

    # ── ⑨ AI 深度：词云 + 最长对话链 + 问题榜 + 话题转折 ──
    deep_html = ''

    # 词云
    wc = analysis.get('wordCloud', [])
    if wc:
        sizes = [22, 18, 16, 14, 13, 12, 11, 10]
        def wc_color(i):
            if i == 0: return accent
            if i < 3: return 'var(--ink)'
            return 'var(--mid)'
        wc_html = ' '.join(
            '<span class="wc-word" style="font-size:' + str(sizes[min(i, len(sizes)-1)]) + 'px;color:' + wc_color(i) + '">' + w + '</span>'
            for i, w in enumerate(wc[:8])
        )
        deep_html += f'<div class="deep-card"><div class="deep-label">本期关键词</div><div class="wc-wrap">{wc_html}</div></div>'

    # 最长对话链
    le = analysis.get('longestExchange', {})
    if le and le.get('memberA') and le.get('memberB'):
        ca = mc.get(le['memberA'], '#6b6560')
        cb = mc.get(le['memberB'], '#6b6560')
        deep_html += f'''<div class="deep-card">
  <div class="deep-label">本期最默契对话</div>
  <div class="exchange-row">
    <span style="color:{ca};font-weight:700">{le['memberA']}</span>
    <span class="exchange-arrow">⇄</span>
    <span style="color:{cb};font-weight:700">{le['memberB']}</span>
    <span class="exchange-rounds">{le['rounds']} 来回</span>
  </div>
  <div class="deep-sub">{le.get('topic','')}</div>
</div>'''

    # 问题榜
    qb = analysis.get('questionBoard', [])
    if qb:
        q_items = ''.join(
            f'<div class="q-item"><span class="q-mark" style="color:{accent}">Q</span><span class="q-text">{q["question"][:30]}</span><span class="q-badge" style="background:{accent}22;color:{accent}">{q["responseCount"]}条回应</span></div>'
            for q in qb[:3]
        )
        deep_html += f'<div class="deep-card"><div class="deep-label">本期问题榜</div>{q_items}</div>'

    # 话题转折
    ttp = analysis.get('topicTurningPoints', [])
    if ttp:
        tp_items = ''.join(
            f'<div class="tp-item"><span class="tp-time">{t["datetime"][5:10]}</span><span class="tp-desc">{t["description"]}</span></div>'
            for t in ttp[:3]
        )
        deep_html += f'<div class="deep-card"><div class="deep-label">话题转折点</div>{tp_items}</div>'

    # ── ⑩ 彩蛋 ──
    fun_fact = analysis.get('funFact', '')
    unanswered = analysis.get('unanswered', '')
    unanswered_sender = analysis.get('unansweredSender', '')
    easter_html = ''
    if fun_fact:
        easter_html += f'''<div class="easter-card" style="background:{bg_tint}">
  <div class="easter-icon">🔍</div>
  <div class="easter-label">冷知识</div>
  <div class="easter-text">{fun_fact}</div>
</div>'''
    if unanswered:
        easter_html += f'''<div class="easter-card" style="background:{bg_tint}">
  <div class="easter-icon">🌊</div>
  <div class="easter-label">本期沉了</div>
  <div class="easter-text">「{unanswered}」</div>
  <div class="easter-author">— {unanswered_sender}</div>
</div>'''

    mood = analysis.get('mood', '')
    offscreen_voice = analysis.get('offscreenVoice', '')
    offscreen_section = (
        '<div class="offscreen-block">'
        '<div class="offscreen-label">画 外 音</div>'
        '<div class="offscreen-text"><span class="offscreen-dot"></span>' + offscreen_voice + '</div>'
        '</div>'
    ) if offscreen_voice else ''

    hourly_json = json.dumps(hourly)

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>群聊海报</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&family=Space+Mono:wght@400;700&display=swap');
:root{{--ink:#1e1c1a;--paper:#faf7f2;--mid:#7a746e;--light:#e8e2d8;--accent:{accent};--tint:{bg_tint};}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#2a2825;display:flex;flex-direction:column;align-items:center;min-height:100vh;padding:40px 20px;font-family:'Noto Serif SC',serif;gap:20px;}}
.export-btn{{background:var(--accent);color:#faf7f2;border:none;padding:12px 36px;font-family:'Space Mono',monospace;font-size:11px;letter-spacing:2px;cursor:pointer;}}
.export-btn:hover{{opacity:.85;}}.export-btn:disabled{{opacity:.5;cursor:wait;}}
.poster{{width:520px;background:var(--paper);}}

/* 封面 */
.cover{{position:relative;padding:44px 44px 32px;border-bottom:1px solid var(--light);}}
.cover-accent{{position:absolute;left:0;top:0;width:4px;height:100%;}}
.eyebrow{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;color:var(--mid);margin-bottom:16px;}}
.cover-title{{font-size:26px;font-weight:900;color:var(--ink);line-height:1.25;margin-bottom:8px;letter-spacing:-.5px;}}
.cover-sub{{font-family:'Space Mono',monospace;font-size:10px;color:var(--mid);margin-bottom:18px;}}
.cover-stats{{display:flex;align-items:center;gap:12px;margin-bottom:14px;}}
.cstat{{display:flex;flex-direction:column;gap:2px;}}
.cnum{{font-family:'Space Mono',monospace;font-size:22px;font-weight:700;color:var(--ink);line-height:1;}}
.clabel{{font-size:10px;color:var(--mid);}}
.csep{{width:1px;height:32px;background:var(--light);}}
.consensus{{font-size:11px;color:var(--mid);font-style:italic;border-left:3px solid var(--accent);padding:6px 10px;background:var(--tint);}}
.consensus-label{{font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;color:var(--accent);margin-right:6px;}}

/* 通用区块 */
.section{{padding:24px 44px;border-bottom:1px solid var(--light);}}
.section-label{{font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:2px;color:var(--accent);text-transform:uppercase;margin-bottom:18px;padding-bottom:8px;border-bottom:1px solid var(--light);}}

/* 人物志九宫格 */
.medal-row{{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:10px;margin-bottom:10px;}}
.medal-row:last-child{{margin-bottom:0;}}
.medal-card{{border-left:3px solid var(--mcolor);padding:12px 10px;background:var(--mcolor)08;display:flex;flex-direction:column;gap:4px;}}
.medal-av-wrap{{width:40px;height:40px;border-radius:50%;overflow:hidden;border:2px solid var(--mcolor);margin-bottom:4px;}}
.medal-av{{width:100%;height:100%;object-fit:cover;}}
.medal-name{{font-size:12px;font-weight:900;color:var(--mcolor);}}
.medal-count{{font-family:'Space Mono',monospace;font-size:8px;color:var(--mid);}}
.medal-role{{font-size:11px;color:var(--ink);line-height:1.5;}}
.medal-quote{{font-size:9px;color:var(--mid);font-style:italic;border-left:2px solid var(--mcolor);padding-left:6px;line-height:1.5;margin-top:2px;}}

/* 故事线 */
.storyline{{display:flex;flex-direction:column;gap:28px;}}
.story-item{{display:flex;gap:14px;padding-bottom:28px;border-bottom:1px solid var(--light);}}
.story-item:last-child{{border-bottom:none;padding-bottom:0;}}
.story-num{{font-family:'Space Mono',monospace;font-size:34px;font-weight:700;line-height:1;flex-shrink:0;opacity:.15;margin-top:2px;}}
.story-body{{flex:1;}}
.story-title-row{{display:flex;align-items:baseline;gap:6px;margin-bottom:5px;}}
.story-emoji{{font-size:16px;line-height:1;}}
.story-title{{font-size:18px;font-weight:900;color:var(--ink);line-height:1.3;}}
.story-meta{{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;}}
.story-time{{font-family:'Space Mono',monospace;font-size:9px;color:var(--mid);}}
.story-ps{{display:flex;gap:8px;flex-wrap:wrap;}}
.story-p{{font-size:11px;font-weight:700;}}
.story-desc{{font-size:13px;color:var(--ink);line-height:1.85;margin-bottom:10px;}}
.story-quote{{font-size:11px;color:var(--mid);font-style:italic;border-left:3px solid;padding:7px 12px;line-height:1.65;}}

/* 时间轴 — 连续轴线版 */
.timeline{{display:flex;flex-direction:column;position:relative;padding-left:16px;}}
.timeline::before{{content:'';position:absolute;left:3px;top:6px;bottom:6px;width:1px;background:var(--light);}}
.tl-row{{display:flex;align-items:center;gap:10px;margin-bottom:10px;position:relative;}}
.tl-row:last-child{{margin-bottom:0;}}
.tl-dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0;position:absolute;left:-19px;top:50%;transform:translateY(-50%);border:1.5px solid var(--paper);}}
.tl-dot.silent{{background:var(--light);}}
.tl-date{{font-family:'Space Mono',monospace;font-size:10px;color:var(--ink);width:44px;flex-shrink:0;line-height:1.3;}}
.tl-date.muted{{color:var(--mid);}}
.tl-time{{font-size:8px;color:var(--mid);display:block;}}
.tl-bar-wrap{{display:flex;align-items:center;gap:5px;width:80px;flex-shrink:0;}}
.tl-bar{{height:5px;border-radius:2px;}}
.tl-count{{font-family:'Space Mono',monospace;font-size:9px;color:var(--mid);}}
.tl-ps{{flex:1;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.tl-silence-label{{flex:1;font-family:'Space Mono',monospace;font-size:9px;color:var(--mid);font-style:italic;opacity:.7;}}
.tl-row.silence{{margin-bottom:4px;}}
.tl-row.merged{{opacity:.5;}}

/* 数据双列 */
.data-cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px;}}
.data-sub{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;color:var(--mid);margin-bottom:10px;}}
.mini-hm{{display:grid;grid-template-columns:repeat(24,1fr);gap:1px;margin-bottom:5px;}}
.mh-col{{display:flex;flex-direction:column;align-items:center;gap:2px;}}
.mh-bar{{width:100%;border-radius:1px;background:var(--ink);}}
.mh-lbl{{font-family:'Space Mono',monospace;font-size:6px;color:var(--mid);}}
.peak-note{{font-size:10px;color:var(--mid);}}
.type-row{{display:flex;align-items:center;gap:8px;margin-bottom:5px;}}
.type-label{{font-size:9px;color:var(--mid);width:36px;flex-shrink:0;}}
.type-track{{flex:1;height:4px;background:var(--light);border-radius:2px;}}
.type-fill{{height:100%;border-radius:2px;}}
.type-val{{font-family:'Space Mono',monospace;font-size:9px;color:var(--mid);width:32px;text-align:right;}}

/* 活跃排行 */
.rank-row{{display:flex;align-items:center;gap:8px;margin-bottom:8px;}}
.rank-row:last-child{{margin-bottom:0;}}
.rank-n{{font-family:'Space Mono',monospace;font-size:11px;font-weight:700;width:20px;flex-shrink:0;}}
.rank-av{{width:26px;height:26px;border-radius:50%;object-fit:cover;flex-shrink:0;background:var(--light);}}
.rank-name{{font-size:12px;font-weight:700;color:var(--ink);width:72px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.rank-track{{flex:1;height:4px;background:var(--light);border-radius:2px;}}
.rank-bar{{height:100%;border-radius:2px;}}
.rank-pct{{font-family:'Space Mono',monospace;font-size:10px;color:var(--mid);width:36px;text-align:right;}}

/* 气泡对白 */
.bubbles-wrap{{background:var(--tint);padding:20px 44px;display:flex;flex-direction:column;gap:14px;}}
.chat-row{{display:flex;align-items:flex-start;gap:10px;}}
.chat-row.right{{flex-direction:row-reverse;}}
.chat-av{{width:30px;height:30px;border-radius:50%;object-fit:cover;flex-shrink:0;background:var(--light);}}
.chat-name{{font-family:'Space Mono',monospace;font-size:9px;margin-bottom:4px;}}
.chat-row.right .chat-name{{text-align:right;}}
.chat-bubble{{display:inline-block;padding:9px 13px;font-size:12px;color:var(--ink);line-height:1.65;max-width:270px;}}
.lb{{border-radius:2px 12px 12px 12px;}}
.rb{{border-radius:12px 2px 12px 12px;}}

/* 本期之最 — 勋章荣誉墙 */
.ins-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;border:1.5px solid var(--ink);}}
.ins-card{{padding:16px 14px;display:flex;flex-direction:column;gap:4px;border-right:1px solid rgba(255,255,255,.15);border-bottom:1px solid rgba(255,255,255,.15);background:#2a2825;color:#faf7f2;position:relative;overflow:hidden;}}
.ins-card:nth-child(3n){{border-right:none;}}
.ins-card.light{{background:#faf7f2;color:var(--ink);border-right:1px solid var(--light);border-bottom:1px solid var(--light);}}
.ins-card .watermark{{position:absolute;right:-8px;bottom:-12px;font-family:'Space Mono',monospace;font-size:56px;font-weight:700;opacity:.05;line-height:1;color:inherit;pointer-events:none;}}
.ins-icon{{font-size:14px;margin-bottom:2px;}}
.ins-label{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:1px;color:rgba(255,255,255,.5);text-transform:uppercase;}}
.ins-card.light .ins-label{{color:var(--mid);}}
.ins-val{{font-size:22px;font-weight:900;line-height:1.1;color:#faf7f2;}}
.ins-card.light .ins-val{{color:var(--ink);}}
.ins-sub{{font-size:11px;color:rgba(255,255,255,.6);}}
.ins-card.light .ins-sub{{color:var(--mid);}}
.ins-note{{font-size:9px;color:rgba(255,255,255,.4);font-style:italic;margin-top:2px;}}
.ins-card.light .ins-note{{color:var(--mid);}}

/* 深度分析 */
.deep-card{{background:var(--tint);padding:14px;margin-bottom:10px;}}
.deep-card:last-child{{margin-bottom:0;}}
.deep-label{{font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;color:var(--mid);margin-bottom:8px;}}
.deep-sub{{font-size:10px;color:var(--mid);margin-top:4px;}}
.wc-wrap{{display:flex;flex-wrap:wrap;gap:6px;align-items:baseline;}}
.wc-word{{font-weight:700;}}
.exchange-row{{display:flex;align-items:center;gap:8px;font-size:14px;}}
.exchange-arrow{{color:var(--mid);font-size:16px;}}
.exchange-rounds{{font-family:'Space Mono',monospace;font-size:10px;color:var(--mid);}}
.q-item{{display:flex;align-items:center;gap:8px;margin-bottom:6px;}}
.q-item:last-child{{margin-bottom:0;}}
.q-mark{{font-family:'Space Mono',monospace;font-size:12px;font-weight:700;flex-shrink:0;}}
.q-text{{font-size:11px;color:var(--ink);flex:1;}}
.q-badge{{font-family:'Space Mono',monospace;font-size:8px;padding:2px 6px;border-radius:2px;flex-shrink:0;}}
.tp-item{{display:flex;gap:10px;margin-bottom:6px;}}
.tp-item:last-child{{margin-bottom:0;}}
.tp-time{{font-family:'Space Mono',monospace;font-size:9px;color:var(--accent);flex-shrink:0;}}
.tp-desc{{font-size:11px;color:var(--ink);line-height:1.5;}}

/* 内心独白 */
.story-voice{{margin-top:10px;padding:8px 12px;background:rgba(0,0,0,.03);border-left:2px dashed var(--light);}}
.story-voice-speaker{{font-family:'Space Mono',monospace;font-size:9px;font-weight:700;margin-right:6px;}}
.story-voice-text{{font-size:11px;color:var(--mid);font-style:italic;line-height:1.6;}}

/* 画外音 */
.offscreen-block{{padding:28px 44px;border-bottom:1px solid var(--light);}}
.offscreen-label{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;color:var(--mid);margin-bottom:12px;}}
.offscreen-text{{font-size:15px;color:var(--ink);line-height:1.8;font-style:italic;}}
.offscreen-dot{{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--accent);margin-right:8px;vertical-align:middle;}}

/* 彩蛋 */
.easter-row{{display:grid;grid-template-columns:1fr 1fr;gap:10px;}}
.easter-card{{padding:12px;}}
.easter-icon{{font-size:18px;margin-bottom:5px;}}
.easter-label{{font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;color:var(--mid);margin-bottom:4px;}}
.easter-text{{font-size:11px;color:var(--ink);line-height:1.6;}}
.easter-author{{font-family:'Space Mono',monospace;font-size:9px;color:var(--mid);margin-top:3px;}}

/* 情绪收尾 */
.mood-close{{padding:32px 44px;text-align:center;background:#2a2825;}}
.mood-text{{font-size:15px;color:#faf7f2;line-height:1.9;font-style:italic;}}
.mood-line{{width:36px;height:2px;background:var(--accent);margin:14px auto 0;}}

/* 底部 */
.footer{{padding:14px 44px;display:flex;justify-content:space-between;border-top:1px solid var(--light);}}
.footer-brand{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;color:var(--mid);}}
.footer-info{{font-family:'Space Mono',monospace;font-size:9px;color:var(--mid);}}
</style>
</head>
<body>
<button class="export-btn" onclick="exportPoster()">↓ 导出图片</button>
<div class="poster" id="poster">

{cover}

<div class="section">
  <div class="section-label">人物志</div>
  {cards_html}
</div>

<div class="section">
  <div class="section-label">本期故事</div>
  <div class="storyline">{stories_html}</div>
</div>

<div class="section">
  <div class="section-label">对话节奏</div>
  <div class="timeline">{timeline_html}</div>
</div>

<div class="section">
  <div class="section-label">数据</div>
  <div class="data-cols">
    <div>
      <div class="data-sub">活跃时段</div>
      <div class="mini-hm" id="mini-hm"></div>
      <div class="peak-note">峰值 <strong style="color:var(--accent)">{peak_label}</strong></div>
    </div>
    <div>
      <div class="data-sub">内容构成</div>
      {type_bars}
    </div>
  </div>
</div>

<div class="section">
  <div class="section-label">活跃排行</div>
  {ranking_html}
</div>

<div class="section" style="padding:24px 0;">
  <div style="padding:0 44px 16px"><div class="section-label">本期对白</div></div>
  <div class="bubbles-wrap">{bubbles_html}</div>
</div>

{"" if not insight_cards else f'<div class="section"><div class="section-label">本期之最</div><div class="ins-grid">{insight_cards}</div></div>'}

{"" if not deep_html else f'<div class="section"><div class="section-label">深度</div>{deep_html}</div>'}

{offscreen_section}

{"" if not easter_html else f'<div class="section"><div class="section-label">本期彩蛋</div><div class="easter-row">{easter_html}</div></div>'}

<div class="mood-close">
  <div class="mood-text">{mood}</div>
  <div class="mood-line"></div>
</div>

<div class="footer">
  <div class="footer-brand">CHAT · REPORT</div>
  <div class="footer-info">{date_range} · {meta['activeMembers']} 位成员</div>
</div>

</div>
<script>
const hourly={hourly_json};
const peakHour={peak_hour};
const accent='{accent}';
const maxH=Math.max(...hourly);
const mh=document.getElementById('mini-hm');
hourly.forEach((v,i)=>{{
  const col=document.createElement('div');col.className='mh-col';
  const bar=document.createElement('div');bar.className='mh-bar';
  bar.style.height=Math.max(2,Math.round((v/maxH)*36))+'px';
  bar.style.opacity=v===0?'0.07':String(0.2+(v/maxH)*0.75);
  if(i===peakHour){{bar.style.background=accent;bar.style.opacity='1';}}
  const lbl=document.createElement('div');lbl.className='mh-lbl';
  lbl.textContent=i%6===0?String(i).padStart(2,'0'):'';
  col.appendChild(bar);col.appendChild(lbl);mh.appendChild(col);
}});
async function exportPoster(){{
  const btn=document.querySelector('.export-btn');
  btn.disabled=true;btn.textContent='生成中...';
  try{{
    const c=await html2canvas(document.getElementById('poster'),{{scale:2,useCORS:true,backgroundColor:'#faf7f2',logging:false}});
    const a=document.createElement('a');
    a.download='群聊海报_{file_suffix}.png';
    a.href=c.toDataURL('image/png');a.click();
  }}catch(e){{alert('导出失败，请截图保存');}}
  btn.disabled=false;btn.textContent='↓ 导出图片';
}}
</script>
</body>
</html>'''

    return html, re.sub(r'[^\w\u4e00-\u9fff]','_', meta['name'])[:20], file_suffix


def render(parsed_path, analysis_path, output_dir):
    parsed = json.load(open(parsed_path, encoding='utf-8'))
    analysis = json.load(open(analysis_path, encoding='utf-8'))
    print('[2/2] 渲染海报...')
    html, name_clean, file_suffix = build_html(parsed, analysis)
    out_dir = Path(output_dir) / SKILL_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name_clean}_{file_suffix}_poster.html"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('\n---CHAT_RENDER_RESULT---')
    print(str(out_path))
    print('---CHAT_RENDER_RESULT_END---')
    return str(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parsed', required=True)
    parser.add_argument('--analysis', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(f'[1/2] 读取: {args.parsed}')
    out = render(args.parsed, args.analysis, args.output)
    print(f'完成: {out}')

if __name__ == '__main__':
    main()

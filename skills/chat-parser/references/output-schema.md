# 标准会话数据对象 Schema

chat-parser 的完整输出结构，供 chat-render 和其他下游 skill 参考。

## 顶层结构

```json
{
  "meta": { ... },
  "members": [ ... ],
  "activity": { ... },
  "interactions": { ... },
  "memberStats": { ... },
  "conversationSessions": [ ... ],
  "silenceGaps": [ ... ],
  "messages": [ ... ]
}
```

---

## meta

基础元数据。

```json
{
  "name": "群聊名称或 chatroom ID",
  "type": "group | private",
  "platform": "wechat",
  "timeRange": {
    "start": "2026-03-18T19:25:40+08:00",
    "end": "2026-03-21T18:28:16+08:00",
    "days": 4
  },
  "totalMessages": 57,
  "systemMessages": 1,
  "activeMembers": 3
}
```

---

## members

活跃度排行，按发言数降序。

```json
[
  {
    "rank": 1,
    "id": "wxid_xxx",
    "name": "昵称",
    "avatar": "https://...",
    "messageCount": 27,
    "percentage": 47.4
  }
]
```

---

## activity

客观时间分布统计。

```json
{
  "ranking": [ ... ],
  "hourlyDistribution": [0, 0, 0, ..., 18, 0, 0],
  "dailyDistribution": {
    "2026-03-18": 26,
    "2026-03-20": 16,
    "2026-03-21": 15
  },
  "peakHour": 21,
  "peakHourLabel": "21:00-22:00",
  "messageTypeRatio": {
    "text": 0.895,
    "image_or_emoji": 0.07,
    "video": 0.018,
    "unknown_4": 0.018
  }
}
```

---

## interactions

客观互动事实。

```json
{
  "mentions": [
    {
      "sender": "展宣—魏",
      "senderId": "wxid_xxx",
      "mentioned": ["2agathon"],
      "timestamp": 1773833140,
      "datetime": "2026-03-18T19:25:40+08:00"
    }
  ]
}
```

---

## memberStats

每位成员的客观行为特征，AI 可直接用于群角色判断，无需心算。

```json
{
  "2agathon": {
    "avgMsgLength": 37.1,
    "maxMsgLength": 161,
    "mediaRatio": 0.222,
    "activeDays": ["2026-03-18", "2026-03-20", "2026-03-21"],
    "firstDatetime": "2026-03-18T19:36:28+08:00",
    "lastDatetime": "2026-03-21T18:28:16+08:00"
  },
  "展宣—魏": {
    "avgMsgLength": 10.2,
    "maxMsgLength": 25,
    "mediaRatio": 0.0,
    "activeDays": ["2026-03-18", "2026-03-20", "2026-03-21"],
    "firstDatetime": "2026-03-18T19:25:40+08:00",
    "lastDatetime": "2026-03-21T18:15:56+08:00"
  }
}
```

字段说明：
- `avgMsgLength`：平均消息字符数，反映表达深度
- `maxMsgLength`：最长单条消息字符数
- `mediaRatio`：媒体消息（图片/视频/表情包）占该成员总消息的比例
- `activeDays`：有发言记录的日期列表
- `firstDatetime` / `lastDatetime`：该成员首条和末条消息时间

---

## conversationSessions

按自然对话段落划分（30分钟无消息为段落边界）。

```json
[
  {
    "index": 1,
    "start": "2026-03-18T19:25:40+08:00",
    "end": "2026-03-18T19:45:21+08:00",
    "messageCount": 8,
    "participants": ["展宣—魏", "2agathon"]
  },
  {
    "index": 2,
    "start": "2026-03-18T21:05:34+08:00",
    "end": "2026-03-18T21:52:51+08:00",
    "messageCount": 18,
    "participants": ["旭辉—刘", "展宣—魏", "2agathon"]
  }
]
```

AI 可用于：识别话题切换点、判断哪次对话最热烈、理解群的活跃节奏。

---

## silenceGaps

沉默间隔排行（Top 10，超过10分钟），降序排列。

```json
[
  {
    "beforeDatetime": "2026-03-18T21:52:51+08:00",
    "afterDatetime": "2026-03-20T07:02:50+08:00",
    "minutes": 1990
  },
  {
    "beforeDatetime": "2026-03-21T14:10:19+08:00",
    "afterDatetime": "2026-03-21T18:15:39+08:00",
    "minutes": 245
  }
]
```

AI 可用于：识别话题自然结束点、理解群的作息规律。

---

## messages

完整原始消息，AI 分析用，不做任何过滤或提炼。

```json
[
  {
    "sender": "2agathon",
    "senderId": "wxid_xxx",
    "timestamp": 1773961398,
    "datetime": "2026-03-20T07:03:18+08:00",
    "type": "text",
    "content": "泪目兄弟们，报销chatgpt会员费了",
    "replyToId": null
  }
]
```

type 枚举值：

| type | 含义 |
|------|------|
| text | 文本 |
| image_or_emoji | 图片 / 表情包 |
| quote_reply | 引用回复 |
| voice | 语音 |
| video | 视频 |
| emoji | 表情包 |
| app | 应用消息（链接/文件/小程序/红包/转账） |
| system | 系统消息 |
| recall | 撤回消息 |
| unknown_N | 未识别类型，N 为原始 type 值 |

---

## 设计原则

**代码只做客观统计，主观判断留给 AI。**

- `memberStats`、`conversationSessions`、`silenceGaps` 是客观事实，代码算
- 群性格判断、话题提炼、金句选取、群画像撰写——全部由 AI 在 chat-render 阶段完成
---

## insights

一次遍历计算的客观行为统计，供 AI 分析和 render 直接使用。

```json
{
  "ghostList": [
    {
      "name": "昵称",
      "id": "wxid_xxx",
      "lastSeenDatetime": "2026-03-10T21:00:00+08:00",
      "label": "本期潜水 | 神秘新人"
    }
  ],
  "nightOwlRanking": [
    {
      "name": "昵称",
      "nightMessages": 12,
      "totalMessages": 45,
      "nightRatio": 26.7
    }
  ],
  "monologueRanking": [
    {
      "name": "昵称",
      "monologueCount": 2,
      "longestStreak": 6
    }
  ],
  "fastestReply": {
    "replier": "昵称",
    "replyGapSeconds": 4,
    "triggerSender": "对方昵称",
    "triggerContent": "触发消息前60字",
    "replyContent": "回复内容前60字",
    "datetime": "2026-03-18T21:52:51+08:00"
  },
  "groupVelocity": {
    "totalMessages": 57,
    "activeHours": 10,
    "avgPerActiveHour": 5.7,
    "avgPerDay": 14.2,
    "peakMinute": "2026-03-18 21:20",
    "peakMinuteCount": 4
  },
  "iceBreakerRanking": [
    { "name": "昵称", "count": 5 }
  ],
  "closerRanking": [
    { "name": "昵称", "count": 6 }
  ]
}
```

字段说明：

| 字段 | 含义 | 边界处理 |
|------|------|---------|
| `ghostList` | 在群但本期零发言的成员 | 过滤 @chatroom 系统账号 |
| `nightOwlRanking` | 深夜(23-3点)发言占比排行 | 起征点：总消息≥10条 |
| `monologueRanking` | 连发≥3条不等回复的独白统计 | 时间窗口：5分钟内算连续 |
| `fastestReply` | 不同人之间最快跟进记录 | 排除<1秒（机器人）和>5分钟 |
| `groupVelocity` | 群活跃速度，含峰值分钟 | 按「有消息的小时」计算，不含沉默期 |
| `iceBreakerRanking` | 每个对话段落第一发言者统计 | 基于 conversationSessions |
| `closerRanking` | 每个对话段落最后发言者统计 | 「话题终结者」反向指标 |

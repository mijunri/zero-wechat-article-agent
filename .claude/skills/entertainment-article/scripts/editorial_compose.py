#!/usr/bin/env python3
"""Editorial layer — angle, opinion, reader voice (not encyclopedia stitching)."""
from __future__ import annotations

import re
from typing import Any

from de_ai_polish import polish
from fact_rank import event_keywords, rank_facts


def pick_angle(hot_title: str, person: str, kind: str) -> str:
    kws = event_keywords(hot_title, person)
    hook = "、".join(kws[:3]) if kws else hot_title[:10]
    if "贫穷" in hot_title or "誓词" in hot_title:
        return "婚礼誓词里的阶级语境"
    if kind == "wedding":
        return f"{person}婚礼细节"
    if kind == "gossip":
        return hook
    return hook


def hook_opening(person: str, hot_title: str, hot_value: int | None, angle: str) -> str:
    heat = ""
    if hot_value and hot_value > 20_000:
        heat = f"热度已经冲到 {hot_value // 10000} 万+，"
    if "贫穷" in hot_title or "誓词" in hot_title:
        return polish(
            f"{person}婚礼誓词里那句「没有贫穷」，{heat}把微博热搜顶上了。"
            f"不是祝福写得多浪漫，是这句话的语境太「硬」——你一眼就能读出阶层差异。"
        )
    return polish(
        f"{person}因为「{hot_title}」上了热搜。{heat}"
        f"我先把能核实的细节捋一遍，再说说我怎么看。"
    )


def write_opinion(
    person: str,
    hot_title: str,
    kind: str,
    event_facts: list[str],
    quotes: list[str],
) -> str:
    """圈内人立场：理解为主，但有明确判断，禁止空话。"""
    if "贫穷" in hot_title or "誓词" in hot_title:
        return polish(
            f"说句实在的，{person}在誓词里写「没有贫穷」，字面是承诺「不让另一半受穷」，"
            f"但放在赌王之子身上，路人读到的往往是另一层意思：这家子从来不知道「穷」是什么滋味。"
            f"你如果是粉丝，可能觉得这是霸总式浪漫；如果是路人，更容易觉得被「凡尔赛」糊脸。"
            f"我不觉得他在故意冒犯谁，但公开誓词本来就要照顾围观者的情绪——"
            f"这句话信息量是有了，情商账上未必划算。"
        )
    if kind == "wedding":
        return polish(
            f"婚礼热搜的套路你我都熟：细节一漏，全网审判。"
            f"{person}这事，我觉得核心不是「结没结」，而是公众想看的到底是幸福，还是落差。"
            f"你要是真关心他，不如等当事人完整回应；要是吃瓜，就把争议点看清楚再站队。"
        )
    if quotes:
        q = quotes[0][:60]
        return polish(
            f"我倾向把这事看成「一句话被拎出来放大」。"
            f"报道里提到「{q}…」，但热搜标题往往只留最刺激的那半句。"
            f"你要是想发表看法，至少把原话上下文找齐——不然很容易骂错人。"
        )
    if event_facts:
        hint = event_facts[0][:80]
        return polish(
            f"看完一圈公开信息，我的判断是：这事还有继续发酵的空间。"
            f"目前能确认的是「{hint}…」这类细节，但情绪已经跑在事实前面了。"
            f"你若是路人，先别急着下结论；若是老粉，也别把热搜当全貌。"
        )
    return polish(
        f"目前能写的只有热搜词条本身，细节还在路上。"
        f"我的态度是：先让子弹飞一会儿，等{person}方或主流媒体把来龙去脉说全，再聊值不值得上纲上线。"
    )


def closing_line(person: str, hot_title: str, kind: str) -> str:
    if "贫穷" in hot_title:
        return polish(
            f"{person}一贯不太按「标准答案」出牌——这次誓词也是。"
            f"热搜会散，但公众对「怎么说才得体」的标准，只会越来越严。"
        )
    return polish(
        f"热闹总会过去，{person}接下来怎么接招，比今天谁骂谁更重要。"
        f"你要是有不同看法，评论区见——别只留表情包。"
    )


def h2_event(angle: str, person: str) -> str:
    if "誓词" in angle or "婚礼" in angle:
        return f"{person}誓词到底说了啥"
    return f"先把{person}这事说清楚"


def h2_opinion() -> str:
    return "说句实在的"


def h2_reader() -> str:
    return "你咋看"

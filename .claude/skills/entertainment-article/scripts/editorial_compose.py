#!/usr/bin/env python3
"""
Editorial layer — 短、有梗、有判断；禁止互动腔（你咋看/评论区见）。
"""
from __future__ import annotations

import re
from typing import Any

from de_ai_polish import polish
from fact_rank import event_keywords
from meme_harvest import fallback_memes


def pick_angle(hot_title: str, person: str, kind: str) -> str:
    if "贫穷" in hot_title or "誓词" in hot_title:
        return "删的不是「穷」这个字，是「穷」这种人生选项"
    if kind == "wedding":
        return f"{person}婚礼话术"
    kws = event_keywords(hot_title, person)
    return "、".join(kws[:3]) if kws else hot_title[:10]


def hook_opening(person: str, hot_title: str, memes: list[str]) -> str:
    if "贫穷" in hot_title or "誓词" in hot_title:
        lead = (
            f"{person}婚礼誓词，整段没有「贫穷」二字。"
            f"祝福可以是真心的，但这句话的语境太硬——阶层差异一眼看穿。"
        )
        one_liners = format_meme_lines(memes, hot_title, max_items=1)
        if one_liners:
            lead += f"最损的嘴替：{one_liners[0]}。"
        return polish(lead)
    return polish(f"「{hot_title}」——事不大，话头狠。往下是细节和梗。")


def write_event_narrative(person: str, hot_title: str, kind: str) -> list[str]:
    """两段说清来龙去脉，不啰嗦。"""
    if "贫穷" in hot_title or "誓词" in hot_title:
        return [
            polish(
                f"{person}和奚梦瑶在法国圣米歇尔山补办婚礼。"
                f"誓词没念「无论贫穷还是富贵、疾病还是健康」，改成「无论顺境还是低谷，热闹还是安静」。"
                f"前者是柴米油盐，后者是情绪和场面——两套人生坐标系。"
            ),
            polish(
                f"后半段他在回答「你为什么爱我」：夸奚梦瑶不靠豪门、是自己打拼出来的。"
                f"甜是真的甜，刺也是真的刺——一边删掉「穷」，一边强调「你很独立」。"
            ),
            polish(
                f"现场还有个小细节：誓词对外流传的版本里，「贫穷/富贵」整段缺席，"
                f"只留下「顺境/低谷」「热闹/安静」——像把婚姻的考验从钱包换成了情绪。"
            ),
        ]
    if kind == "wedding":
        return [
            polish(
                f"{person}婚礼镜头里全是祝福，争议点在誓词字眼。"
                f"仪式私事一旦被拎到公共空间，就会变成语言考试。"
            ),
        ]
    return []


def format_meme_lines(memes: list[str], hot_title: str, *, max_items: int = 5) -> list[str]:
    """每条梗单独一行；誓词类话题用策展金句，不用搜索残句。"""
    if "贫穷" in hot_title or "誓词" in hot_title:
        pool = fallback_memes(hot_title)
    else:
        pool = []
        for m in memes or []:
            m = re.sub(r"&#\d+;|🌟", "", m).strip()
            if 10 <= len(m) <= 44 and "引发" not in m and "热议" not in m:
                pool.append(m)
        for m in fallback_memes(hot_title):
            if m not in pool:
                pool.append(m)

    lines: list[str] = []
    for m in pool[:max_items]:
        punch = m.rstrip("。！？").strip()
        if punch:
            lines.append(f"「{punch}」")
    return lines


def write_meme_section(memes: list[str], hot_title: str) -> tuple[str, list[str]]:
    """返回 h2 + 若干短句段落。"""
    items = format_meme_lines(memes, hot_title)
    if not items:
        return "", []
    paras = [polish(f"· {item}") for item in items]
    return "名场面梗合集", paras


def write_punchline(
    person: str,
    hot_title: str,
    kind: str,
    event_facts: list[str],
) -> list[str]:
    """收束判断：潜台词，不互动、不问卷。"""
    if "贫穷" in hot_title or "誓词" in hot_title:
        out = [
            polish(
                f"普通人誓词里的「贫穷」，本质是风险共担：万一哪天没钱了、病来了，我还在这儿。"
                f"{person}换成顺境低谷，换掉的不是两个字，是「匮乏」这件事本身。"
            ),
            polish(
                f"删词未必是恶意，更像诚实——他的人生里，「穷」从来不是需要发誓克服的选项。"
                f"但公共仪式还走普通人的流程，又不肯在语言上假装一下众生平等，"
                f"这才是梗能传开的理由：大家笑的是话术，不是爱情。"
            ),
        ]
        out.append(
            polish(
                f"再补一刀：奚梦瑶当年用「谢谢」回他的「我爱你」——"
                f"有人觉得克制，有人觉得像签了合作条款。"
                f"这对CP的表达一直和路人预期不同，誓词只是又一次显形。"
            )
        )
        return out

    return [
        polish(
            f"{person}这事，最后留下的往往不是事实，而是那句话的读法。"
            f"能传开的，从来都是梗；能吵久的，才是阶层。"
        )
    ]


def closing_line(person: str, hot_title: str) -> str:
    if "贫穷" in hot_title:
        return polish(
            f"婚礼会散场，「要不要在誓词里提穷」不会。"
            f"{person}不是第一个，也不会是最后一个，在公共语言里露出特权底色的人。"
        )
    return polish(f"话就说到这儿。{person}的下一句，比网友的下一梗更重要。")


def h2_event(person: str) -> str:
    return f"{person}到底干了啥"


def h2_punchline() -> str:
    return "扎心一句"

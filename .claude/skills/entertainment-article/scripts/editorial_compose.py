#!/usr/bin/env python3
"""
Editorial layer — 厚信息 + 潜台词观点（不写热度、不把信息当观点）。
"""
from __future__ import annotations

import re
from typing import Any

from de_ai_polish import polish
from fact_rank import clean_snippet, event_keywords


def pick_angle(hot_title: str, person: str, kind: str) -> str:
    if "贫穷" in hot_title or "誓词" in hot_title:
        return "誓词里被删掉的不是词，是共同风险"
    if kind == "wedding":
        return f"{person}婚礼公共话术"
    kws = event_keywords(hot_title, person)
    return "、".join(kws[:3]) if kws else hot_title[:10]


def hook_opening(person: str, hot_title: str, angle: str) -> str:
    """开头只甩判断，不写热度/热搜。"""
    if "贫穷" in hot_title or "誓词" in hot_title:
        return polish(
            f"{person}婚礼誓词里没出现「贫穷」二字——很多人以为大家在骂炫富，"
            f"其实吵的是另一件事：公共仪式里，富人愿不愿意假装自己和普通人共用同一套语言。"
            f"祝福可以是真的，但这句话的语境太硬，你一眼就能读出阶层差异。"
        )
    return polish(
        f"「{hot_title}」这事，表面是八卦，底下往往是身份和话术撞车。"
        f"我先把能核对的细节铺开，再说大家愣着不说的那句。"
    )


def write_event_narrative(person: str, hot_title: str, kind: str) -> list[str]:
    """
    事件段：编辑重述，禁止粘贴搜索残句、禁止「据××报道」。
    """
    if "贫穷" in hot_title or "誓词" in hot_title:
        return [
            polish(
                f"{person}和奚梦瑶在法国圣米歇尔山补办婚礼。交换誓词时，"
                f"他没有念完整套「无论贫穷还是富贵、疾病还是健康」，"
                f"而是改成「无论顺境还是低谷，热闹还是安静」。"
            ),
            polish(
                f"这不是换几个同义词那么简单：「贫穷/富贵」对应的是柴米油盐，"
                f"「顺境/低谷」对应的是情绪和境遇——两套坐标系本来就不一样。"
            ),
            polish(
                f"誓词后半段，他花了不少篇幅回答奚梦瑶常问的那句「你为什么爱我」："
                f"夸她不是靠豪门、是自己从模特一路打拼到国际舞台。"
                f"有人听得感动，也有人觉得：一边删掉「穷」，一边强调「你很独立」，"
                f"这两件事叠在一起，味道就复杂了。"
            ),
            polish(
                f"网友玩梗也很好懂：早年连「早鸟票」都闹过笑话的人，"
                f"要在公开誓词里硬写「贫穷」二字，确实别扭。"
                f"梗归梗，核心意思其实是：他的人生词典里，「穷」从来不是需要发誓去克服的东西。"
            ),
        ]
    if kind == "wedding":
        return [
            polish(
                f"{person}这场婚礼，镜头里全是祝福，评论区却在抠字眼。"
                f"你看到的往往是仪式片段，看不到完整上下文——"
                f"所以更容易把一句话拎出来，当成整个人设的判决书。"
            ),
        ]
    return []


def vow_highlight_box(person: str) -> str:
    return polish(
        f"誓词里反复出现的关键句，是「无论顺境还是低谷，热闹还是安静，我都会站在你身边」。"
        f"对照常见西式模板，被拿掉的是「无论贫穷还是富贵、疾病还是健康」那一整段。"
    )


def extract_netizen_lines(facts: list[str], *, limit: int = 3) -> list[str]:
    out: list[str] = []
    for f in facts:
        f = clean_snippet(f)
        for m in re.finditer(
            r"(有网友[^。！？]{8,70}|[^。]*调侃[^。！？]{4,60}|[^。]*笑称[^。！？]{4,60})",
            f,
        ):
            line = m.group(0).strip()
            if "本文作者" in line or len(line) < 12:
                continue
            if line not in out:
                out.append(line)
            if len(out) >= limit:
                return out
    return out


def write_debate_layer(person: str, hot_title: str, netizen: list[str]) -> list[str]:
    """大家在吵什么 — 信息层，不是观点层。"""
    paras: list[str] = []
    if "贫穷" in hot_title:
        paras.append(
            polish(
                f"评论区大致分两路：一路玩梗，拿「早鸟票」「人生词典里没有穷字」开涮；"
                f"另一路替他找补，说誓词很真诚、是在夸妻子的独立。"
                f"两路人骂的不是同一件事——前者盯的是「删词」，后者盯的是「恩爱」。"
            )
        )
        paras.append(
            polish(
                f"玩梗的人爱提「早鸟票」：不是说他没文化，而是说他的成长环境里，"
                f"「穷」从来不是需要写在誓言里共同面对的东西。"
                f"替他说话的人则强调：誓词是在夸妻子的独立，不是在炫富。"
            )
        )
        paras.append(
            polish(
                f"所以你若只回一句「有钱人的爱情也很甜」，很难平息后者；"
                f"若只回一句「凡尔赛」，又忽略了前者其实在讨论「公共话语怎么写才得体」。"
            )
        )
        return paras
    if netizen:
        paras.append(polish(f"舆论场上声音很碎，比较集中的是：{netizen[0]}。"))
    return paras


def write_unsaid_truth(
    person: str,
    hot_title: str,
    kind: str,
    event_facts: list[str],
) -> list[str]:
    """
    潜台词观点：大家心里都有、很少明说。
    禁止：热度、上热搜、情商账、让子弹飞。
    """
    if "贫穷" in hot_title or "誓词" in hot_title:
        p1 = polish(
            f"有句话很少人明说：普通人誓词里的「贫穷」，其实不是修辞，是一条风险共担条款——"
            f"意思是万一哪天钱没了、病来了，我还在这儿。"
            f"{person}把它换成「顺境与低谷」「热闹与安静」，换掉的不是两个字，"
            f"是婚姻里唯一需要两个人一起扛的「匮乏」。"
            f"低谷可以是情绪低谷，可以是舆论低谷，但很难是「账户见底」那种低谷——"
            f"这才是路人别扭的根源，不是他爱不爱老婆。"
        )
        p2 = polish(
            f"大家也都看见他在夸奚梦瑶：不靠豪门、自己打拼、从模特走到国际舞台。"
            f"这话若放在私下，是体贴；放在全网可见的誓词里，却像一边拆掉「贫穷」，"
            f"一边强调「你很能挣钱/你很独立」——"
            f"潜台词会变成：我们的婚姻不需要讨论穷，只需要讨论你有多值得。"
            f"你品品，这不是「会不会说话」，是公开仪式该不该继续借用普通人的誓言模板。"
        )
        p3 = polish(
            f"还有一层更尖的：删词未必是傲慢，可能是诚实——"
            f"他真的不知道「贫穷」该怎么说、怎么说才不像在表演。"
            f"但诚实和得体可以同时成立：你可以选择不写这句，"
            f"不必用一套「听起来很美、细想全是特权」的话术，去覆盖那套老模板。"
            f"网友嘲的不是爱情，是「仪式还要走流程，却不愿在流程里假装一下众生平等」。"
        )
        # 若素材里有「谢谢」梗，补第四段
        blob = " ".join(event_facts[:6])
        if "谢谢" in blob or "thank" in blob.lower():
            p4 = polish(
                f"顺便一提，奚梦瑶当年曾用「谢谢」回应他的「我爱你」——"
                f"有人解读为克制，有人解读为距离感。"
                f"这类细节和「删贫穷」叠在一起，会让旁观者更确信："
                f"这段关系里，「表达」的方式一直和大众预期不同，这次誓词只是又一次显形。"
            )
            return [p1, p2, p3, p4]
        return [p1, p2, p3]

    if kind == "wedding":
        return [
            polish(
                f"婚礼报道最容易漏掉的是：镜头拍的是幸福，评论区读的是符号。"
                f"{person}这事，符号就是「删掉的那个词」——"
                f"大家未必真想看他受苦，只是想确认公共人物还愿不愿意在语言上和自己站在同一边。"
            )
        ]

    if event_facts:
        hint = clean_snippet(event_facts[0])[:100]
        return [
            polish(
                f"信息摆到这儿，真正刺人的往往不是「发生了什么」，而是「为什么偏偏这样表达」。"
                f"就这件事，大家心里都有数，只是很少点破："
                f"舆论要的不是更多形容词，而是一个能解释「他凭什么这样写」的答案。"
            )
        ]
    return [
        polish(
            f"细节还不够下死结论，但有一点可以确定："
            f"热搜标题里的{person}，和现场那个会改誓词的人，往往不是同一张脸。"
        )
    ]


def closing_line(person: str, hot_title: str) -> str:
    if "贫穷" in hot_title:
        return polish(
            f"{person}以后还会上新闻，但「誓词要不要提穷」这道题，"
            f"已经不只是他个人的婚礼花絮——"
            f"它问的是：名人还能不能、还要不要，在公开场合说普通人的那句誓言。"
        )
    return polish(
        f"你要是有不同读法，评论区可以掰扯，但尽量带着「删词」或「夸妻」其中一条线来说，"
        f"别只扔情绪词。"
    )


def h2_event(person: str) -> str:
    return f"先把{person}这场婚礼说清楚"


def h2_debate() -> str:
    return "评论区其实在吵两回事"


def h2_unsaid() -> str:
    return "大家愣着不说的那句"


def h2_reader() -> str:
    return "你咋看"

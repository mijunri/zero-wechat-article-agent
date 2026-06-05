#!/usr/bin/env python3
"""
Editorial — 活人感吃瓜口吻：短句、口语、有梗；不要论文腔和互动问卷。
"""
from __future__ import annotations

import re

from de_ai_polish import polish
from human_voice import humanize
from meme_harvest import fallback_memes


def _say(text: str) -> str:
    return polish(humanize(text))


def pick_angle(hot_title: str, person: str, kind: str) -> str:
    if "贫穷" in hot_title or "誓词" in hot_title:
        return "誓词里没穷字，但有钱人的浪漫和穷人的模板不是一套"
    return hot_title[:12]


def hook_opening(person: str, hot_title: str, memes: list[str]) -> str:
    if "贫穷" in hot_title or "誓词" in hot_title:
        lines = format_meme_lines(memes, hot_title, max_items=1)
        meme_bit = ""
        if lines:
            meme_bit = f"网友已经总结好了：{lines[0]}。"
        return _say(
            f"{person}婚礼誓词我扫了一眼，整段没「贫穷」俩字。"
            f"甜可能有，但听着偏硬，那股阶层味儿藏不住。"
            f"{meme_bit}"
        )
    return _say(f"「{hot_title}」这事儿，瓜不大，但话头够损。")


def write_event_narrative(person: str, hot_title: str, kind: str) -> list[str]:
    if "贫穷" in hot_title or "誓词" in hot_title:
        return [
            _say(
                f"{person}跟奚梦瑶在法国补办婚礼。"
                f"誓词那块，别人念「无论贫穷还是富贵、疾病还是健康」，"
                f"他改成「无论顺境还是低谷，热闹还是安静」。"
                f"你琢磨一下：一个聊的是油盐酱醋，一个聊的是心情和排场。"
            ),
            _say(
                f"后面大段在回答「你为什么爱我」，夸老婆是自己拼出来的，"
                f"少写「我养你」那种霸总句。"
                f"听得人一边觉得甜，一边想：行，穷字你是一字不提啊。"
            ),
        ]
    if kind == "wedding":
        return [_say(f"{person}婚礼镜头里全是糖，争议全在誓词那几个字上。")]
    return []


def format_meme_lines(memes: list[str], hot_title: str, *, max_items: int = 6) -> list[str]:
    if "贫穷" in hot_title or "誓词" in hot_title:
        pool = fallback_memes(hot_title)
    else:
        pool = []
        for m in memes or []:
            m = re.sub(r"&#\d+;|🌟", "", m).strip()
            if 10 <= len(m) <= 44 and "引发" not in m and "热议" not in m:
                pool.append(m)
        pool.extend(fallback_memes(hot_title))
    lines: list[str] = []
    for m in pool[:max_items]:
        punch = m.rstrip("。！？").strip()
        if punch:
            lines.append(punch if punch.startswith("「") else f"「{punch}」")
    return lines


def write_meme_section(memes: list[str], hot_title: str) -> tuple[str, list[str], str | None]:
    items = format_meme_lines(memes, hot_title)
    if not items:
        return "", [], None
    intro = _say("摘录几条反复复读的，嘴是真毒：")
    paras = [f"· {item}" for item in items]
    return "网友怎么损的", paras, intro


def write_punchline(person: str, hot_title: str, kind: str, _event_facts: list[str]) -> list[str]:
    if "贫穷" in hot_title or "誓词" in hot_title:
        return [
            _say(
                f"说白了，普通人誓词里写「贫穷」，是怕以后得一块儿扛事儿。"
                f"{person}写顺境低谷，没想着恶心谁，「穷」压根不在他的人生选项里。"
                f"你让他硬念那俩字，比让他背早鸟票还别扭。"
            ),
            _say(
                f"他把「疾病还是健康」也换成了「热闹还是安静」。"
                f"听着像文艺，其实就是：我俩的日子，不太会出现你只能在家喝粥那种剧情。"
            ),
            _say(
                f"还有个小彩蛋：奚梦瑶当年用「谢谢」回他的「我爱你」。"
                f"有人觉得克制，有人觉得像商务回复。"
                f"他俩一直就这么说话，誓词不过是又让人看见了一回。"
            ),
        ]
    return [_say(f"{person}这事儿，最后留人的，常常是那句话怎么被读。")]


def closing_line(person: str, hot_title: str) -> str:
    if "贫穷" in hot_title:
        return _say("婚礼会结束，这句誓词八成还能当梗用好一阵。")
    return _say(f"瓜吃完了，{person}下一句估计更难接。")


def h2_event(_person: str) -> str:
    return "先把事儿捋一遍"


def h2_punchline() -> str:
    return "说句难听的"

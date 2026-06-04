"""Lightweight de-AI pass on Chinese prose (entertainment-article §第5步)."""
from __future__ import annotations

import re

_REPLACEMENTS = [
    (r"本质上[，,]?", ""),
    (r"归根结底[，,]?", ""),
    (r"值得注意的是[，,]?", ""),
    (r"不得不说[，,]?", "说实话，"),
    (r"综上所述[，,]?", ""),
    (r"从某种意义上[，,]?", ""),
    (r"显而易见[，,]?", ""),
    (r"毋庸置疑[，,]?", ""),
    (r"此外[，,]", "还有，"),
    (r"然而[，,]", "但问题是，"),
    (r"正式落幕", "告一段落"),
    (r"但很少有人认真想过[，,]?", ""),
    (r"大家都忽略了[，,]?", ""),
    (r"前者是", ""),
    (r"后者是", ""),
    (r"说白了，说白了", "说白了，"),
]


def polish(text: str) -> str:
    from prose_guard import guard_prose  # noqa: WPS433

    from prose_guard import ban_contrast_rhythm  # noqa: WPS433

    out = guard_prose(text)
    out = ban_contrast_rhythm(out)
    for pat, repl in _REPLACEMENTS:
        out = re.sub(pat, repl, out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()

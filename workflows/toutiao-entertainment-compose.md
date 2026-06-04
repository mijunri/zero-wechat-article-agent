# Workflow：头条娱乐成稿约束

适用：`pipeline_daily_toutiao_entertainment.py`、`compose_from_research.py`、`entertainment-article` Skill。

## 硬性禁用句式

### 1. 「不是 A，而是 B」/「不是 A，是 B」

**全文禁止**（含变体：不是说不、往往不是、倒不是…而是）。

| 禁止 | 改法示例 |
|------|----------|
| 不是说不甜，是听着太硬 | 甜可能有，但听着太硬 |
| 不是故意恶心谁，是穷不在选项里 | 「穷」压根不在他的人生选项里 |
| 往往不是真相，是那句话怎么被读 | 留下来的，常常是那句话怎么被读 |
| 删的不是一个词，而是穷 | 删掉的其实是「穷」这档人生体验 |

实现：`prose_guard.ban_contrast_rhythm()`，成稿前 `paragraph_ok()` 会拒稿。

### 2. 其他（见 `entertainment-article/SKILL.md`）

- 禁止「据××报道」
- 禁止「你咋看」式互动收尾
- 禁止文末署名/免责声明块
- 活人感口语，禁止论文腔（风险共担、匮乏、坐标系）

## 流水线检查点

```text
research_topic（含梗搜索）
  → bundle.memes[]
  → compose_from_research
  → prose_guard + human_voice + ban 不是…而是
  → publish_toutiao
```

发布前自检（脚本可代劳）：

```bash
python3 .claude/skills/entertainment-article/scripts/lint_prose.py --html-file article.html
```

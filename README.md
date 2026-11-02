# ✨ AI隐身术 - 让AI写的内容"活"过来

> 给已写好的中文内容做「去 AI 味」改写：先按 AI 文本的典型特征逐条体检（套话开头、三段式排比、万能过渡词、过度对称的句子、空泛形容词堆叠），再逐句改写成人话，并输出一份可核对的体检报告。适用于公众号、讲稿、书评、小红书笔记等需要读起来像真人写的场景。核心是改写方法与判据，不依赖任何外部服务。

**版本** 1.1.0 ｜ **技能名** `ai-text-humanizer`

【问题分布】 - AI高频词汇：3处（"综上所述"、"由此可见"） - 否定式排比：2处 - 机械节奏：平均单句28字，变化不足 - 口语化表达：0处

## 用法

**发送你的文本 + 需求**，例如：

```
帮我把这篇文章去AI味，改得更像真人写的
[粘贴你的文章内容]
```

或

```
检测一下这段文字的AI浓度
[粘贴你的内容]
```

## 安装

把本目录整个复制到你的 agent 技能目录（如 `~/.agent/skills/` 或所用工具的 skills 目录）：

```bash
git clone https://github.com/WilliamWang6586/ai-text-humanizer.git
cp -r ai-text-humanizer "<你的技能目录>/"
```

放进去后，agent 读到 `SKILL.md` 即可按其中的触发条件调用。

## 文件

- `SKILL.md`
- `references/01-AI-Pattern-Library.md`
- `references/02-Humanization-Techniques.md`
- `references/03-Quality-Metrics.md`
- `references/04-Scene-Case-Library.md`
- `scripts/ai_taste.py`

## 说明


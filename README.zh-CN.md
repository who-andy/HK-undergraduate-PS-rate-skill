# PS Evaluator Skill v0.4.0

本科个人陈述评估 Skill，采用**动态专业研究**模式，适用于港五及其他大学。Skill 内不预置 HKU、HKUST 等特定 Major 的固定画像，也不会杜撰各校内部 PS 评分权重。

## 港五 PS 规则基线

见 `requirements/hk-five-2027.json` 与 `references/hk-five-requirements.md`。港大 1000 词共用，港中文 6000 字符共用（医学例外），港科大要求 PS 但通用字数上限待核实，城大官方 FAQ 提到每专业 Applicant Statement，理大大部分专业可选提交。所有规则按学校、专业、申请途径与年份核实；学校内部评分权重未知。

## 工作流程

1. 确认大学、准确专业名称、入学年份、申请途径，以及同一篇 PS 是否覆盖多个志愿。
2. 使用可用的搜索能力查找官方英文招生要求和专业培养目标。分别记录提交规则、课程事实、推导出的专业相关能力、未解决事项及资料来源。
3. 先用统一 Rubric 评价文章本身的质量（70 分），再针对**每个目标专业**单独评价匹配度（30 分）。70/30 是研究用途的实验权重，不代表港校官方标准。
4. 输出原文证据、评分理由、重要问题、各专业匹配度、可靠性提示及来源。若无法核实官方专业资料，只输出通用评估或注明专业评分暂不可靠。
5. 支持不同版本比较、同一文书跨专业比较和 Benchmark 一致性测试。

## PS 得到多少分代表什么水平？

以下等级是这套 **70 分通用质量 + 30 分专业匹配度** 的实验性解释。它们不代表港校官方评分、录取概率或申请人百分位。

| 总分 | 等级 | 典型表现 |
|---|---|---|
| 95–100 | 极强 | 几乎所有维度都有深入分析、可信证据和准确的专业匹配。 |
| 90–94 | 优秀 | 思考有深度，个人贡献明确，专业相关论证充分。 |
| 85–89 | 很强 | 动机与论据有说服力，只有少数短板。 |
| 80–84 | 良好 | 结构和经历扎实，仍可深化内容或专业联系。 |
| 70–79 | 中等，有明显改进空间 | 有清晰动机，但存在较明显的实质性不足。 |
| 60–69 | 偏弱 | 证据、分析或专业相关性明显薄弱。 |
| 0–59 | 需要重构 | 核心论证和结构需要较大的调整。 |

90 与 80 的差异必须通过具体评分维度和原文证据解释。研究不到对应专业的官方信息时，仅给通用评分 /70，不能转换成 /100；部分核实的专业信息只能产生暂定等级。字数超限、已确认的重大事实问题应单独标成提交阻碍，即使总分达到 95 也不能忽略。详见 [`references/score-interpretation.md`](references/score-interpretation.md)。语言质量已纳入评分，贡献 5 分。

## 安装

```bash
npx skills add who-andy/HK-undergraduate-PS-rate-skill --skill ps-evaluator
```

也可以将 仓库根目录 放到 Claude Code 的 `~/.claude/skills/ps-evaluator/` 或 Codex 的 `~/.agents/skills/ps-evaluator/`。Skill 不依赖 AIOS，不需要默认购买模型 API。

## 调用例子

> 使用 ps-evaluator 评估我的 2027 年国际 A-Level 申请 PS，目标为[大学][完整专业名]。先核对官方英文招生规定和课程结构，给出出处，再评价文章质量和专业匹配度。如果同一篇 PS 覆盖两个志愿，分别检查两者。

## 结构检查

```bash
cd skills/ps-evaluator
python3 scripts/validate_profiles.py --root .
python3 -m unittest discover -s tests -v
python3 scripts/aggregate_scores.py --rubrics . --input examples/evaluations.synthetic.json
python3 scripts/benchmark.py --input examples/benchmark.synthetic.json
```

Python 脚本验证评分格式、求和和评委分歧，不负责上网、调用 AI 或验证录取概率。示例样本均为虚构数据。详细规则见 `references/research-protocol.md` 和 `references/output-schema.md`。

真实 PS、申请人资料、个人化评估报告不得擅自提交到公共 GitHub。

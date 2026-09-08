# Claude 原生历史只读跟进：10 次保留记录

这是同一份缺证据的合成本地历史导出记录的只读审核，不是健康对照、自然加载、真实导出执行、真人试用或最终 Codex 矩阵。全部最终回答中的历史业务结果仍为 UNVERIFIED；评分衡量审核行为，不是产品通过。

| 调用 / 公开原回答 | Skill 版本 | 实际加载证据 | 冻结断言 | 耗时（秒） | CLI 估费（USD） |
| --- | --- | --- | --- | --- | --- |
| [initial-slash](runs/initial-slash/final.md) | baseline-7d94bb6 | UNVERIFIED | 2/4 | 27.138 | 0.03961965 |
| [slash-replay](runs/slash-replay/final.md) | baseline-7d94bb6 | UNVERIFIED | 2/4 | 34.675 | 0.04986525 |
| [explicit-read](runs/explicit-read/final.md) | baseline-7d94bb6 | 完整 Read | 3/4 | 24.471 | 0.03724860 |
| [corrected-r1](runs/corrected-r1/final.md) | history-v1 | 完整 Read | 3/4 | 32.542 | 0.04378170 |
| [baseline-r1](runs/baseline-r1/final.md) | baseline-7d94bb6 | 完整 Read | 3/4 | 35.172 | 0.04405740 |
| [history-v2-r1](runs/history-v2-r1/final.md) | history-v2 | 完整 Read | 4/4 | 34.919 | 0.04078095 |
| [final-r2](runs/final-r2/final.md) | history-v2 | 完整 Read | 3/4 | 33.233 | 0.04138110 |
| [baseline-r2](runs/baseline-r2/final.md) | baseline-7d94bb6 | 完整 Read | 3/4 | 42.808 | 0.03516510 |
| [history-v3-r1](runs/history-v3-r1/final.md) | history-v3 | 完整 Read | 4/4 | 35.107 | 0.04239480 |
| [history-v3-r2](runs/history-v3-r2/final.md) | history-v3 | 完整 Read | 4/4 | 42.389 | 0.05521035 |

合计：10 次完成；31/40 条断言通过，3/10 次四项全过；342.454 秒调用耗时之和；CLI 估算 **$0.42950490**，非账单核验。缓存包含在 137455 个统计 token 中，不能等同唯一输入或直接按总量计费。协调、准备、评分、规范化、其他宿主调用未计入。

## 不能省略的限制

- 两次 slash 调用缺少可见 Skill 全文加载，保持 UNVERIFIED；不是断言它一定没有被 CLI 展开。另八次 prompt 明确要求 Read Skill，不能宣传成自然发现。
- 所有实际宿主工具清单都只有 Read。零写入有工具记录及 8 个项目文件逐一前后摘要复核，但不是无限制宿主的安全能力证明。
- 保留全部失败和中间版本；V2 一过一败，V3 仅两次通过，不能据此保证修复、解释确定因果或估计长期收益。没有把同配置失败换成重试成功。
- 第四项允许准确的最小部分补证建议，但必须留明残余。V3 的编码证明细节未完整展开；R2 的目录 Read 失败后作了未获原生观察支持的目录内容陈述。细节保留在原评分。
- baseline 指旧 Skill，不是无 Skill；不把这 10 次混成配对因果增益。没有健康历史正例，所以不能证明不会一律 UNVERIFIED。

## 可复核内容

每个 runs 子目录含配置/Skill SHA、冻结 grading.json、按事件行号提取的工具调用、可公开最终回答、timing.json、原始文件 SHA。共享 inputs 保留实际合成输入；versions 保留每版实际安装的公开 Skill。原生完整流只保留本地，不放入公开副本。

规范化规则见 [normalization.json](normalization.json)，逐调用汇总见 [summary.json](summary.json)，原始来源摘要见 [source-hashes.json](source-hashes.json)。工具事件行号指未公开的原始事件行；公开提取不含模型思考流或签名。摘要不能认证采集诚实性。

可在原始本地 workspace 中离线执行 work/collect-claude-native-followup-public.mjs 重建；collector 不发 API、不执行导出或 helper，只读取明示的十份记录，生成规范化副本。标准 skill-creator viewer 另存于 functional-acceptance-workspace/iteration-7/review.html。

# SQLite 原生生成、交接与历史生命周期硬化证据

本目录保存“正常业务能通过，但超时后仍有写入者”的反例与定向修复过程。**这是历史硬化版本，不是当前集成版验收或上线批准。** 原生生成执行者之外的审查发现问题；诊断、硬化和本目录审计由同一修复执行者完成，不能称为陌生人独立验收。

## 最初生成、无 Skill 交接及维护

四次完成的原生 Codex 调用使用预先准备好的公开源码和依赖。两次生成得到相同冻结需求，但自行制作合成输入与 pytest 包；随后两个不同的新模型任务得到候选生成包、README 和需求，未得到项目 Skill 或原会话。这个无 Skill 交接不是“从零无 Skill 生成”基线，也不是外部真人试用。

| 已完成调用 | 整次时长 | input + output tokens | 真实测试运行 |
| --- | ---: | ---: | --- |
| [候选生成](generation/with_skill/final.md) | 174.389 s | 307,237 | 两次，各 5 项通过 |
| [旧 Skill 生成](generation/old_skill/final.md) | 256.507 s | 511,290 | 两次，各 1 个测试、12 个记录检查通过 |
| [新执行者无 Skill 重放](handoff/replay/final.md) | 105.146 s | 199,104 | 原入口不改，5 项通过，112 个提供文件不变 |
| [另一执行者无 Skill 维护](handoff/maintenance/final.md) | 239.367 s | 640,290 | 原包和新增字段各 5 项通过，仅 README 与测试修改 |

input 已包含 cached input。四次合计 1,657,921 tokens，不包括早期不可得用量，也不包括协调者准备/审查等成本；不是总实验用量、货币或人工节省。候选/旧 Skill 测试拆分不同，不能把 5 对 1 当成覆盖优劣。元数据分别位于 final 同目录。

保留 [生成后的独立产物审计](generation/retained-evidence-audit.json)、[交接/维护后的独立审计](handoff/retained-handoff-audit.json)和 [本次公开数据复核](curation-audit.json)。候选首轮通过后补了显式关闭 SQLite 观察连接，旧 Skill 补了运行时身份记录，各自保留两次。它们不是零修改一次成型，也不是为了抹掉失败而只留最终结果。

维护是执行前冻结的[合成字段要求](handoff/maintenance/MAINTENANCE-REQUIREMENTS.md)，不是外部反馈：新增邮编字符串和首选名，包含前导零、null 与空字符串。原 23 条断言保留、加 2 条，见 [修改差异](handoff/maintenance/acceptance.diff)与 [原执行者验证](handoff/maintenance/final-validation.json)。五个损坏内存值被比较器拒绝是观察器控制，不是五个应用失败。内部记录 216.048 秒的起点较晚，整次调用以 239.367 秒为准。

完整三条联系人输入/导出、原始 CLI JSON 输出、全部保留边界快照、主要命令和终态分别在 `generation/{with_skill,old_skill}/run-2/`、`handoff/replay/run-1/`、`handoff/maintenance/{baseline,changed}/`。这些数据按原始字节复制；最早生成轮保留 stdout 和源摘要，完整首次数据仍只留在本地原记录。

最初 [host 初始化失败](starts/initial-host-failure/pair-result.json)和 [operator-stopped pair](starts/operator-stopped/pair-result.json)另存。后者在约 33.95 秒由操作者 SIGTERM 中止，虽 metadata 的计时器 `forced` 字段为 false，也不是无干预完成。两组 usage 均不可得，不能按零计。原因与准备范围见 [原执行说明](generation/EXECUTION-NOTES.md)。它们均不计入完成的四次调用。

公开包不包含完整 native 流、模型思考、DB 或完整 before/after 清单。内容、值类型、源摘要和公开命令关联可复核；“未加载 Skill”等全流负面事实在此仅由独立审计/元数据归因支持，不能声称本精简包可重新证明全部执行边界。历史 final 中原工作副本链接按路径归一化保留，并非都对应本公开树的文件。

## 业务结果与交付阻断

固定合同要求：导入合成联系人后，在新 CLI 进程中完整读取并导出 JSON；字段值原样保留；重复 id 插入必须可见拒绝且保留全部联系人；无关表的结构和行在每个边界都不变。原包两次原生运行均为 5/5，但这只建立正常业务路径：[第一次](original/native-run-1.stdout.txt)、[第二次](original/native-run-2.stdout.txt)。

原生成包的外层 runner 超时只 kill pytest 单 PID。内层 CLI 的 20 秒计时和 PID 日志都由 pytest 执行：父进程被杀后计时器消失，CLI 没有“自身的 20 秒”，日志也未必写出。因而当时阻断的是安全交接/重跑，不是否定已观察到的正常业务结果。

## RED → 探针 → GREEN

| 保留的尝试 | runner 退出后观察 | 活动 PID 启动记录 | 限定结果 |
| --- | --- | --- | --- |
| [RED 1](fault/red-1/result.json) / [RED 2](fault/red-2/result.json) | 心跳 45→155 / 150 字节，CLI 仍活 | 无 | RED |
| [只修组回收](fault/group-only/result.json) | CLI 已退出，心跳 40→40 | 无 | 仍 RED |
| [首次 GREEN](fault/green-1/result.json) / [冻结 GREEN](fault/green-final/result.json) | CLI 已退出，心跳 40→40 | 有 | 限定反例 GREEN |
| [真实 pytest RED](fault/native-red/result.json) | 实际收集 5 项并进入 fixture；心跳 45→150，CLI 仍活 | 无 | RED |
| [真实 pytest GREEN](fault/native-green/result.json) | 同故障，CLI 已退出，心跳 40→40，owned group absent | 有 | 限定反例 GREEN |

所有故障运行的 runner 都返回预期超时码 **124**，不是业务 PASS。真实 pytest 的 [RED 输出](fault/native-red/runner.stdout.txt) 和 [GREEN 输出](fault/native-green/runner.stdout.txt)都停在第一个测试，没有把被中断的 5 项写成通过。

合成故障只替换第一个 identity CLI：它在本次 owned 目录写心跳，6 秒自行退出；外层 180 秒 wait 缩为 0.4 秒，内层 20 秒缩为 1 秒。最小版本直接进入真实 fixture，另两次使用真实 pytest 引擎。监护器持有本次启动的准确进程组，并在 finally 清理；没有全局 pkill，也不按旧 PID 自动清理。故障记录中的原始 argv 仍是被替换调用的请求，不代表它在故障运行中真实执行。详见 [provenance](provenance.json)。

## 修复与不变量

修复限制在全新 acceptance 副本：

- pytest 建独立会话/组，启动即记 PID；退出、超时、SIGINT/SIGTERM、可捕获异常都走 TERM→有界等待→KILL→wait，并确认 owned group 不存在。
- CLI 启动即记 PID/PGID，仍继承 pytest 组；单命令超时终止并等待直接子进程，然后中止 fixture，不继续观察可能仍被写入的数据库。
- 不能确认终态时为 UNKNOWN；父自然退出但留有子进程也不能报成功。文档移除“CLI 自带 20 秒”的错误说法。
- 应用源码未动，5 个业务测试函数 AST 与原包一致；[审计](hardening/audit.json)保留原包和硬化包的完整文件摘要、10 对启动/终态关联及真实 JSON/只读数据库的独立输入比对结果。数据库本身不公开。

冻结版本实测：[标准库 9/9，5.866 秒](hardening/stdlib-9.log)；[原生 sqlite-utils 5/5，2.99 秒](hardening/native-5.stdout.txt)。[早期新副本迁移 5/5，3.59 秒](migration-early/native-5.stdout.txt)单列，不与生成执行者的两次或硬化作者的运行混为一次。

**后续审查仍发现缺口：** 根任务在迁移集成时发现原故障测试的小时间窗可能混入解释器启动时间，又发现插件检查发生在 import 之后的风险，继续修订测试/预检。它们不被上述历史 9/9 或 5/5 覆盖。后续集成记录另见 [checks](../checks/)，当前包见 [示例目录](../../../../examples/sqlite_utils/acceptance/)；本目录不复写或宣称后续全集结果。

## 命令与适用边界

以下是从工作区根执行的历史命令；原始工作副本/环境不随本公开证据包分发，路径不是新的执行授权：

```sh
work/sqlite-utils-onboarding-env/bin/python -B work/sqlite-pack-hardening/debug/lifecycle_fault.py --native-pytest --label UNIQUE
# RED 另指定：--project work/sqlite-pack-hardening/red-project
PYTHON_3_14_BIN/python3.14 -B -S -m unittest discover -s work/sqlite-pack-hardening/project/acceptance -p test_lifecycle.py -v
work/sqlite-utils-onboarding-env/bin/python -B work/sqlite-pack-hardening/project/acceptance/run.py
```

POSIX 继承组回收不保证 runner 被 SIGKILL、主机失效或子进程主动 setsid 脱组后的清理；这些情况保持 UNKNOWN，保留证据、不自动重试/删除。组消失只证明资源释放，不证明中断写入成功或回滚。以上没有成本节省、跨环境普适性或生产就绪结论。

## 来源、字节与脱敏

上游为 [simonw/sqlite-utils 的固定提交](https://github.com/simonw/sqlite-utils/tree/85b1be10c81d9dd3567e36faf8dd411e4a8789bd)，其 [Apache-2.0 LICENSE](https://github.com/simonw/sqlite-utils/blob/85b1be10c81d9dd3567e36faf8dd411e4a8789bd/LICENSE)只说明上游许可，不替本仓库选择许可证。合同与依赖环境由协调者预先准备，不是零准备的陌生项目测试。

[provenance.json](provenance.json)逐文件记录原始/公开 SHA-256、字节数和变换：替换私有工作区绝对根、机器名及解释器目录；对需派生的无末尾 LF 文本补一个 LF，逐项标记。metadata 是明确列出 selected_keys 的结构化节选，省略完整清单、认证描述和宿主诊断，缺失字段保留 null；联系人 JSON、快照及不需脱敏的原始数据直接逐字节复制。返回码、时长、心跳计数、PID 关联、源文件摘要和断言结果不变。141 份来源记录中 84 份字节完全相同，其余变换逐项列明；README、provenance 和 curation-audit 是新写的索引/复核，不伪称原始输出。未复制数据库、完整上游源码、模型思考、私有会话或凭据。哈希用于复核字节，不构成对采集真实性的独立保证。

# Functional Acceptance · 功能验收

[English](README.md)

**功能写好了，用户真的能用吗？**

Functional Acceptance 是一个帮助 AI 编程助手按真实使用流程验收功能的 Skill。它指导助手核对用户应得到的结果，给出证据，并留下下次还能运行的测试。

比如：导出命令提示成功，CSV 却少了最后一条数据。验收要做的是打开文件、核对内容，而不是看到命令返回 `0` 就结束。

> 可安装的开发预览版，尚非受支持的正式版本。请先在隔离测试项目中试用；许可证仍待确定。

## 在你的项目中开始

### 1. 安装

在待使用 Skill 的项目根目录运行。下面使用已测试的第三方安装工具 `skills@1.5.24`，需要 Node 22.20+；执行时可能联网下载工具和仓库。

**仅用于首次安装：** 先检查 `.agents/skills/functional-acceptance/` 是否已存在；Claude Code 对应 `.claude/skills/functional-acceptance/`。安装会替换同名目录，包括你的本地修改。已有安装请按[升级指南](UPGRADING.md)处理。

```sh
DO_NOT_TRACK=1 npx --yes skills@1.5.24 add Quine-rq/functional-acceptance --skill functional-acceptance --agent codex --copy --yes
```

使用其他助手时，把 `codex` 换成 `claude-code`、`cursor`、`github-copilot` 或 `opencode`。这些是已检查的安装目标，不代表实际执行能力都验证到了同一程度，详见[适配范围](#适配范围与当前限制)。

必要时重新加载助手，确认它发现的是当前项目中的 `functional-acceptance`。没发现时，先按[安装与发现检查](INTEGRATIONS.md#verify-the-installed-copy)排查。无需全局安装或新模型账号，Skill 也不附带运行环境。上面的命令跟随默认分支；要固定版本，请[指定已审阅的提交](INTEGRATIONS.md#pin-update-recover-and-remove)。

### 2. 说清你要验收的结果

在待验收项目中，点名 Skill 并描述功能预期。例如，项目有 CSV 导出功能时可以说：

> 用 functional-acceptance 验收这个项目的 CSV 导出：应有的记录和字段都不能丢，也不能覆盖已有目标文件。只用合成数据和临时测试文件。先列出检查项，再执行，最后给我证据和复验命令。不要修改业务代码。

把导出要求换成你自己的功能和限制即可，不需要先学一套配置格式。助手应使用项目已有工具；缺少必要工具、观察手段或权限时，应明确指出缺口，而不是宣称通过。

第一次只想看看计划，可以说：“用 functional-acceptance 规划这个功能怎么验收，不要运行命令或创建文件。”交付完整计划就完成了这个请求，不需要为了规划先提供凭据。

### 3. 拿到能核查的结果

执行前，助手应给出简短的[验收前检查表](skills/functional-acceptance/references/acceptance-contract.md)：保留原始目标，列清每个检查项、独立预期和获授权范围。执行后，给出包含证据和复验方法的[验收报告](skills/functional-acceptance/references/acceptance-report.md)。

下面是交付形式示意，不是新增的一次实测记录：

```text
结论：失败——导出返回 0，但缺少记录 r-005。
完整性：FAIL，实际 4 条，独立预期为 5 条。
已有目标文件：PASS，拒绝覆盖，前后内容一致。
覆盖：两项要求均已观察。执行：已结束。
清理：仅保留已标识的测试证据，没有活动写入进程。
复验：附原生命令、工作目录、输入数据和证据位置。
```

没观察到的项目应标为 **UNVERIFIED（未验证）**，说明阻塞原因和下一步。发现真实缺陷也是有用的验收结果，但不等于获得修复或上线授权。两份模板默认在对话中填写，不强制往项目里生成文档。下面的可运行示例会产生实际证据，而不只是这段示意文字。

## 运行示例

示例把三页合成数据导出成真实 CSV 文件，再重新读取，与事先确定的五条记录逐项比较。其中一个版本故意漏掉最后一页，却仍然返回成功。

无需安装依赖、登录账号、联网或安装 Skill。在仓库根目录运行，需要 Python 3.10+，以及支持硬链接和不跟随符号链接访问的 POSIX 本地文件系统。本地示例检查已在 macOS + Python 3.10.20 和 3.14.4 上运行。

```sh
python3 -B examples/paginated_export/accept.py --case healthy
python3 -B examples/paginated_export/accept.py --case defect
python3 -B examples/paginated_export/accept.py --case missing-observation
```

| 场景 | 实际发生了什么 | 验收结论 | 退出码 |
| --- | --- | --- | --- |
| `healthy` | 五条记录及各字段全部吻合 | PASS：通过 | 0 |
| `defect` | 导出返回 0，但缺少记录 `r-005` | FAIL：失败 | 1 |
| `missing-observation` | 文件已生成，但故意不提供必需的观察记录 | UNVERIFIED：未验证 | 2 |

后两种退出码是预期结果，请分别运行，不要用 `&&` 串联。UNVERIFIED 表示证据不足，不等于导出功能有缺陷。报告还会单独说明验收覆盖情况和清理状态，不与通过、失败混为一谈。

### 查看证据

每条命令都会在本仓库的 `.acceptance/runs/` 下创建独立目录，并打印位置。打开其中的 `report.md` 查看结论，或读取 `report.json` 获取结构化结果。同一目录还保留了验收标准、实际执行的程序和输入快照、进程记录，以及 `attempt-1/output.csv`。

报告交付失败时，摘要会保持“未完成”，并标明本次实际创建的目录。若其中已有 `report-delivery.json`，可查看报告写入或清理失败的详情。中断留下的临时文件不是正式报告，历史报告中的 PASS 也不能替代本次尚未完成的交接。

每次运行的材料独立保留在本地。需要指定位置时，添加 `--run-dir NEW_DIRECTORY`；程序会拒绝使用已存在的运行目录。不再需要某次材料时，用文件管理器删除那一个已确认的目录即可；删除后，这次证据就无法再次核查。

如果只想检查导出程序，不使用 Skill 或报告工具，可按[独立示例说明](examples/paginated_export/README.md)运行。

## 适配范围与当前限制

Skill 采用 Agent Skills 格式，使用项目已有工具，不限定语言或框架；实际能验什么，仍取决于工具、权限和观察条件。只做计划不需要 Python，可选 CSV 核验脚本另有上文说明的 Python/POSIX 要求。

| 助手 / 环境 | 已实际检查 | 尚未验证 |
| --- | --- | --- |
| Codex | 原生执行、计划、历史证据审核、回归试验及 12 次 Cookiecutter 重复运行 | 对自然、未穷举验收点的用户请求是否有收益，以及外部陌生用户复用 |
| Claude Code | 明确加载 Skill 后的实际只读历史审核 | 自然加载、健康历史判别、执行完整用户流程 |
| Cursor、GitHub Copilot、OpenCode | 项目内安装、替换和卸载 | 原生发现与实际执行效果 |
| 手机 / 其他远端服务 | 仅为预期应用场景 | 真机和具体服务的验收 |

这些观察对应[原生评估](NATIVE-FOLLOWUP-RESULTS.md)与[安装记录](INTEGRATIONS.md)中的版本和环境，不是对后续指令改动的行为认证。普遍适配、节省时间和生产可用性都还没有得到证明。

内置示例覆盖的是**合成分页数据 → 真实 Python 进程 → 本地 CSV 文件**。报告检查导出完整性和字段内容，输入异常与文件安全另有测试。

[sqlite-utils 回归包](examples/sqlite_utils/README.md)检查导入、独立读取、导出、重复主键拒绝和无关数据保留；[linkding 回归包](examples/linkding/README.md)检查真实浏览器、服务端与数据库流程，包括持久化、账号隔离和恢复。它们是原生示例，不是通用适配器。接入协助和修正过程均有记录，尚不能证明外部用户能从零独立接入。

详细尝试及失败保留在[初期宿主试验](evals/results/2026-09-08-host-smoke/README.md)、[协助完成的 linkding 研究](evals/results/2026-09-08-linkding/README.md)、[加固记录](evals/results/2026-09-08-product-hardening/README.md)和[原生后续评估](NATIVE-FOLLOWUP-RESULTS.md)中。测试数量不能证明用户收益。

### 安全与证据边界

- 在已授权的测试环境中使用。验收本身不授权修改业务代码、操作生产数据、推送提交或发布评论。
- 缺少工具或观察结果，就保留为未验证项。模拟服务只能证明实际测到的行为，不能用缩小后的测试范围替代用户原本的要求。
- 核验工具直接读取 CSV 并与固定期望比较，不执行报告中的命令，也不接受外部填入的“通过”。文件摘要能发现材料被改动，但不能证明采集过程真实，或发现一开始就漏掉的需求。
- 报告默认留在本地，不会自动脱敏。分享前须检查内容，不要把凭据、私有日志或用户数据放进公开 Issue。

支持的核验规则与信任边界见[材料格式说明](skills/functional-acceptance/references/material-format.md)。

## 开发检查

```sh
python3 -B -m unittest discover -s tests -v
python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_lifecycle.py -v
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_identity.py -v
```

第一条检查核验工具、证据采集程序、Skill 包及原生示例的安全和报告规则；第二条独立检查导出程序；第三、四条使用合成对照检查 SQLite 回归包的生命周期和导入前校验，不运行其业务流程。这些命令都不运行依赖本机环境的 linkding 浏览器流程。检出缺陷的测试通过，不表示那次缺陷导出正确。

[`EVALUATION-HARNESS.md`](EVALUATION-HARNESS.md) 说明重复评估使用的开发期只写一次调用账本。runner 位于 `skills/functional-acceptance` 之外，不进入安装包，也不授予命令权限；它只记录一次已审阅的子进程，并在超时、观察器失败、重复调用或仍有受管后代进程时保守失败。

安装集成检查仅供开发，需要 Node 22.20+：

```sh
npm --prefix integration ci --ignore-scripts --no-audit --no-fund
npm --prefix integration test
```

它们在临时项目中实际调用固定版本的 `skills` 安装工具，不要求登录 Agent 或全局安装 Skill。这些 npm 依赖不会进入用户的 Skill 包。

已有安装需要更新时，先按[暂存升级指南](UPGRADING.md)检查本地修改、保留备份。
[本轮复用与恢复结果](REUSE-RESULTS.md)记录了复制中断恢复、旧材料兼容和重复
浏览器回归。此前被阻断的宿主与陌生项目评估已经补做，见[独立的后续记录](NATIVE-FOLLOWUP-RESULTS.md)，旧失败记录不覆盖。

[CI](.github/workflows/checks.yml) 在 Ubuntu 24.04 + Python 3.10/3.14 上运行原生检查，另有 Node 22.22.3 安装集成任务，使用只读权限和固定到提交的 Actions。接入源码 `f4b1ef9` 的三个任务均已通过（[运行记录](https://github.com/Quine-rq/functional-acceptance/actions/runs/34185450287)），[此前的 M2 记录](M2-RESULTS.md#remote-ci)也保留了早期失败及修正过程。使用时仍需查看对应提交的运行结果，旧版本的绿灯不能证明后续改动也通过。

## 文档与下一步

- **了解使用方法：** [Skill 指令](skills/functional-acceptance/SKILL.md)、[独立示例](examples/paginated_export/README.md)、[材料格式](skills/functional-acceptance/references/material-format.md)。
- **核对实现进展：** [M1 范围](M1-PLAN.md)、[M1 验证记录](M1-RESULTS.md)、[M2 加固记录](M2-RESULTS.md)、[路线图](ROADMAP.md)。
- **了解设计：** [产品设计](DESIGN.md)、[架构](ARCHITECTURE.md)、[评估计划](VALIDATION.md)。这些是中文详细文档，其中计划执行的评估不代表已经通过。

正式发布前，还需要验证第二种宿主稳定执行完整流程，让外部开发者在自己的项目中试用，证明相对基线的实际收益，并确定许可证和安全支持方式。[本轮原生评估](NATIVE-FOLLOWUP-RESULTS.md)逐项说明已做什么、仍有哪些失败；本地测试通过不等于成熟产品。

## 反馈与许可

如果某个功能看起来成功，实际使用却不对，欢迎提供预期行为和使用合成数据的最小复现。现阶段，这类具体案例比笼统的全平台适配需求更有帮助。

开源许可证尚未选定，当前仓库还没有应用开源许可证。

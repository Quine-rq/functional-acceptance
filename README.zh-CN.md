# Functional Acceptance · 功能验收

[English](README.md)

**功能写好了，用户真的能用吗？**

Functional Acceptance 是一个帮助 AI 编程助手按真实使用流程验收功能的 Skill。它指导助手核对用户应得到的结果，给出证据，并留下下次还能运行的测试。

比如：导出命令提示成功，CSV 却少了最后一条数据。验收要做的是打开文件、核对内容，而不是看到命令返回 `0` 就结束。

> 开发中：已有可运行的本地 CLI/CSV 示例，目前是实验性源码，尚未正式发布。

## 它怎样工作

从功能需求和待验收的项目开始，Skill 指导 AI 编程助手完成三步：

1. **说清怎样才算成功。** 明确用户要完成什么，以及怎样证明结果正确。规则不明确、缺少权限等问题要保留下来。
2. **实际核对结果。** 使用项目已有工具执行流程，检查最终产物。除了正常情况，也检查与本次需求相关的失败和恢复场景。
3. **交付结论和复验方法。** 说明哪些通过、哪里失败、哪些还没验证，附上证据和再次检查的运行说明。

Skill 提供验收方法，实际操作由助手和项目工具执行。它不替代现有测试框架，也不替你批准上线。目前跑通的是下面这条本地导出流程，其他场景仍需验证。

## 运行示例

示例把三页合成数据导出成真实 CSV 文件，再重新读取，与事先确定的五条记录逐项比较。其中一个版本故意漏掉最后一页，却仍然返回成功。

无需安装依赖、登录账号、联网或安装 Skill。在仓库根目录运行，需要 Python 3.10+，以及支持硬链接和不跟随符号链接访问的 POSIX 本地文件系统。目前实际验证的环境是 macOS + Python 3.14.4。

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

## 接入你的编程助手

开发版 Skill 已整理为独立目录 [`skills/functional-acceptance/`](skills/functional-acceptance)，采用 Agent Skills 格式，不附带新的 Agent 运行时。可选 CSV 核验脚本另需 Python/POSIX 环境；只做验收计划不需要它。

首次接入请看[安装说明与实测范围](INTEGRATIONS.md)：使用固定版本的现有安装工具，覆盖 Codex、Claude Code、Cursor、GitHub Copilot、OpenCode 五种安装目标，并说明更新、卸载的影响。**安装检查通过，不等于 Agent 已经实际完成验收。**

确认助手已加载 Skill 后，可以先说：“用 functional-acceptance 规划这个功能怎么验收，先不要运行应用。”同时提供功能预期和项目位置。实际验收再使用该助手已有且获授权的项目工具。

## 适配范围与当前限制

这套方法优先使用项目已有工具，不要求采用某种语言或框架。Web、API、命令行、桌面和移动端是计划覆盖的应用场景，不是已经验证的适配清单。

当前示例实际覆盖的是**合成分页数据 → 真实 Python 进程 → 本地 CSV 文件**。报告检查导出完整性和字段内容，输入异常与文件安全另有测试。真实上游 API、浏览器、数据库、手机和第二个项目都还没有验证。

[M1 验证记录](M1-RESULTS.md)记载了首批 77 个通过的测试方法，以及另一名 Agent 对独立示例的重跑。[M2 报告交付检查](M2-RESULTS.md)将当时测试补至 84 个方法，覆盖中断、磁盘错误和未完成交接。本轮打包与安装检查[另有记录](INTEGRATIONS.md)。这些结果不代表外部用户已经用得顺手、节省了时间，或具备生产可用性。正式版本仍待验证，克隆源码本身不等于安装了 Skill。

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
```

第一条检查核验工具、证据采集程序和可迁移的 Skill 包；第二条独立检查导出程序，不依赖 Skill 或核验工具，也会确认故意注入的缺陷能被检出。检出缺陷的测试通过，不表示那次缺陷导出正确。

安装集成检查仅供开发，需要 Node 22.20+：

```sh
npm --prefix integration ci --ignore-scripts --no-audit --no-fund
npm --prefix integration test
```

它们在临时项目中实际调用固定版本的 `skills` 安装工具，不要求登录 Agent 或全局安装 Skill。这些 npm 依赖不会进入用户的 Skill 包。

[CI](.github/workflows/checks.yml) 在 Ubuntu 24.04 + Python 3.10/3.14 上运行检查，使用只读权限和固定到提交的 Actions。M2 源码 `c26a86f` 的两个任务均已通过（[运行 #3](https://github.com/Quine-rq/functional-acceptance/actions/runs/34183660278)），[验证记录](M2-RESULTS.md#remote-ci)也保留了此前失败及修正过程。使用时仍需查看对应提交的运行结果，旧版本的绿灯不能证明后续改动也通过。

## 文档与下一步

- **了解使用方法：** [Skill 指令](skills/functional-acceptance/SKILL.md)、[独立示例](examples/paginated_export/README.md)、[材料格式](skills/functional-acceptance/references/material-format.md)。
- **核对实现进展：** [M1 范围](M1-PLAN.md)、[M1 验证记录](M1-RESULTS.md)、[M2 加固记录](M2-RESULTS.md)、[路线图](ROADMAP.md)。
- **了解设计：** [产品设计](DESIGN.md)、[架构](ARCHITECTURE.md)、[评估计划](VALIDATION.md)。这些是中文详细文档，其中计划执行的评估不代表已经通过。

接下来会验证真实宿主的调用和缺能力时的行为，在第二个获授权项目中尝试复用，并对比同一个 Agent 使用与不使用 Skill 的效果。这些验证先于正式发布。

## 反馈与许可

如果某个功能看起来成功，实际使用却不对，欢迎提供预期行为和使用合成数据的最小复现。现阶段，这类具体案例比笼统的全平台适配需求更有帮助。

开源许可证尚未选定，当前仓库还没有应用开源许可证。

# 联系人导入 CLI 回归包

本包使用 pytest 和真实 CLI 子进程，无需 Skill、外部服务或原会话。验收合同来自项目根目录 `ONBOARDING-REQUIREMENTS.md`。它验证小型合成联系人列表的持久化、跨进程读取、JSON 导出、重复主键拒绝及无关数据保留，不代表生产就绪。

## Setup 与重跑

先按[项目接入指南](https://github.com/Quine-rq/functional-acceptance/blob/main/examples/sqlite_utils/README.md)把本目录和需求合同复制到固定版本的 sqlite-utils 源码工作副本。工作目录必须是该源码根目录，而不是 Functional Acceptance 仓库。实测环境为 Python 3.14.4、sqlite-utils 4.2.1、pytest 9.1.1；使用自行准备的隔离解释器：

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B acceptance/run.py
```

迁移给另一执行者时，替换为已配置相同依赖的 Python 解释器。应用通过 `python -B -m sqlite_utils` 启动；工作目录和 PYTHONPATH 均固定到本包所在项目。运行前探针验证 `sqlite_utils.__file__` 和 `sqlite_utils.cli.__file__` 指向此项目，并拒绝未预期的应用插件。环境分发版本号只是辅助证据，源码路径及 SHA-256 才定位实际执行内容。无需读取原始取材目录。

`run.py` 是唯一推荐重复入口：每次创建新的 `artifacts/onboarding-<UTC>-<随机后缀>/`，不复用旧数据库，不覆盖旧尝试。它以白名单环境调用原生 pytest，禁用用户 site、外部 pytest 插件、字节码和 pytest 缓存；HOME、配置、临时目录、pytest basetemp 均在该次 artifacts 内。真实 pytest argv / 环境见 `invocation.json`。直接裸跑 pytest 缺少此环境不受支持。

本 runner 需要 POSIX（本次实测 macOS）。每个 CLI 的父等待器有 20 秒期限；pytest 执行期限为 180 秒，随后保留最多约 6 秒的组终止与 wait 清理时间。CLI 不自带独立的 20 秒定时器。此包没有自动场景重试。首个真实应用阶段为 CLI 导入合成无关表，而非直接创建被测联系人结果。输入常量在测试代码中独立固定，每次写入 `*.input.json`。包含乱序 id、Unicode/emoji、换行、引号、反斜线、null、空字符串、整数和小数。按 id 比较完整记录及每个字段，不依赖 JSON 空格、键序和行序。未声称覆盖所有可能的 JSON 数据类型。

## 原生入口依据与覆盖

| 要求 | 随项目保留的依据 / 已有覆盖 | 本包增加的真实观察 |
| --- | --- | --- |
| 联系人导入 | `pyproject.toml` 的 console script；`sqlite_utils/__main__.py`；`docs/cli.rst` 的插入段；`tests/test_cli_insert.py::test_insert_with_primary_keys` | 新 CLI 导入 `contacts.input.json --pk id`，关闭进程后用标准库 SQLite 只读连接检查全部值 |
| 跨 CLI 读取 | `sqlite_utils/cli.py::query`；上游多数使用进程内 CliRunner | 导入进程退出后启动新 `query` 进程，完整解析并比较 stdout |
| JSON 导出 | `docs/cli.rst` 的 rows / query JSON 段；`tests/test_cli.py::test_query_json_unicode_not_escaped_by_default` | 新 `rows` 进程生成原始 stdout，逐字节保留为 `contacts.export.json`，重新打开并检查完整内容 |
| 普通重复 id 拒绝 | `sqlite_utils/cli.py::insert` / `insert_upsert_implementation`；`tests/test_cli_insert.py::test_insert_ignore` 检查无 ignore 时非零 | 使用已存 id=17 及不同字段，要求非零退出及明确唯一约束错误；随后只读 SQL 和新 CLI 都核查全部旧联系人 |
| 无关数据保留 | 以上已读测试未覆盖整条链路的无关表 | 在 seed、import、read、export、拒绝、最终读取六个边界对比 unrelated 表、索引定义与完整行；最终表集合精确检查 |

5 个 pytest 测试共用一次有状态链路；不会因普通业务断言失败而跳过后续已经可执行的观测。基础设施/探针/初始建库失败可能使 fixture 报 ERROR，此时受影响结果为 UNVERIFIED，不能把非零退出一概认作产品失败。测试退出 0 且收集 5 项才是预期通过。

## 证据与排障

每次目录包含：

- `identity.json`、`00-identity.*`：解释器、Python/SQLite/pytest 版本、UID、实际源码加载路径、插件清单。
- `source-sha256.json`：应用 Python 源码、需求、配置和回归代码内容身份。
- `help-*.stdout`：实测 CLI 帮助；`*.started.json` 在启动后、等待前记录 argv、cwd、PID/PGID，`*.command.json` 在等待结束后记录终态、超时与退出码。前者不是退出证明；后者缺失不代表没有运行过。
- 对应 `*.stdout` / `*.stderr`：原始命令结果，包括预期被拒绝的写入，绝不删除失败输出。
- `*.input.json`、`contacts.db`、`contacts.export.json`：可检查的输入、最终数据库与原始 JSON 导出。
- `*.snapshot.json`：六个操作边界的只读数据库状态。
- `pytest.stdout.txt`、`pytest.stderr.txt`、`pytest.xml`、`pytest.started.json`、`termination.json`：测试结果、独立会话组身份、父进程 wait 结果和整个组的清理后状态。
- `writer-state.json`：正常走完后所有 CLI 已等待终止，观察连接已显式关闭。

异常时先看对应 command / stderr 和数据库只读状态。明确观察到正确对象违背合同才记 FAIL；解析/报告代码故障记测试故障及相关 UNVERIFIED；环境不可用记环境缺口。不要修改应用或放宽断言使结果通过。修正观察器后应另起全新运行目录，保留旧尝试并说明差异。

pytest 在 runner 创建的独立 POSIX 会话组内运行，所有本包 CLI 保持继承该组。CLI 等待超时时，先 kill/wait 直接 CLI，再中止 fixture，停止后续数据库观察。runner 在正常退出、总超时、SIGINT/SIGTERM 或可捕获异常后都回收该组：TERM、限时等待、必要时 KILL、wait 父进程，并核实组已不存在。父正常退出却遗留子进程也记基础设施失败（退出 70），不会被业务测试的 0 掩盖。总超时退出 124；中断返回 128+信号号。

先查 `termination.json.cleanup` 的 `terminal=true`、`leader_waited=true`、`group_after_cleanup="absent"`，再对照 started/command 记录判断哪一步尚未完成；该终态证明进程释放，不证明被中断的业务操作满足合同。`writer-state.json` 也不能代替外层组终态。未知、缺失或不完整证据一律保留目录，不自动重试、不清理。若 Popen 没有返回可持有句柄，启动状态也只记 UNKNOWN。不要通过旧记录的数字 PID 自动发信号（PID 可复用）。需要操作者在当前受控会话核实进程归属与终态；确认写入者已退出后才可只读检查原库，并在另一个全新运行目录重跑。

边界：SIGKILL 杀死 runner、主机失效、主动脱离会话的子进程不受 Python finally 保障；本包只覆盖固定原生 CLI 的继承组，不是任意 daemon 的进程树监管器。这些情况不能从缺失文件、时间戳或等待 20 秒推断安全。不要向原库盲目重试写入。

## 生命周期回归（无 pytest / sqlite-utils 依赖）

```sh
python3 -B -S -m unittest discover -s acceptance -p test_lifecycle.py -v
```

标准库 11 项生命周期测试使用限时合成写入者和 run-owned 临时目录，实际调用 `lifecycle.run_group` 及从本测试 fixture 提取的原始 `invoke` 函数，验证总超时、CLI 超时、SIGINT/SIGTERM、忽略 TERM 的升级回收、父自然退出留下子进程、启动记录写失败、启动中断没有句柄以及 UNKNOWN 拒绝假通过。内层 CLI 超时测试把 20 秒等待缩为 0.3 秒；合成总超时另有 0.5 秒等待，二者都先有界等待写入者就绪。父退出场景给启动 4 秒；父退出和内层超时分别注入慢启动，避免把解释器启动慢误判为另一种故障。不修改业务输入或业务断言。每次测试 finally 都只清理本次自建的组。

另用 `python3 -B -S -m unittest discover -s acceptance -p test_identity.py -v` 运行 3 项导入前身份检查。它提取真实 probe，使用合成模块观察插件拒绝、无插件健康和元数据异常时的导入顺序；不是完整应用验收。业务探针先查元数据，拒绝插件后不会导入应用；应保持隔离依赖不变，不把这项检查当作 Python 环境沙箱。迁移时也保留 `__init__.py`，避免其他普通同名包抢占导入。

## 清理责任

证据目前有意保留，由接手者在确认不再需要后清理。正常运行须先核对 `termination.json` 为 exited 且组已 absent、父进程已 wait、terminal=true，所有命令 terminal=true、无 timed_out，并有 `writer-state.json`。若运行被中断，按上段完成终态检查再决定清理，绝不自动从旧 PID 记录发信号。

从项目根目录仅删除明确选中的运行目录，例如：

```sh
# 用文件管理器移除已经核对终态、不再需要的那一个运行目录。
# 不使用通配符，不删除整个 artifacts。
```

以后运行使用当次实际目录名，不要通配整个 artifacts。删除某次目录同时清除其合成数据库、临时目录、隔离 HOME 和证据。不需要数据库外部恢复。保留 `acceptance/` 供回归；生命周期支持文件为 `lifecycle.py` 和 `test_lifecycle.py`，迁移时须与 `run.py`、`test_onboarding.py` 一起复制。

## 范围与交接状态

本目录是原生 Agent 生成包经审查后硬化的可迁移副本；原始生成、无 Skill 重跑、后续维护和硬化结果分开保留，见[本轮记录](../../../evals/results/2026-09-08-native-followup/README.md)。本次独立硬化复制包已经真实运行 5 项业务验收，以及上述标准库生命周期回归。没有运行全部上游测试；未执行磁盘耗尽、崩溃恢复、多写者并发等扩展故障，也没有真机、网络、生产、发布验证。这些不能从本次 PASS 外推。

# sqlite-utils 原生验收示例

把联系人导入数据库后，另一个进程还能完整读取和导出吗？重复导入同一主键时，旧联系人和无关数据会不会被改变？本包通过真实 sqlite-utils CLI、完整 JSON 比较和独立只读 SQLite 观察回答这些问题。

这是固定上游版本的 pytest 验收包，不是新的通用运行时。正常业务有 5 项验收；进程生命周期有 11 项、导入前身份检查有 3 项标准库回归。它不需要安装 Skill，也不调用模型或外部服务。

## 放到真实项目中使用

实测上游是 [simonw/sqlite-utils](https://github.com/simonw/sqlite-utils/tree/85b1be10c81d9dd3567e36faf8dd411e4a8789bd)，提交 `85b1be10c81d9dd3567e36faf8dd411e4a8789bd`。本仓库不复制或分发上游源码。

1. 准备该提交的独立源码工作副本。确认 `sqlite_utils/cli.py` 与 `pyproject.toml` 存在，不使用业务数据库。
2. 将本目录的 `acceptance/` 和 `ONBOARDING-REQUIREMENTS.md` 复制到该源码根目录。若同名路径已经存在，先比较并备份，不直接覆盖。
3. 使用隔离 Python 环境准备该项目依赖和 pytest。实测 Python 3.14.4、sqlite-utils 4.2.1、pytest 9.1.1。依赖环境由评估协调者预先准备，尚未验证陌生用户从零安装；本包不自动安装依赖。
4. 在该源码根目录运行：

```sh
.venv/bin/python -B acceptance/run.py
```

将 `.venv/bin/python` 换成实际隔离解释器。入口先用发行元数据检查应用插件，再导入并确认当前副本源码；有插件或元数据错误会在导入前停止。执行期间须保持隔离依赖环境不变，这不是对任意 Python 启动代码的沙箱。每次创建新 `artifacts/onboarding-*` 目录，不使用旧数据库、不覆盖旧证据。查看打印目录的 `pytest.stdout.txt`、`termination.json` 及完整导出；退出 0 且 5 项通过才是正常业务预期。

[完整说明](acceptance/README.md)包含证据文件、超时、中断、重跑和清理责任。进程释放与业务通过是两个结论：超时后不能因为进程已停止就认定写入成功或已回滚。未知状态保留证据，不自动重试。

## 本仓库内的生命周期检查

以下只需要 Python 3.10+ 和 POSIX，不需要 sqlite-utils 或 pytest，不运行真实业务流程：

```sh
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_lifecycle.py -v
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_identity.py -v
```

测试使用本次自建的短时合成写入进程，覆盖 TERM/KILL 清理、父进程先退出、启动记录失败、CLI 超时和 UNKNOWN 兜底。此支持代码只管理固定 CLI 的继承进程组；不保证 runner 被 SIGKILL、主机失效或子进程主动脱离会话后的清理。

## 证据边界

原生 Agent 从不含预制验收脚本的公开源码生成了最初的包，另外两个新执行者分别完成无 Skill 重跑和字段维护。随后审查发现原包会在 pytest 超时后遗留写入者；本目录包含经过同反例验证的修正，不把生成时的正常通过当作故障安全证明。

见[本轮记录](../../evals/results/2026-09-08-native-followup/README.md)。这些是独立 Agent，不是外部人类用户；使用了预备依赖和合成需求，也没有证明比不用 Skill 更省时间。完整源码、依赖和运行产物并不随本包发布。

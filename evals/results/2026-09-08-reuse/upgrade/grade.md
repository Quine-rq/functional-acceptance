# 升级保护独立验收

结论：**发现 1 个可复现的实质漏检，当前验收不通过。** 18 项已有本地集成测试全部通过，但执行权限变化存在假绿。

## P2：所有者执行位丢失仍被报告为 unmodified

位置：`integration/review-update.mjs:43-44`。

工具把执行权限记录成 `Boolean(opened.mode & 0o111)`，只区分“是否任意一位可以执行”。这会丢失所有者、组、其他人的差异。

在本次独立构造的合成包中，三份 `SKILL.md`、`probe.sh` 字节完全相同，基线和候选 `probe.sh` 为 `0755`，安装副本为 `0655`。移除所有者执行位后：

- 基线脚本直接执行：退出码 `0`。
- 安装副本直接执行：`EACCES`，无退出码。
- 比较工具：退出码 `0`，`status: unmodified`，`local_changes` 的 added/removed/changed 均为空。

脚本字节 SHA256：`306c6ca7407560340797866e077e053627ad409277d1b9da58106fce4cf717cb`。

复现目录保留在 `work/reuse-upgrade-review/permission-baseline`、`permission-installed`、`permission-candidate`。在任务根目录执行：

```sh
node outputs/functional-acceptance/integration/review-update.mjs work/reuse-upgrade-review/permission-baseline work/reuse-upgrade-review/permission-installed work/reuse-upgrade-review/permission-candidate
```

当前应当检测到权限变化，但返回未修改。建议至少保存精确的 `mode & 0o111`；如果要承诺所有 POSIX 权限，则另行明确并保存相应完整权限位。补测必须包含 `0755 → 0655` 这种仍有其他执行位、但所有者真实执行能力已经改变的场景。现有 `test-upgrade.mjs:68` 只在 `0644` 与 `0755` 之间切换，无法揭示此问题。

## 实际执行与其余证据

执行 Node `v22.22.3`、本地缓存的 `skills 1.5.24`，命令为：

```sh
TMPDIR=<TASK_ROOT>/work/reuse-upgrade-review/tmp NODE_DISABLE_COMPILE_CACHE=1 npm --offline --prefix outputs/functional-acceptance/integration test
```

结果：18 tests，18 pass，0 fail，0 skipped，测试进程报告总耗时 4595.75 ms。未启动外部 Codex、Claude 或其他模型；安装器中的主机名称只选择本地安装目录。测试临时目录由现有测试自动清理，独立权限反例保留。

- **只读比较成立。** 完整读取工具代码，文件系统调用均为只读；另外核对合成基线/安装/候选三份输入，前后内容 SHA256 和 mode 完全相同。
- **一般改动检测成立。** 已有测试真实断言新增本地文件、删除既有文件、候选指令变化、空目录和 `__proto__`/`constructor`/`toString` 文件名，均通过。权限检测的例外见上。
- **坏路径保持未验证。** 缺失路径的独立 CLI 检查返回 1、空 stdout、`status: unverified`/`ENOENT`；参数不足返回 1。已有链接、缺 SKILL.md、超大文件、条目上限测试实际抛错并通过。
- **SIGKILL 确实发生。** 读过 pinned installer 的 `cleanAndCreateDirectory` 和 `copyDirectory`：先删目标，再并发复制文件。测试调用真实 `skills/bin/cli.mjs`，注入 hook 仅匹配已知合成目标下的子路径；SKILL.md 原生复制完写入唯一标记，再对自身 PID 发 SIGKILL。`test-upgrade.mjs:36-39` 同时断言无 spawn 错误、终止信号 SIGKILL、真实复制标记。两种目录布局的直接重装与暂存共 4 次中断场景均通过。
- **暂存失败未动 live。** 两种布局均在独立 staging project 中中断；实测 live 的 inventory 前后相同。
- **备份和回滚保住旧字节。** 直接重装反例先保存含 local-only.txt 的备份，确认中断后该文件丢失且包不完整，再恢复并逐项核对 inventory；替换/回滚测试使用含不同旧指令字节的基线和 live，检查候选差异、备份字节、回滚后的旧字节以及 unrelated.txt 均保留。
- **没有夸大承诺。** UPGRADING.md 明确两次 move 非原子交换、不提供 lock 合并、未证明 host reload、并发或掉电安全；这些限制与测试覆盖相符。

按此次 9 项独立义务计：8 项通过、1 项失败。这是该限定验收的评分，不是产品成熟度或发布通过率。

## 被评审代码身份

- review-update.mjs：`8e36fec5a676efb2641f5c78a43af8598409aa70c1fb27b62f510adb96ae1db2`
- test-upgrade.mjs：`1a432a65fbeb724db8922d6648d77f108944b2472dd7db78211182790ca7cb16`
- fixtures/interrupt-copy.mjs：`47cb1aae69c21fefb563150a0c1b0c436d7b8a05c3eb219ea6e9ee2de9ff10a7`
- UPGRADING.md：`7fce4efa5ecbdf86176eee50c9a37a066f5c78a785aca2423412920b9218e32a`

评审只写入当前 work/reuse-upgrade-review 下的合成反例与本报告；未修改产品仓库、未提交或推送。

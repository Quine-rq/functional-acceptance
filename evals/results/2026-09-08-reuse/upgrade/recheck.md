# 原始权限反例修正后的独立复验

结论：**当前改动已通过本轮限定验收，原先发现的权限假绿在同一份保留反例上消失。** 原始 `grade.md` / `grade.json` 及反例均未改写；本次不覆盖第一次失败记录。

未重建反例、未 chmod、未修改输入。基线/安装/候选仍为 `0755 / 0655 / 0755`；三份 probe.sh 的 SHA256 都仍是 `306c6ca7407560340797866e077e053627ad409277d1b9da58106fce4cf717cb`，三份 SKILL.md 的 SHA256 都仍是 `c4d2e215bb1c022552e99dae3b283009ca7d85a36e9a65c824df811c50966e9e`，mode 为 `0644`。执行前后的内容摘要与权限完全相同。

同一条 reviewer 命令的新结果：退出码 **2**，`status: local-changes`，`local_changes.changed: ["probe.sh"]`，无新增/删除项；候选相对基线仍无差异。记录的 execute_bits 分别为十进制 `73 / 9 / 73`（八进制 `0111 / 0011 / 0111`）。直接执行行为没有被改变：基线仍返回 `0`，安装副本仍是 `EACCES`。因此变化来自工具检测能力，而非比较条件被修正。

重新完整读取当前工具与升级测试。当前 `review-update.mjs:44` 保留精确 `opened.mode & 0o111`，新增测试也检查实际执行成功→EACCES，再断言 local-changes 和精确 changed 列表。独立重新运行升级相关的全部 9 项测试：**9 pass，0 fail，0 skipped**，报告总耗时 **2913.546042 ms**。

命令：

```sh
TMPDIR=<TASK_ROOT>/work/reuse-upgrade-review/tmp NODE_DISABLE_COMPILE_CACHE=1 node --test outputs/functional-acceptance/integration/test-upgrade.mjs
```

其余原义务复核：

- 三份比较输入内容及模式不变；读取缺失路径仍返回 1 / unverified / ENOENT。
- 一般新增、删除、候选内容变化，空目录与 prototype 文件名检查仍通过。
- 坏包的链接、缺入口、超大文件、过量条目仍被拒绝。
- 两种布局的真实安装器 SIGKILL 共 4 场景仍通过，包括信号和已复制入口标记；仍仅作用于测试新建的精确合成目录。
- 暂存失败后 live 未变；备份恢复、旧字节回滚、无关文件保护均通过。
- fault hook 与 UPGRADING.md 的 SHA256 和首次评分一致；此前明确的非原子交换、无自动 lock 合并、非 host reload 证明等边界保持不变。

本轮 9 项验收义务全部通过。范围仍只是可信、静止、本地普通目录及文档承诺的文件内容和执行位；不新增对其他权限位、并发、掉电、远端下载、宿主重载或生产发布的保证。

## 当前源身份与历史保留

- review-update.mjs：`6c1647218d7739e614b5d01b4a0d10ff1a8db0485fabaf5a800604a1cdcbd737`
- test-upgrade.mjs：`e3230932f7a117d5b1962481858d5a72ebc0bf970f1fddfe9b48418e627ec5f8`
- fixtures/interrupt-copy.mjs：`47cb1aae69c21fefb563150a0c1b0c436d7b8a05c3eb219ea6e9ee2de9ff10a7`
- UPGRADING.md：`7fce4efa5ecbdf86176eee50c9a37a066f5c78a785aca2423412920b9218e32a`
- 原 grade.md：`b094c6f2cb510cc913b0e5b237aeac9cd04ba04c0016a58aca80a06472f30ba3`
- 原 grade.json：`15c5d427f652b27701b6ff370f2401c5d7113ee4b9eda53a81ecc6b848de39df`

评审未修改产品仓库、原报告或原反例，未调用任何外部模型，未提交或推送。

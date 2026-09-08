# 明确标记的诊断复验

本轮是新候选的独立代理诊断复验，不替换此前四次验收记录，不是人工用户证明。expired-session 单次通过后，按授权各执行一次此前未执行的 lost-response、unicode-notes；最后一场再次出现超时，已停止，没有重跑或修改产品源码。

| 场景 | 实际结果 | 耗时 | run_dir |
| --- | --- | --- | --- |
| expired-session | PASS / 0 | 29,657 ms | run-20260908T062102428303Z |
| lost-response | PASS / 0 | 28,607 ms | run-20260908T062141545322Z |
| unicode-notes | UNVERIFIED / 2 | 32,945 ms | run-20260908T062225292764Z |

目录均位于 `.acceptance-study/artifacts/`。`diagnostic-recheck.json` 单独保留 expired-session 复验；`diagnostic-results.json` 保留三次完整原始 result 和独立观察，目录字段继续使用 `run_dir`。各场 stdout/stderr 单独存于权限 0700 的 `.handoff-diagnostic/`，日志权限为 0600。旧 `final-results.json`、`final-summary.json`、`final-candidate-report.md` 的 SHA-256 从执行前到执行后均不变。

## 精确异常位置与安全调用轨迹

unicode-notes 保持 `harness-or-observation / UNVERIFIED / partial`，不是业务 FAIL。阶段为 `delete with unrelated control`，最后原生步骤是 `target.confirm_click`，bookmark_id=14。

本轮 owner-only 的 `obstacle.private.txt` 已读取并局部复核，文件权限确为 0600。以下摘录不含凭据：

```text
accept.py:334  confirm_delete(target_id, 'target')
accept.py:212  confirmation.click()
playwright._impl._errors.TimeoutError: Locator.click: Timeout 7000ms exceeded.
Call log:
  - waiting for locator("ld-confirm-dropdown").get_by_role("button", name="Confirm", exact=True)
```

原生步骤依次为 target.delete_click（06:22:47.354963 UTC）、target.await_confirmation（06:22:47.387061）、target.confirm_click（06:22:47.464787）；没有 target.modal_closed。按已捕获脚本的顺序，可见断言已通过，随后才生成确认截图和进入点击。

独立逐图查看发现：位于可见断言与点击之间生成的 `delete-confirmation.png` 已无 Confirm，`delete-confirmation.txt` 同样不包含 Confirm；超时后的 obstacle.png 仍显示目标详情和 Delete，没有 Confirm。这些证据显示观察到的可见状态未维持到实际点击，但不能仅凭这些证据判断状态变化的原因，也不能证明旧版同类超时具有相同根因。

本次没有触发 120 秒看门狗。expired-session 的单次通过不证明偶发问题已消除；后续 unicode-notes 的确认点击超时也说明完整诊断批次未通过。

## 已验证与未完成的用户结果

expired-session 的会话移除、重新登录和同一对象恢复通过，目标 id 10 与控制 id 11 的四步删除顺序完整，最终只保留旧 id 5、id 9。lost-response 的真实 POST 完成后响应被丢弃，恢复前数据库只存在一条本场目标记录，随后恢复同一对象而未重新提交；目标 id 12、控制 id 13 清理完毕，旧基线保持一致。

unicode-notes 的中文、双引号、emoji 和换行在保存、全新浏览器读取、服务器重启后读取、另一账户攻击后和编辑持久化时，均由真实 UI 字段与独立数据库观察精确核对通过。重启截图可见这些字符；最终只读查询也确认 id 14 中编辑后的完整笔记仍精确一致。这是笔记保留的证据，不能替代尚未完成的删除和整场验收。

当前书签 IDs 为 [5,9,14,15]。额外逐字段查询确认旧 id 5、id 9 完全未变；新增残留为本场 target id 14 与 control id 15，没有手工清理。`data_cleanup` 正确单独报告 `not-completed-or-unobserved`。

独立记录器有一处标签不够准确：`old_id5_and_id9_full_rows_preserved` 实际比较的是“当前整个数据集等于基线”，因此出现新增残留时为 false；它并不证明旧行被改写。此标签及原记录未被悄悄重写，补充核查在 `diagnostic-review.json` 明确区分 `prior_rows_exactly_unchanged=true` 与 `entire_dataset_restored=false`。

## 运行身份与收尾

三场使用相同诊断候选；执行前后脚本、环境、依赖锁和资源摘要均一致，产品受跟踪源码无改动。原生脚本快照和环境回执与独立摘要一致，应用从捕获的 server.py 启动。DEBUG 404 的省略事件仍存在，对应 PNG/TXT 均未生成。

三场 execution_cleanup 均为 stopped，日志排空无错误或截断，浏览器 start/close 成对。最终由 lsof 复核 18741/18742 无监听，由只读 ps 复核异常场景记录的 85746、85747、85789 均不存在。没有手工终止未知进程、删除旧对象、触发看门狗或覆盖既有结果。

诊断维护的实际价值是把这次超时从笼统阶段收窄到具体 Confirm 定位器，并独立显示数据清理未完成；它尚未使完整流程稳定通过。原验收失败和本轮诊断失败均继续保留。

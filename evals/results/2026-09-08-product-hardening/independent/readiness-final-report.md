# 导航等待候选：独立最终矩阵

当前候选六场顺序各执行一次，实际退出码为 **0, 1, 2, 0, 0, 0**，全部符合事先冻结的预期；不把它们统称为业务 PASS。每场上限 120 秒，无超时、重试、运行中纠正或源码修改。

| 场景 | 真实判定 / code | 耗时 ms | target / control | 本场对象处理 | run_dir |
| --- | --- | ---: | --- | --- | --- |
| healthy | PASS / 0 | 16350 | 16 / 17 | 定点清理完成 | run-20260908T064933595747Z |
| note-loss | FAIL / 1 | 4685 | 18 / 无 | id18 反例保留 | run-20260908T065001070681Z |
| missing-observation | UNVERIFIED / 2 | 16960 | 19 / 20 | 定点清理完成 | run-20260908T065021106437Z |
| expired-session | PASS / 0 | 18182 | 21 / 22 | 定点清理完成 | run-20260908T065050840688Z |
| lost-response | PASS / 0 | 18673 | 23 / 24 | 定点清理完成 | run-20260908T065127721172Z |
| unicode-notes | PASS / 0 | 17380 | 25 / 26 | 定点清理完成 | run-20260908T065156014250Z |

## 先行的机制对照与改动影响

本次作者提供的候选只在 native 执行器 details View 点击外增加实际 `support.turbo_visit_completed(page, href)`，匹配真实 `turbo:load detail.url`；并新增 `details.navigation_completed` 事件。没有修改 upstream linkding 产品源码。

独立复用原精确 rAF150ms 探针；`observe.js` 经 cmp 与原 3 红完全一致，调用点仍为固定 bundle `19:11228`、回调 `()=>e()`。只在 View 外调用实际 helper，未增加任意 sleep 或伪造事件。新 3 轮全部命中注入，真实 before-cache / details load 先于 Delete；Confirm 在原 450 ms 窗口内保持可见，均 Cancel 退出。原 3 红和此前所有 misses/自然失败均未改。

第 1 轮相对 frame-load：before-cache +167.8 ms → details load +169.0 → helper 返回 +186.2 → Delete +191.7 → dropdown 添加 +219.7 → Confirm 可见 +239.5。新对照采集 7402 ms、外层 8170 ms，原始事件和完整执行身份位于 `.raf-render-wait-recheck/`。

这支持“当前 native 执行器在该受控调度窗口下等待正确导航边界”的结论，不证明旧两次自然超时必然由该机制导致，也不声明产品早点击 UX 已修复或偶发问题永久消除。

## 独立证据核对

每场 initial 数据库与启动前独立观察相等。新驱动明确区分：

- `prior_rows_exactly_unchanged`：原有书签全部数据库列、完整 bookmark-tag 关联行逐字段不变；六场全部为 true，业务 notes/tags 等另与 native 观察逐项核对。
- `owned_run_bookmarks_removed`：只检查本场 target/control；除按预期保留反例的 note-loss 为 false 外，其余为 true。

起始旧 IDs [5,9,14,15] 保留；note-loss 新增并保留 id18，后四场将它纳入各自基线，最终为 [5,9,14,15,18]。没有手工清理旧失败或旧 control。unused tags、会话、合成账号和证据可按 pack 契约保留。

- note-loss：真实 UI 观察到 notes 为空，独立数据库确认仅留下本场一个 id18；这是明确 runtime mutation 的反例，不是新发现的 upstream 缺陷。
- missing-observation：明确记录 `observation_withheld`，重启后数据库义务仍 UNVERIFIED；不能用其它 UI 成功或最终清理替代该缺口。
- expired-session：清除浏览器会话后真实登录页出现，正常登录恢复同一 id21，没有另建对象。
- lost-response：真实 POST 已完成、302 响应被丢弃；重试前独立观察唯一已存对象 id23，并恢复而不重复提交。
- unicode-notes：中文、双引号、🧭、换行，在 save / fresh browser / restart / owner-after-attack / edit 五处的实际 UI 字段与独立数据库精确一致；编辑时只追加约定行。最终 id25/id26 清理完成。已直接查看本场 edit_persisted 截图及 healthy 的实际 Confirm 截图，不靠退出码代替 UI 证据。
- 五个到达权限阶段的场景均记录两条敏感页面证据省略；所有六场 `bob-edit-denied`、`bob-write-denied` 的 PNG/TXT 均确实不存在。note-loss 未到达该阶段，不声称它执行了权限检查。

## 执行身份、隐私及清理

固定 upstream HEAD：`65813a75404b1319aca8b09700fadc0b15adabaf`，tracked diff 为空。六场的执行脚本、完整 pack、环境/静态资源身份一致；每场 captured script / native-pack / pack-identity / environment-identity 与本场启动前值相同，批次结束再次核对不变。

候选 accept.py SHA-256：`84a4b4fa488c4b9fad2e5148770e12e392110a9b2834ff08f443b5c12d8a3d26`。
候选 support.py SHA-256：`493cd346337bf278880c83026bc4f4eba781a5878578f510cbdf3389d837a4f9`。
完整身份见 `readiness-final-results.json` 及 `readiness-final-review.json`。

所有自有服务最终退出；逐场以及批次末的记录 PID 检查无存活，浏览器 started/closed 成对（26/26）。18741/18742 已释放，最后独立 lsof 空输出、退出码 1。所有 private stdout/stderr 分场保留且不公开；无日志截断或排空错误。已对六个新 run 的 170 个非 private 文件做已知测试凭据扫描，未命中；这不是任意日志/数据的通用安全认证。

旧 final-results、final-summary、final-candidate-report、diagnostic-results 和 diagnostic-recheck 的哈希全部保持。独立驱动与 audit 只写本隔离目录；无 stage、commit、push。探针未点击 Confirm、登录后未发送书签业务写请求；完整矩阵则按授权真实保存/编辑/定点删除本场对象。正常登录会创建/更新会话，绝不声称全程零写入。

## 交接与边界

`readiness-final-results.json` 每项含 scenario、code、elapsed_ms、**run_dir** 与原生 result 正文；原生 result.run 的大小写与目录名不同，请按 run_dir 定位。独立字段/精确 Unicode 摘要/隐私与进程核对见 `readiness-final-review.json`；执行器为 `readiness-final-handoff-runner.py`，分场记录及审计代码位于 `.handoff-readiness-final/`。此处 stdout/stderr 均 owner-only，父任务脱敏导出时不要包含 private 文件、数据库或原始截图。

此轮按作者明确给出的候选和受控时序条件执行，是带作者指导的诊断后独立复验；没有读作者案例产物。复验中无需额外业务决策或运行修正。diagnosing-bugs 用于保留原红和新对照、核对失败与清理；浏览器遵循明确隔离约束，不使用日常用户 Chrome profile。

这是代理交接证据，不是人工用户证据。当前 macOS / Python 3.14 / 固定 Chrome 和依赖组合的一次完整矩阵，不覆盖其它平台、所有网络故障或全部并发时序。无全量“可上线”或“消除偶发问题”的推断。


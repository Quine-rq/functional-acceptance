# 最终候选独立交接结果

本次是独立代理执行证据，不是人工用户验收证明。只阅读更新后的 examples/linkding/README.md 和其原生脚本，没有读取作者案例产物。按授权复用已经准备的隔离克隆，逐场执行一次；在 expired-session 出现非预期结果后立即停止，没有执行剩余场景、重跑、修订测试包或改动产品源码。

## 实际结果

| 场景 | 文档预期 | 实际 | 耗时 | 是否符合预期 |
| --- | --- | --- | --- | --- |
| healthy | PASS / 0 | PASS / 0 | 32,249 ms | 是 |
| note-loss | FAIL / 1 | FAIL / 1 | 5,714 ms | 是 |
| missing-observation | UNVERIFIED / 2 | UNVERIFIED / 2 | 50,795 ms | 是 |
| expired-session | PASS / 0 | UNVERIFIED / 2 | 90,329 ms | 否；清理控制对象时观察超时 |
| lost-response | PASS / 0 | 未执行 | — | 按遇异常停止规则保留 |
| unicode-notes | PASS / 0 | 未执行 | — | 按遇异常停止规则保留 |

每场 stdout/stderr 分开以 0600 权限保存到 `.handoff-final/<scenario>.stdout.private.txt` 和 `.handoff-final/<scenario>.stderr.private.txt`；目录权限 0700。每场有独立事件、运行目录、脚本快照和回执。记录器使用 115 秒发出停止请求、120 秒截止的看门狗；本次没有触发看门狗，也未人工终止任何场景。所有原始产物继续保留，不作覆盖。

`final-results.json` 保留四项真实执行记录，每项含 `scenario`、`code`、`elapsed_ms`、`run_dir` 和完整原始 `result` 正文，以及独立核查结果。**实际目录字段是 `run_dir`**；`result.run` 是小写业务标识，不能直接当大小写敏感的目录路径。两个未执行场景在 `final-summary.json` 单独列出，没有伪造 result。

| 场景 | 实际目录名（位于 .acceptance-study/artifacts/） |
| --- | --- |
| healthy | run-20260908T061206476263Z |
| note-loss | run-20260908T061251551005Z |
| missing-observation | run-20260908T061315674040Z |
| expired-session | run-20260908T061415262120Z |

## expired-session 的证据与缺口

异常阶段为 `cleanup control through UI`，错误类型 `TimeoutError`，原生分类保持 `harness-or-observation`，业务结论保持 `UNVERIFIED / partial`，不能改写为业务 FAIL。

会话 Cookie 移除、要求登录、重新登录、恢复同一对象 id 8 均有界面和独立数据库通过证据。之后的跨账号隔离、原对象未被改写、编辑持久化、目标 id 8 的定向删除、控制对象 id 9 保持完整，也都通过。失败发生在最后清理控制对象的阶段。

`obstacle.png` 和 `obstacle.txt` 显示 id 9 的详情弹窗已打开，Delete 可见，Confirm 未显示。当前脚本把打开详情、点击 Delete、点击 Confirm 放在同一阶段，异常记录只保留 TimeoutError 和通用提示，未保存具体失败 locator、Playwright 调用栈或逐动作轨迹。因此证据只能证明控制对象清理未完成，不能确认究竟是哪次调用超时，更不能仅凭截图断言产品缺陷或特定竞态根因。原生 runner 的 stderr 为 0 字节；应用日志没有 Traceback / Internal Server Error 标记，不能补齐客户端定位器缺口。

超时发生在 06:15:36 UTC，最终完成进程收尾并发布回执于 06:15:45 UTC。90.329 秒内结束，未触发外部看门狗。

## 对象与基线

healthy 开始和结束均无书签。note-loss 明确暴露笔记被运行时故障清空，只留下失败对象 id 5。missing-observation 虽然缺失指定的重启后数据库观察，其余流程仍结束，id 5 的全部已观察字段保持不变。expired-session 开始时同样保留 id 5，结束时它未被改写；当前还留有本场尚未清理的 control id 9，总计两条书签。目标 id 8 已删。

这些结论来自每场执行前后的独立只读 SQLite 查询与事件内对象快照的逐字段比较，不只依赖原生 PASS 标签。凭据和完整数据库内容没有输出或发布。没有清空数据库、删掉失败证据或手工删除 control id 9。

## 维护改动的实际影响

DEBUG 404 过滤变化已在走到权限检查的 healthy、missing-observation、expired-session 三场直接观察：均记录了 `bob-edit-denied` / `bob-write-denied` 的省略事件，且对应四个 PNG/TXT 文件确实不存在。授权校验仍保留状态码和对象未变化证据。note-loss 提前结束，未走到这些页面；它不提供额外过滤证明。其他产物仍不能自动认定安全可公开。

四场均独立比对了执行前后脚本、环境、依赖锁和资源摘要；跨场候选输入一致，受跟踪产品源码未改动，原生 `native-pack/` 快照与启动脚本一致，应用服务实际从捕获的 server.py 启动。此次候选 accept.py SHA-256 为 `b4c13e3eadf58365186184ea742d77a796a883b2bc30851d6c275187b64605e2`，support.py 为 `f4e91d32aa437e45b8ff8ccfbfbe775c8ca6c6008ddfc36f845bc933dc9e629c`。详细指纹在各原始回执和 final-results.json 中。

unicode-notes 尚未执行，因此不能报告中文、引号、emoji 与换行已精确保留。信号标记的实现已阅读，但本次授权场景没有注入 SIGTERM/SIGINT，不能据此宣称独立验证了中断恢复修复。上述未验证项没有借用作者测试结果补齐。

## 进程与执行纪律

每场独立核查记录的服务进程已退出、两端口空闲、浏览器 start/close 数量相等，原生 execution_cleanup 均为 stopped。四场共记录 16 次新沙箱浏览器启动和 16 次关闭。服务日志没有 drain 错误或截断。异常场景的 83222、83223、83286 还由只读 ps 复核为不存在；lsof 核对 18741/18742 无监听。浏览器 PID/profile 未由原生报告公布，因此这不应扩展成对所有浏览器后代的独立 OS 级身份担保。

执行命令为每场一次 `.venv/bin/python final-handoff-runner.py <scenario>`，其实际原生 argv 完整保存在每项 `command`。记录器仅负责独立日志、时限、身份/数据/清理核查与汇总，不导入或改变原生测试包。没有 commit、push、源码修正、自动重跑或读取作者产物。

当前最终候选的独立验收未通过完整六场要求；应保留本次真实失败和未执行项，补齐观察定位能力及该清理路径的证据后，才另行决定新的候选验收。

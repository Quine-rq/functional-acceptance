验收被环境阻断，**全部 11 项功能检查仍为 UNVERIFIED**，不能判定 linkding 通过或失败。

启动文章服务时，绑定 `127.0.0.1:18742` 返回 `PermissionError: Operation not permitted`。一次诊断确认后停止；未启动应用或浏览器、未写入业务数据，所有已启动进程均已退出。

已保留：

- [验收报告与重跑说明](.acceptance-study/artifacts/README.md)
- [原生 Playwright 回归](.acceptance-study/artifacts/acceptance_regression.py)——仅通过语法检查，浏览器流程尚未验证。
- 首次尝试、诊断和进程退出证据，均在报告中索引。

需在允许两个指定 loopback 端口监听的环境中重跑；当前策略禁止提权。
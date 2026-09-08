# 精确 rAF 调度注入：3 轮受控红信号

这是独立代理交接证据，不是人工用户验收。只证明固定版本在受控调度下的机制；不把原有两次自然超时归因于此，也不声明产品或早点击 UX 已修复。

执行：`.venv/bin/python .raf-render-callsite-injection/probe.py`。3 轮各执行一次，无失败重试；退出码 0 是采集完成，不是业务 PASS。外层 7047 ms、采集 6285 ms，低于 60 s 上限。

## 注入边界

启动前校验实际 bundle SHA-256，锁定唯一 Visit.render 内 rAF 调用位置 `/static/bundle.js:19:11228`。登记堆栈按 loopback URL 解析并去 query；只匹配源位置及 `()=>e()` 回调。每轮第一个进度条 rAF 原样透传，目标回调延迟 150 ms 一次。每轮都有 match、原始回调到期、delivered 及 RAF/cancel 恢复 receipt。没有 dispatch 假事件或阻止 Turbo/cache 事件，也没有修改应用文件或后端。

## 真实事件顺序

下表以每轮真实 details frame-load 为 0，单位 ms。完整 epoch 时间、DOM 状态和安全堆栈保留在原始 JSON。

| 轮次 | dropdown 添加 | Confirm 可见断言 | 延迟回调交付 | before-cache | dropdown 移除 | details turbo:load |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 37.1 | 62.1 | 167.2 | 167.3 | 168.5 | 168.9 |
| 2 | 36.3 | 53.4 | 167.5 | 167.6 | 168.5 | 169.0 |
| 3 | 36.7 | 55.3 | 167.2 | 167.4 | 168.2 | 168.7 |

3 轮 before-cache 的捕获阶段均为 dropdown=1、Confirm 可见；随后真实 DOM 移除，事件后的状态变成 dropdown=0、Confirm 不存在。移除发生在退出动作之前，最终用 Escape 退出。frame 已 complete 且不 busy 仍早于这段缓存时序；本轮没有测试新的导航完成等待。

## 数据、文件和进程

未发送书签业务写请求、未点击 Confirm，书签基线 [5,9,14,15] 逐字段不变。写请求保护安装在正常登录之后，登录本身可能创建或更新会话，不作“零写入”宣称。

执行脚本、应用源码、环境 identity 及旧 final-results 均一致。之前的自然观察、ready 单轮、错误 rAF 目标的 3 次 misses 全部保留。

自有服务 PID 93178/93179 都已退出（-15）；独立 OS ps 查无此 PID，lsof 查 18741/18742 无监听，二者均空输出、退出码 1。无错误、无 watchdog 触发。

安全导出：`result.json`、三轮 JSON、`summary.json`、`report.md`、`probe.py`、`observe.js`。不导出 private 日志、数据库或截图。诊断技能仅用于保留红信号、边界和清理证据；受本次授权限制，不进入修复或更多循环。


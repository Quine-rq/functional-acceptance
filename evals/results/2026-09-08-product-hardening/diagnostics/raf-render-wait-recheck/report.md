# 导航完成等待：同一精确探针对照

调用实际 `support.turbo_visit_completed` 包住 View.click；`observe.js` 与原 3 红版本经 cmp 完全一致。目标 callback/callsite、150 ms 注入和 450 ms DOM 观察窗口不变，没有伪造事件或新加等待延迟。

3 轮均命中，真实 before-cache 与匹配 details turbo:load 均先于 helper 返回及 Delete。Confirm 此后可见，整个观察窗口未被移除，均以 Cancel 退出。采集 7402 ms、外层 8170 ms。完整候选身份保留在 result.json。

| 轮次 | before-cache | details load | helper 返回 | Delete 开始 | dropdown 添加 | Confirm 可见 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 167.8 | 169.0 | 186.2 | 191.7 | 219.7 | 239.5 |
| 2 | 168.3 | 169.2 | 186.1 | 191.8 | 220.0 | 242.2 |
| 3 | 168.4 | 169.9 | 186.9 | 193.4 | 220.5 | 243.3 |

时间相对各轮 frame-load，单位 ms。旧业务字段与 tags 逐字段不变 [5,9,14,15]；未点击 Confirm、登录后无书签业务写请求。正常登录可更新会话，不声称零写入。脚本/应用/环境 identity 一致，旧 final-results 未改。自有服务 PID 94367/94368 退出且 OS 核查不存在，两端口空闲。

这是独立代理的受控机制对照；原 3 红及自然失败全部保留，不证明原两个自然超时已被归因或偶发问题永久消除。


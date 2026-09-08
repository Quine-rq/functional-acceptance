# readiness-contract-probe：单轮只读观察

本轮独立记录，不覆盖之前十轮观察或验收/诊断记录。只对已有合成书签 id 14 执行 View → Delete → 观察 → Cancel；没有点击 Confirm、没有发出书签写请求，没有修改产品或测试包。

采集耗时 4.622 秒，外部包装进程总耗时 5.310 秒，无错误或看门狗触发。完整事件、状态和退出信息在 result.json；逐轮记录为 readiness-contract-1.json，精简时序在 summary.json。

以下以详情 frame 的 `turbo:frame-load` 分发时刻为 0（epoch 毫秒 1788849152560.9001）：

| 相对时间 | 实际事件或 DOM 事实 |
| --- | --- |
| −2.3 ms | modal.visible；URL 已为 /bookmarks?details=14，frame complete 属性尚不存在 |
| −1.0 ms | 调用 Delete 点击开始 |
| 0.0 ms | turbo:frame-render 和 turbo:frame-load；complete 属性存在，frame busy=false |
| +0.4 ms | turbo:before-visit；detail.url=/bookmarks?details=14，随后 document aria-busy=true |
| +15.8 ms | turbo:before-cache；dropdown 数量仍为 0 |
| +16.7 ms | turbo:render，随后该详情 URL 的 turbo:load；document aria-busy=false |
| +38.6 ms | MutationObserver 记录 dropdown.added，数量变为 1 |
| +52.7 ms | Delete 点击调用返回，Confirm 已实际可见 |
| +515.5 ms | 观察窗口结束，开始 Cancel 退出；Confirm 仍可见 |
| +538.5 ms | Cancel 后记录 dropdown.removed，数量归零 |

事件分发前后均记录了 URL 的 loopback 安全路径、frame complete/busy、document preview/aria-busy；未采集凭据或输入值。完整对象内保留 after-dispatch 状态，不依赖上表四舍五入后的时间判断。

本轮直接证明：详情 URL 和 frame 完成可以早于后续页面访问的缓存/渲染/加载收尾；URL 匹配或 complete 属性不能单独代表这些后续事件已经发生。匹配 /bookmarks?details=14 的最后一次 turbo:load 在 before-cache 之后、dropdown 创建之前。该轮 Confirm 保留到 Cancel，未观察到 before-cache 移除已存在的 dropdown。

这是一条真实导航时序证据，不是原超时根因的证明。本轮没有试验 `await frame.loaded` 或任何新增等待修正，不能据此声称修正有效或偶发问题消失。

收尾独立核查：书签 ids [5,9,14,15] 的全部字段未变；没有 Confirm 点击或登录后的写请求；源码/环境及旧 final-results.json 摘要未变。两个自有服务 90118、90119 已终止，18741/18742 无监听。所有新代码和采集仅位于本目录，之前十轮目录未改写。

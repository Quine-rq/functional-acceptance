# Runtime scheduling injection — 指定阶段未验证

本轮严格按固定方案执行三次：在目标 id 14 的 turbo:frame-load 后，将下一次真实 window.requestAnimationFrame 回调延迟 150 ms；调度接口在登记后立即恢复，并为该单个回调保留取消语义。没有伪造、阻止或手动派发 Turbo/cache 事件，没有修改产品文件或后端。

结果应记为 **INCONCLUSIVE / 指定阶段未验证**。三次真正被延迟的回调体均为：

```js
()=>{this.progressElement.style.width=10+90*this.value+"%"}
```

该回调体对应固定版本 Turbo 的 `ProgressBar.refresh`，不是 `Visit.render` 的 Promise resolve 回调。真实 before-cache 与匹配详情 URL 的 turbo:load 仍在被延迟回调交付前发生。因此不能把本轮没有红信号解释为导航等待有效、偶发问题消失或原根因已证实。没有换注入点、增加循环或重跑。

| 轮次 | 实际回调延迟 | before-cache | 详情 turbo:load | dropdown 添加 | Confirm 观察可见 | 被延迟回调交付 |
| --- | --- | --- | --- | --- | --- | --- |
+| 1 | 150.3 ms | +15.1 ms | +16 ms | +36.1 ms | +56.4 ms | +165.2 ms |
| 2 | 150.3 ms | +16.8 ms | +17.6 ms | +38.6 ms | +63.2 ms | +166.9 ms |
| 3 | 150.9 ms | +16.6 ms | +17.5 ms | +43.6 ms | +68 ms | +167.4 ms |

除“实际回调延迟”外，各时间均相对本轮目标 frame-load。三轮 Confirm 均真实出现，并保持到最后 Cancel；没有出现“Confirm 已存在 → before-cache → dropdown 消失”的目标红信号。原始三轮及注入 receipt 完整保留在 result.json 和 scheduling-injection-1/2/3.json。

每轮 receipt 均证明 requestAnimationFrame 已恢复，交付时配套 cancelAnimationFrame 也已恢复。调用栈的 bundle URL 过滤未保留任何 frame；回调归属依据是记录的真实 callback_source 与固定源码内容比对，不能伪称保存了有效调用栈。完整源码 SHA-256 在 result.json/summary.json，包括 bundle、Turbo ESM 和 confirm-dropdown.js。

总采集 7.221 秒，包装进程 8.622 秒，未触发 60 秒看门狗。没有点击 Confirm、没有登录后的写请求，全部旧书签逐字段不变，产品源码/环境及旧 final-results.json 摘要不变。两个自有服务 91711、91712 已退出，18741/18742 无监听；没有手工清理对象或未知进程。

这是明确标注的人为调度注入，不是自然故障复现，也不是人工用户验收证明。本组到此结束，未继续扩大探针范围。

# 原始十轮只读生命周期观察

对已留存 id 14 逐轮从列表打开详情、点击 Delete、只观察 Confirm、以 Cancel/Escape 退出；从未点击 Confirm。十轮全部原样保留，每轮没有重试。采集 13.797 秒，包装总耗时 14.162 秒。

十轮均未复现 Confirm 消失：dropdown 在观察窗口内持续存在，最后只在主动退出时关闭。所有观察到的 before-cache 分发时 dropdown 数量都为 0；不能声称已经观察到该事件移除一个已存在的确认框。因此“定位后比较 frame-complete”的条件未成立，对照组未运行，不能报告该等待方式有效。

第 1 轮的真实顺序为：frame-render/load 和 complete 属性出现于 epoch 1788848916125.0 ms，modal.visible 于 6138.2 ms，delete.begin 于 6139.4 ms，before-cache 于 6142.3 ms，dropdown.added 于 6178.7 ms。同一秒内的后四个简写均以 1788848916000 ms 为基准。该例直接显示 frame-load/complete 早于 before-cache，但 dropdown 创建更晚，故未触发移除。

追加 turbo:before-visit/render/load、URL 和 document 状态的需求到达时本组已结束；没有倒填或重跑。后续另立 readiness-contract-probe 记录该需求，本目录原始十轮文件没有改写。

结果确认全部旧书签字段、源码/环境与旧 final-results 摘要未变，登录后没有写请求，服务进程 87932/87933 已退出，两端口空闲。本轮不证明偶发问题消失，也不证明原故障根因。

**不满足需求：导出提示成功，但最后一页被静默丢弃。**

- 根因：`export.py:130` 无条件执行 `pages[:-1]`，未传 `--fault` 也会漏页。
- 最小已观察反例：直接使用提供的 fixture，预期 5 条，实际只有 4 条；第 3 页唯一记录 `r-005` 完全缺失，但命令退出码为 0。
- 冒烟检查通过（1 项），因为 `test_smoke.py:8–9` 只检查退出码和表头，没有验证“每条记录按顺序完整导出一次”。

实际 CSV 已按 UTF-8 解析逐字段比对：前 4 条顺序、内容完全一致。复用输出路径返回 2，原 CSV 保持不变；所有 supplied 文件哈希均未变化。

保留证据：[实际 CSV](artifacts/export-observed-310ac3c7.csv)、[检查日志及完整差异](artifacts/verification-310ac3c7.json)。未修改应用、测试、需求或 fixture。
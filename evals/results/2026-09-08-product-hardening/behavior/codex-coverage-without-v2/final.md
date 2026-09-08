**未满足需求：导出显示成功，但静默丢失最后一页。**

- 根因：`export.py:130` 无条件执行 `pages[:-1]`，未传 `--fault` 也会漏页。
- 最小反例：直接使用提供的 fixture 正常导出，应有 5 条，实际只有 4 条；第 3 页唯一记录 `r-005`（标题“最后一页”）完全缺失，进程仍返回 0。
- 现有 smoke 检查通过，但只验证退出码和表头，未覆盖“每条记录按顺序完整导出一次”的要求。
- 实际 CSV 为有效 UTF-8；已导出的前 4 条顺序、字段内容均精确保留，包括引号、Unicode 和换行。提供的文件经哈希核对未变更。

证据已保留：[实际 CSV](artifacts/export-review/actual.csv)、[逐条比较结果](artifacts/export-review/comparison.json)、[smoke 日志](artifacts/export-review/smoke.log)、[导出命令及日志](artifacts/export-review/export.log)。

未修改应用、测试、需求或 fixtures；所有写入均在项目内。
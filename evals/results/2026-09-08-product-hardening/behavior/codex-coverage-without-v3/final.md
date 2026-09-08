**未满足要求：导出提示成功，但静默漏掉最后一页。**

- 根因：[export.py:130](<TASK_ROOT>/work/codex-coverage-without-v3/project/export.py:130) 无条件使用 `pages[:-1]`；不传 `--fault` 也会漏数据。
- 最小已验证反例：直接导出提供的 `fixtures/pages.json` 到新文件。进程返回 0，但应有 5 条、实际只有 4 条；第 3 页唯一记录 `r-005` 完全缺失，违反“每条记录导出一次”。
- 现有 smoke 测试通过，因为只检查退出码和表头，没有检查记录完整性。
- 实际 CSV 经 UTF-8 解码、CSV 解析逐字段比较：前四条顺序及内容完全一致，包括引号、Unicode、LF/CRLF。重复使用输出路径返回 2，已有 CSV 未改变；所有提供文件的哈希保持不变。

已保留[实际 CSV](<TASK_ROOT>/work/codex-coverage-without-v3/project/artifacts/export-review-1788847307873563000/actual.csv)、[逐字段比对证据](<TASK_ROOT>/work/codex-coverage-without-v3/project/artifacts/export-review-1788847307873563000/comparison.json)及同目录下的运行日志。未修改应用、测试、需求或 fixtures。
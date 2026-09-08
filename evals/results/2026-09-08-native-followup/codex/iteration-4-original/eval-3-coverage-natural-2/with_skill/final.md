**验收失败：导出提示成功，但漏掉最后一页。**

- **FAIL — 完整性**：原始数据有 5 条，实际 CSV 只有 4 条；缺失 `r-005`（标题“最后一页”）。原因是 `export.py` 默认执行 `selected_pages = pages[:-1]`，无需启用故障参数。
- **PASS — 已导出的记录**：顺序正确、无重复，三个字段逐字一致，含 Unicode、引号和换行；CSV 为有效 UTF-8。
- **PASS — 原有检查**：smoke 通过，但仅验证退出码与表头，未覆盖记录完整性、顺序、字段保真和已有文件保护。
- 本次已有文件哈希均未变化；目标已存在时的拒绝覆盖分支未实测。

最小已验证反例：直接使用提供的 fixture，不修改任何数据：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

输出名须不存在。预期 5 条，实际 4 条，但退出码仍为 0。

保留证据：[实际 CSV](project/artifacts/acceptance-1788853544510248000/actual.csv)、[逐字段核对与哈希](project/artifacts/acceptance-1788853544510248000/observation.json)、[smoke 日志](project/artifacts/acceptance-1788853544510248000/smoke.json)、[导出日志](project/artifacts/acceptance-1788853544510248000/export.json)。

未修改应用、测试、需求或 fixture；进程已结束，无遗留临时文件。
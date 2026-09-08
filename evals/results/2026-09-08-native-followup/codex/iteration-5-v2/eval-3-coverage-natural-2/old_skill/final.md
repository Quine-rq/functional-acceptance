**验收失败：命令提示成功，但最后一页记录丢失。**

- **FAIL — 完整导出：** 提供的 fixture 有 5 条记录，实际 CSV 仅有 4 条，缺少第 3 页的 `r-005`（标题“最后一页”）。`export.py` 无条件执行 `selected_pages = pages[:-1]`，默认运行就会漏掉末页。
- **PASS — 已输出记录：** 前 4 条顺序正确、无重复，字段逐字一致，包括中文、引号、逗号、换行和 CRLF；CSV 可严格按 UTF-8 解码。
- **PASS — 文件保护：** 已有目标被拒绝，退出码为 2，内容未变；提供的实现、测试、需求及 fixture 哈希未变。
- **覆盖缺口：** 现有 smoke 运行通过，但仅断言退出码和表头，没有检查记录完整性、顺序或字段内容。

最小复现无需修改 fixture 或启用故障参数，在项目根目录运行，确保输出名未使用：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

预期 5 条，实际 4 条，退出码仍为 0。

保留的证据：[实际 CSV](<PROJECT>/artifacts/acceptance-20260908-160646-462633/actual.csv)、[完整比对和运行日志](<PROJECT>/artifacts/acceptance-20260908-160646-462633/observation.json)。

未修改应用；所有执行已结束，无遗留导出临时文件。结论仅针对提供的本地合成数据。
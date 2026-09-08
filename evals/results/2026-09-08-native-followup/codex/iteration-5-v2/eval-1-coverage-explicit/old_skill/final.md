**FAIL：smoke 虽然通过，用户仍会拿到缺记录的 CSV。**

- **完整性 FAIL**：原夹具有 5 条记录，实际导出只有 4 条，缺失第三页的 `r-005`。命令却退出 0、显示成功。
- **顺序与字段保真 PASS（仅已导出的 4 条）**：逐字段一致，包括中文、引号、逗号、LF、CRLF 和 emoji；无重复。
- **文件要求 PASS**：输出可按 UTF-8 读取；再次指定已有输出时退出 2，原文件字节不变。提供的文件哈希均未改变。

现有 smoke **只检查退出码和表头**，未覆盖完整性、顺序、字段保真及已有文件保护。根因是 `export.py` 默认执行 `selected_pages = pages[:-1]`，无条件丢弃最后一页。

最小复现无需修改夹具，在项目根目录使用一个不存在的输出名：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

预期包含 `r-001` 至 `r-005`；实际止于 `r-004`。

已保留[实际 CSV](project/artifacts/acceptance-20260908T160250944749/actual.csv)、[逐字段观察](project/artifacts/acceptance-20260908T160250944749/observation.json)和[命令、退出码与文件哈希](project/artifacts/acceptance-20260908T160250944749/execution.json)，同目录保留各次 stdout/stderr。

所有进程已结束，无遗留导出临时文件；未修改应用。结论仅针对提供的本地合成数据，远端服务不适用。
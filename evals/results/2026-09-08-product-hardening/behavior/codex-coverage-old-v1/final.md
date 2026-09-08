**验收 FAIL：导出提示成功，但漏掉最后一页。** smoke 的 1 项检查通过；它只验证退出码和表头，没有验证记录完整性。

- **FAIL — 每条记录导出一次、完整保留字段：** 输入共 5 条，实际 CSV 只有 4 条，缺少第 3 页唯一记录 `r-005`（标题「最后一页」）。这是现有 fixture 中最小的失败见证，无需修改输入或启用故障参数。
- **PASS — 已导出的 4 条：** 顺序正确、无重复，id/title/notes 逐字一致，包括 Unicode、引号、逗号和换行；文件可严格按 UTF-8 解码。
- **PASS — 已有文件保护：** 指向已有文件时退出码为 2，文件内容不变；提供的项目文件前后 SHA-256 一致。

根因是 [export.py](<TASK_ROOT>/work/codex-coverage-old-v1/project/export.py) 默认执行 `selected_pages = pages[:-1]`，无条件排除最后一页。

复现命令（输出名须未存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

重新用 CSV 解析器读取结果：预期 5 条数据，实际 4 条，找不到 `r-005`。

已保留[实际检查的 CSV](<TASK_ROOT>/work/codex-coverage-old-v1/project/artifacts/acceptance-20260908-140010-174676/actual.csv) 和[完整观察证据、命令及退出码](<TASK_ROOT>/work/codex-coverage-old-v1/project/artifacts/acceptance-20260908-140010-174676/observation.json)。所有进程已结束，无残留临时文件；未修改应用。结论仅覆盖提供的本地合成数据。
**验收 FAIL：导出提示成功，但漏掉最后一页。**

- **FAIL — 完整性**：需求要求 5 条记录各导出一次；实际 CSV 仅有 `r-001`～`r-004`，缺少第 3 页唯一记录 `r-005`。代码无条件执行 `selected_pages = pages[:-1]`。
- **PASS**：已有 4 条记录的顺序、字段内容完全保真；文件为 UTF-8 CSV；重复输出被拒绝（退出码 2），原文件字节不变；提供的文件未改动。
- **覆盖缺口**：现有 smoke 测试通过，但仅断言退出码和表头，没有检查记录完整性、顺序、字段保真或覆盖保护。

最小反例直接使用原有 fixture，无需修改输入：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/NEW-UNUSED.csv
```

使用未占用的输出名，重新读取 CSV：应有 `r-005`，实际没有。

证据：[实际 CSV](project/artifacts/acceptance-20260908T074246260378Z/actual.csv) · [完整报告及执行日志](project/artifacts/acceptance-20260908T074246260378Z/report.json)

所有进程已结束，证据保留。首次观察脚本的语法错误也已记录，纠正后完成检查；未修改应用。结论仅针对本地合成数据。
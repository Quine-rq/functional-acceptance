**验收 FAIL：导出提示成功，但漏掉最后一页。**

- 现有 smoke：**PASS**，仅检查退出码和表头，未覆盖完整性、顺序及字段保真。
- 实际导出：应有 5 条，只有 4 条；缺少第 3 页唯一记录 `r-005`（标题“最后一页”）。违反“每条记录恰好导出一次”。
- 已输出的 4 条记录：顺序、字段内容均准确，包括 Unicode、引号、逗号及换行；UTF-8 解码通过。
- 已存在目标保护：重复导出返回 `2`，原 CSV 字节未改变；所提供文件哈希未改变。

最小已实测反例：使用原始 fixture，正常执行，无需故障参数：

```bash
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

目标名称必须尚不存在。命令返回成功，却缺少 `r-005`。原因是 `export.py` 无条件执行 `selected_pages = pages[:-1]`。

已保留[实际检查的 CSV](project/artifacts/acceptance-20260908-161735-194784/actual.csv)及[完整证据与执行日志索引](project/artifacts/acceptance-20260908-161735-194784/report.json)。所有进程已结束，无残留临时文件；未修改应用。结论仅针对项目提供的本地合成数据。
**验收 FAIL：导出提示成功，但用户拿到的数据不完整。**

- 现有 smoke test：**PASS**，仅验证退出码和表头，未覆盖完整性、顺序、字段保真及原文件保护。
- 实际 CSV：应有 5 条，只有 4 条。第三页唯一记录 `r-005 / 最后一页` 丢失，违反“每条记录恰好导出一次”。
- 已导出的 4 条：顺序、字段、Unicode、引号及换行均准确，无重复；新文件为 UTF-8。
- 本次运行前后，提供的代码、测试、需求、fixture 和 sentinel 哈希一致。已有目标文件冲突保护未实测，属 **UNVERIFIED**。

原因是 `export.py` 中无条件执行 `selected_pages = pages[:-1]`，默认命令也会舍弃最后一页。

最小复现无需修改 fixture，在项目根目录运行（输出名称须未存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

退出码为 0，但 CSV 缺少 `r-005`，这一条记录已足以反证需求。

证据已保留：[实际 CSV](artifacts/acceptance-20260908-140100-117076/actual.csv)、[逐字段核对及哈希](artifacts/acceptance-20260908-140100-117076/observation.json)、[smoke 日志](artifacts/acceptance-20260908-140100-117076/smoke.json)、[导出日志](artifacts/acceptance-20260908-140100-117076/export.json)。

未修改应用；所有进程已结束，无遗留临时文件。
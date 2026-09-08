**验收 FAIL：导出提示成功，但漏掉最后一页。**

- 现有 smoke：1 项通过，仅检查退出码和表头，未覆盖完整性、顺序、字段保真及已有文件保护。
- 实际 CSV：应有 5 条，只有 4 条。最小反例是提供的第 3 页唯一记录 `r-005` 完全缺失。原因是 `export.py` 无条件执行 `selected_pages = pages[:-1]`，无需启用故障参数。
- 已验证：前 4 条顺序及字段值完全一致；输出是新建 UTF-8 CSV；运行前已有的 30 个文件内容哈希均未变化。

在项目根目录复现，输出路径须尚不存在：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

退出码为 0，但 CSV 缺少 `r-005`，违反“每条记录恰好导出一次”的要求。

已保留[实际 CSV](project/artifacts/acceptance-20260908/actual.csv) 和[完整观察记录](project/artifacts/acceptance-20260908/observation.json)，包括预期值、实际值及命令结果。未修改应用、测试、需求或 fixture；所有进程已结束，临时目录为空。
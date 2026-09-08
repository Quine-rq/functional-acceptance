验收 **FAIL**：导出提示成功，但用户拿到的数据不完整。

- **最小已实测反例**：使用原有 `fixtures/pages.json`，不加故障参数。预期 5 条，实际 CSV 只有 `r-001`～`r-004`，缺少第三页唯一记录 `r-005`。原因是 `export.py` 无条件使用 `pages[:-1]`。
- **覆盖缺口**：现有 smoke 通过，但仅检查退出码和表头，没有验证全部记录、顺序或字段内容。
- **通过项**：实际导出的四条记录无重复、顺序和字段完全一致（含换行、引号及 Unicode）；UTF-8 可解码；重复输出返回码 2，已有 CSV 内容未变。

在项目根目录复现，输出名须未存在：
```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

已保留[实际 CSV](project/artifacts/acceptance-20260908T154358058559/export.csv) 和[完整观察记录及命令结果](project/artifacts/acceptance-20260908T154358058559/observations.json)。

未修改应用、测试、需求或 fixtures；原有项目文件哈希未变。执行均已结束，无残留临时文件。结论仅适用于提供的本地数据。
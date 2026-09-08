**验收 FAIL：导出提示成功，但用户拿不到全部记录。**

- **FAIL｜完整性**：提供的 fixture 有 5 条记录，实际 CSV 只有 4 条，遗漏第 3 页唯一记录 `r-005`（标题「最后一页」）。默认执行路径使用 `pages[:-1]`，直接舍弃最后一页，无需故障参数即可复现。
- **PASS｜已有检查**：smoke 通过，但仅断言退出码和表头，未覆盖完整性、顺序或字段保真。
- **PASS｜实际观察**：已导出的 4 条记录各出现一次、顺序正确、字段完全保留；新文件为有效 UTF-8，已有项目文件哈希未变。
- **UNVERIFIED**：拒绝覆盖已有目标文件的分支未运行，遵守“不复用已有输出名”的限制。

最小已观察反例就是提供数据中的 `r-005` 缺失。在项目根目录使用一个全新文件名复现：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-unique.csv
```

重新读取 CSV，应有 5 条数据，实际只有 4 条。

保留的证据：[实际 CSV](project/artifacts/acceptance-20260908-161420/actual.csv)、[完整观察记录](project/artifacts/acceptance-20260908-161420/observations.json)，同目录包含测试和导出的原始输出。

两次子进程均已退出，无残留临时文件；证据保留，未修改应用、测试、需求或 fixtures。结论仅针对本地合成数据。
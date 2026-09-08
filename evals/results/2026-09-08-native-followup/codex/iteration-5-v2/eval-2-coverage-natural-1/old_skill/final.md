验收 **FAIL**：导出提示成功、退出码为 0，但用户丢失最后一页数据。

- **最小反例**：直接使用原 fixtures/pages.json，预期 5 条，实际只有 4 条；第 3 页唯一记录 `r-005` 完全缺失。无需故障参数。
- **根因**：export.py 无条件使用 `selected_pages = pages[:-1]`，跳过末页。
- **检查盲区**：现有 smoke 已运行通过，但只断言退出码和表头，没有覆盖“每条记录恰好导出一次”的要求。
- **通过部分**：已导出的 4 条顺序和字段完全一致，包括 Unicode、引号、换行；CSV 为 UTF-8。重复输出被拒绝（退出码 2），原文件内容未变。

复现命令（项目根目录，输出名必须尚不存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

保留证据：[实际 CSV](project/artifacts/acceptance-1788854663339396000/actual.csv)、[完整日志与逐字段对照](project/artifacts/acceptance-1788854663339396000/evidence.json)。

未修改应用、测试、需求或 fixtures；所有执行已结束，临时文件无残留。结论仅针对提供的本地数据。
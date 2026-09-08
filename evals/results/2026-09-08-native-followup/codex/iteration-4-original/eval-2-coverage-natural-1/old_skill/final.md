**验收 FAIL：用户看到导出成功，但最后一页的数据丢失。**

- **最小已实测反例**：直接使用提供的 `fixtures/pages.json`，不传 `--fault`。预期导出 5 条，实际只有 `r-001`～`r-004`；第三页唯一记录 `r-005`（标题“最后一页”）缺失，程序仍返回 0。
- **原因**：`export.py:130` 无条件执行 `selected_pages = pages[:-1]`，排除了最后一页。
- **覆盖缺口**：现有 smoke 重新运行通过，但只断言退出码和表头，未检查记录完整性、顺序或字段保真。

其余实测结果：已导出的四条记录顺序及字段完全一致，包括 Unicode、引号和换行；CSV 为 UTF-8；覆盖已有输出的尝试返回 2，原文件字节不变。提供的文件哈希均未改变。

在项目根目录复现（输出名必须尚不存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

保留的证据：[实际 CSV](project/artifacts/acceptance-20260908-154354-323923/actual.csv)、[逐字段观察及哈希](project/artifacts/acceptance-20260908-154354-323923/observations.json)。同目录保留全部执行日志，包括拒绝覆盖的失败记录。

未修改应用、测试、需求或 fixtures。所有进程已结束，临时文件已清理；结论仅针对本地合成数据。
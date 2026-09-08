**验收 FAIL：用户收到“导出成功”，但 CSV 丢失最后一页。**

- **最小已验证反例**：使用原始 `fixtures/pages.json`，不传 `--fault`，预期 5 条，实际仅 4 条，缺少第三页唯一记录 `r-005`（标题“最后一页”）。导出仍返回退出码 0。
- **原因**：[export.py:130](<TASK_ROOT>/work/codex-coverage-with-v3/project/export.py:130) 无条件执行 `pages[:-1]`。
- **Smoke PASS，但覆盖不足**：现有 1 项测试通过，只验证退出码和表头，未检查完整性、顺序、字段保真或已有文件保护。
- **实际观察 PASS**：已导出的 4 条顺序正确、各出现一次，字段逐字符一致（含 Unicode、引号、换行）；CSV 为 UTF-8。再次写入同一路径返回 2，文件内容不变。所有原有文件哈希未变。

在项目根目录复现（输出名必须尚不存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

证据已保留：[实际 CSV](<TASK_ROOT>/work/codex-coverage-with-v3/project/artifacts/acceptance-e61f9cf90e/actual.csv)、[比对结果及完整命令日志](<TASK_ROOT>/work/codex-coverage-with-v3/project/artifacts/acceptance-e61f9cf90e/report.json)。

未修改应用、测试、需求或 fixture；所有命令已结束，无残留导出临时文件。结论仅针对本地提供的数据。
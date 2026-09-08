**验收 FAIL：smoke 虽然通过，但用户会收到缺少最后一页的 CSV。**

- **FAIL — 全量、原样导出：**提供的 fixture 共 5 条，实际 CSV 只有 `r-001`～`r-004`。最小反例是第 3 页唯一记录 `r-005`（标题“最后一页”）完全缺失；命令仍退出 `0` 并提示成功。原因是 `export.py` 默认执行 `selected_pages = pages[:-1]`。
- **覆盖缺口：**现有 smoke 仅断言退出码和表头，没有验证记录数量、顺序或字段内容。
- **PASS — 已导出的 4 条：**重新打开实际 CSV，确认顺序、唯一性及全部字段精确一致，包括中文、引号、换行和 emoji；UTF-8 解码成功。
- **PASS — 文件保护：**同名输出被拒绝，退出 `2`，原 CSV 字节未变；提供的文件前后哈希一致。

实际文件：[actual.csv](project/artifacts/acceptance-20260908T155755905743/actual.csv)；完整命令、退出码、预期与实际值：[observation.json](project/artifacts/acceptance-20260908T155755905743/observation.json)。

在项目根目录复现，输出路径必须尚不存在：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

预期 5 条数据，实际 4 条。全部检查已终止，无遗留写入进程，证据已保留；未修改应用、测试、需求或 fixtures。结论仅针对本地合成数据。
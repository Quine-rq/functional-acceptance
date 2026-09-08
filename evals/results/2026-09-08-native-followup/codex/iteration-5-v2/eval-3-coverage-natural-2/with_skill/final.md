**验收不通过：命令成功，但用户拿到的 CSV 少了最后一页。**

- **FAIL — 全量导出**：输入共 5 条，实际只有 `r-001`～`r-004`。最小已观察反例是第 3 页唯一记录 `r-005`（标题“最后一页”）完全缺失。原因是 `export.py` 无条件使用 `pages[:-1]`，默认运行也会丢弃最后一页。
- **覆盖缺口**：现有 smoke 已运行通过，但只断言退出码和表头，无法发现漏记录。
- **PASS — 已导出内容**：4 条记录顺序正确，字段逐字一致，包括中文、引号、逗号、换行和 emoji；文件可严格按 UTF-8 解码。
- **PASS — 文件保护**：输出原先不存在；再次写同一路径返回退出码 2，原 CSV 字节不变。检查范围内的原有项目文件内容未变。

复现（在项目根目录，使用尚不存在的输出名）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

预期 5 条，实际 4 条，退出码仍为 0。

已保留[实际 CSV](project/artifacts/acceptance-1788854802758968000/export.csv)及[完整比对与运行证据](project/artifacts/acceptance-1788854802758968000/report.json)。所有进程已结束，无遗留临时文件；未修改应用、测试、需求或 fixture。
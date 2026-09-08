**验收失败：导出提示成功，但漏掉最后一页。**

- **FAIL — 完整导出**：提供的 5 条记录实际仅导出 `r-001`～`r-004`，缺少第 3 页唯一记录 `r-005`（标题 `最后一页`）。`export.py` 无条件执行 `selected_pages = pages[:-1]`。
- **PASS — 已导出内容**：前 4 条顺序正确、无重复，id/title/notes 精确保留，包括 Unicode、引号、逗号和换行；输出为新建 UTF-8 CSV。
- **PASS — 文件保护**：原有文件内容均未变化；对独立创建的既有目标再次导出返回退出码 2，目标内容保持不变。
- **覆盖缺口**：现有 smoke 通过，但只检查退出码和表头，没有断言记录完整性、顺序或字段内容。

最小复现无需修改夹具，在项目根目录执行，输出名须尚不存在：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

退出码为 0，却缺少 `r-005`，直接违反“每条记录恰好导出一次”。

已保留实际检查的 [CSV](project/artifacts/acceptance-1788854679093979000/actual.csv) 和包含命令、退出码、预期/实际内容及文件校验的 [验收证据](project/artifacts/acceptance-1788854679093979000/report.json)。所有进程已结束，无残留临时写入；未修改应用、测试、需求或夹具。
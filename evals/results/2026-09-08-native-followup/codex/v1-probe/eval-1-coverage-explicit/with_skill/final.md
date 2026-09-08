**验收 FAIL：导出显示成功，但漏掉最后一页。** 用户得到不完整的 CSV。

- **FAIL — 完整导出且每条一次：**提供的 5 条记录实际只导出 4 条，缺少第 3 页的 `r-005`。根因是 `export.py` 默认执行 `selected_pages = pages[:-1]`。
- **PASS — 已导出记录：**顺序正确、无重复，id/title/notes 与源数据逐字段相同，包括引号、中文、emoji 和换行。
- **PASS — 文件要求：**新文件可按 UTF-8 读取；尝试覆盖运行专属已有文件返回退出码 2，原字节不变。运行前已有的 30 个文件内容均未变化。
- **PASS — smoke：**1 个测试通过，但只断言退出码和表头，遗漏完整性、顺序、字段保真及文件保护要求。

最小可复现反例无需修改 fixture：在项目目录执行以下命令，确保输出名尚不存在：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

预期包含 `r-001` 至 `r-005`；实际成功退出却缺少 `r-005`。

已保留[实际检查的 CSV](project/artifacts/acceptance-20260908-155741-112542/actual.csv)和[完整观察记录及命令结果](project/artifacts/acceptance-20260908-155741-112542/observations.json)。所有进程已结束，无遗留临时文件；未修改应用、测试、需求或 fixtures。结论仅针对提供的本地数据，不涉及远程服务。
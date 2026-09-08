**验收 FAIL：导出提示成功，但用户少拿到最后一页的数据。**

- **FAIL｜全部记录完整保留**：实际重新打开 CSV，预期 5 条，只有 4 条；缺失 `r-005`（标题“最后一页”，notes 为 `END, "边界"\n末尾`）。原因是默认执行 `selected_pages = pages[:-1]`，无需故障参数就会漏页。
- **PASS｜已导出内容**：前 4 条顺序正确，三个字段逐值相同，包括中文、引号、换行和 emoji；文件是新建 UTF-8 CSV。
- **PASS｜已有文件保护**：对本次专属已有目标执行导出，退出码为 2，内容未变；项目原有文件前后逐字节一致。
- **PASS｜现有 smoke**：1 项通过，但只断言退出码和表头，未覆盖完整性、顺序、字段保真及覆盖保护。

最小复现无需改 fixture：在项目根目录执行以下命令，确保输出名尚不存在，然后检查 `r-005` 是否存在：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

实际证据：[CSV](project/artifacts/acceptance-20260908-160250-975452/export.csv) · [完整报告及命令结果](project/artifacts/acceptance-20260908-160250-975452/report.json)。

在预算内结束，所有子进程已退出，无遗留导出临时文件；证据保留，未修应用。结论仅针对提供的本地合成数据。
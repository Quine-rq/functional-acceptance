**FAIL：导出提示成功，但用户收到的 CSV 缺少最后一页。**

- **FAIL — 完整且恰好一次：**提供的夹具有 5 条记录，实际 CSV 只有 `r-001`～`r-004`。最小反例是第 3 页唯一记录 `r-005`（标题“最后一页”）完全缺失。根因是 `export.py` 默认使用 `pages[:-1]`。
- **PASS — 顺序及字段：**已导出的 4 条记录顺序正确，id/title/notes 原样保留，包括引号、Unicode、LF 和 CRLF；CSV 可按 UTF-8 读取。
- **PASS — 文件保护：**同名输出再次执行返回 2，原 CSV 哈希不变；提供的文件前后哈希一致。
- **PASS — 现有 smoke：**1 项通过，但只断言退出码和表头，未覆盖完整性、顺序或字段保真。
- **NOT_APPLICABLE — 远程交付：**需求明确仅验证本地合成数据。

在项目根目录，用未使用过的输出名即可复现：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

预期 5 条，实际 4 条，命令仍返回 0。

实际检查的 [CSV](export.csv) 和 [完整观察记录及执行日志](observations.json) 已保留。所有执行均已结束，无残留临时文件；未修改应用、测试、需求或夹具。
验收 **FAIL**：导出提示成功、退出码为 0，但用户收到的数据不完整。

- **FAIL｜全部记录恰好导出一次**：fixture 有 5 条，实际 CSV 只有 4 条，缺少第 3 页唯一记录 `r-005`（标题“最后一页”）。原因是 `export.py:130` 无条件执行 `pages[:-1]`。
- **PASS｜已输出记录顺序及字段保真**：前 4 条顺序正确，中文、引号、逗号、换行及 CRLF 均原样保留；CSV 可严格按 UTF-8 读取。
- **PASS｜已有文件不变**：重复输出被拒绝，退出码 2，原 CSV 字节不变；提供的文件哈希均未变化。
- **PASS｜现有 smoke**：1 项通过。但它仅断言退出码和表头，未覆盖完整性、顺序、字段保真或防覆盖。

最小已观察反例：使用原 fixture，无须任何故障参数，即漏掉 `r-005`。在项目根目录使用一个尚不存在的输出名复现：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

实际检查的 [CSV](project/artifacts/acceptance-f86725d5f3/export.csv) 与 [完整观察记录](project/artifacts/acceptance-f86725d5f3/observations.json) 已保留，同目录包含各次命令的 stdout/stderr。

在预算内结束，所有进程已退出，无残留临时文件；未修改应用、测试、需求或 fixture。结论仅针对提供的本地数据，不涉及远程或生产能力。
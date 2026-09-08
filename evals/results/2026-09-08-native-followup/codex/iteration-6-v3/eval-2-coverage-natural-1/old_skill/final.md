**验收 FAIL：导出显示成功，但漏掉最后一页。**

- 现有 smoke：PASS，但只检查退出码和表头，未覆盖完整性、顺序及字段保真。
- 实际 CSV：应有 5 条，仅有 4 条；缺少第 3 页的 `r-005`（标题“最后一页”）。违反“每条记录导出一次”的要求。
- 已导出的 4 条：顺序正确、无重复，字段内容逐字一致，UTF-8 解码成功。
- 已有文件保护：PASS，重复目标路径返回退出码 2，文件字节不变。项目原有文件哈希未变。

原因是 `export.py` 无条件执行 `selected_pages = pages[:-1]`，默认命令也会舍弃末页。

最小复现无需修改 fixture，在项目根目录执行（目标名必须不存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

退出码为 0，但 CSV 缺少 `r-005`，这一条缺失即足以反证需求。

保留证据：[实际 CSV](project/artifacts/acceptance-9p0k5hxs/export.csv)、[完整比较和执行记录](project/artifacts/acceptance-9p0k5hxs/report.json)。所有执行均已结束，无残留临时文件，未修改应用。结论仅针对提供的本地合成数据。
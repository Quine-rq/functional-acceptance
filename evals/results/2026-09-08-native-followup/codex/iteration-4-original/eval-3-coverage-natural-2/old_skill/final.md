**验收 FAIL：导出显示成功，但遗漏最后一页。**

- 原 fixture 有 5 条记录，实际 CSV 只有 4 条，缺少第三页唯一记录 `r-005`，违反“所有记录恰好导出一次”。
- 根因：`export.py:130` 无条件使用 `pages[:-1]`，正常执行也会丢弃末页，无需启用 `--fault`。
- 现有 smoke：1 项通过，但只检查退出码和表头，没有验证数量、顺序或字段内容。

最小复现无需修改输入，在项目根目录执行（输出名必须未存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

程序返回 0，但 CSV 缺少 `r-005`。

其余实测：已导出的 4 条顺序及字段完全一致、无重复、UTF-8 可解码；重复使用输出路径返回 2，原文件字节不变。

证据保留于：

- [实际 CSV](project/artifacts/acceptance-20260908-154551-501281/actual.csv)
- [逐项结果、预期与实际内容及执行日志](project/artifacts/acceptance-20260908-154551-501281/observations.json)

所有检查已结束；未修改应用、测试、需求或 fixtures，无项目外写入。结论仅针对提供的本地合成数据。
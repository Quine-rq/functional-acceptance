**验收 FAIL：用户收到“导出成功”，但 CSV 少了最后一页。**

- **FAIL｜完整导出、顺序与字段保真**：提供的数据有 5 条，实际仅 4 条；缺失第 3 页唯一记录 `r-005`（标题“最后一页”）。其余 4 条的顺序、字段值均一致。原因是 `export.py` 无条件使用 `pages[:-1]`。
- **PASS｜新建 UTF-8 CSV**：运行前目标不存在，运行后重新读取并成功解析。
- **PASS｜已有文件不变**：原有文件前后哈希一致；对本次创建的已有目标再次导出，退出码为 2，内容未变。
- **覆盖缺口**：现有 smoke 的 1 项测试通过，但只断言退出码和表头，无法发现漏记录。

最小已观察反例就是提供 fixture 中的 `r-005`：要求出现一次，实际零次。项目根目录复现（输出名必须尚不存在）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

实际检查的 [CSV](project/artifacts/acceptance-20260908-161418-131870/actual.csv)、[期望数据](project/artifacts/acceptance-20260908-161418-131870/expected.json)、[比对结果](project/artifacts/acceptance-20260908-161418-131870/observed.json)及[命令与退出结果](project/artifacts/acceptance-20260908-161418-131870/commands.json)均已保留。

所有执行进程已结束，无导出临时文件残留。未修改应用、测试、需求或 fixture；证据保留供复核。结论仅针对本地合成数据。
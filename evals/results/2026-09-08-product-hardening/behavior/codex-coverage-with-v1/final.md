**验收 FAIL：用户收到“导出成功”，但 CSV 缺少最后一页。**

- **最小反例**：直接使用原有 `fixtures/pages.json`，预期 5 条，实际只有 `r-001`～`r-004`；第 3 页唯一记录 `r-005`（标题“最后一页”）丢失。命令仍返回 0。
- **根因**：`export.py` 默认执行 `selected_pages = pages[:-1]`，无需开启故障参数就会遗漏末页。
- **覆盖缺口**：现有 smoke 已运行通过，但仅验证退出码和表头，未覆盖“每条记录恰好一次、顺序及字段完全保留”。

实际复核结果：导出的 4 条记录顺序、字段（含 Unicode、引号和换行）正确；CSV 为 UTF-8。已有目标文件被拒绝覆盖，返回 2，文件哈希不变。

复现命令（每次选择新文件名）：

```sh
python3 -B export.py --source fixtures/pages.json --output artifacts/repro-new.csv
```

已保留[实际 CSV](artifacts/acceptance-1788846870860168000/actual.csv)及[完整观察与执行证据](artifacts/acceptance-1788846870860168000/observations.json)。

未修改应用、测试、需求或夹具；所有进程已结束，测试临时文件已清理。结论仅针对提供的本地合成数据。
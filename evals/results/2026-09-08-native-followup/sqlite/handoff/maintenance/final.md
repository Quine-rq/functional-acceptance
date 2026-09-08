本轮合成维护验收通过：

- 未修改包独立重放、新字段版本均 **5/5 通过**。
- `"00123"` 字符串及前导零、首选名 `null`/空字符串均原样保留。
- 23 条旧断言全部保留，仅修改 acceptance 内两个文件。
- 无未预期失败；拒绝写入证据、命令终态和成本记录均已保存。耗时约 216 秒，不代表生产就绪。

报告：[INDEPENDENT-MAINTENANCE.md](WORKSPACE_ROOT/work/reuse-sqlite-independent-native/maintenance/project/artifacts/INDEPENDENT-MAINTENANCE.md)

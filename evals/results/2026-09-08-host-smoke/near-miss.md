**退出码 0 只说明命令报告成功，不能证明导出的数据完整、正确。** 现有测试特意展示了这个区别：

- **直接反例**：[test_export.py:65](test_export.py:65) 启用 `omit-final-page`，断言退出码仍为 0，但内容只有 `expected[:-1]`，随后确认完整性比较会抛出 `AssertionError`。只检查退出码就会漏掉“最后一页丢失”。
- **检查实际内容**：[test_export.py:42](test_export.py:42) 用 `csv.DictReader` 按 CSV 规则解析文件，先核对表头及列顺序，再将记录列表与独立的预期数据比较。这能检查记录数量、顺序和每个字段的值，而不只是文件存在。
- **覆盖特殊字符**：[expected_records.json:2](fixtures/expected_records.json:2) 包含逗号、双引号、中文、Emoji、空字符串以及 LF／CRLF。配合 `newline=""`，可以检查这些内容经过 CSV 导出、读取后是否原样保留。
- **预期独立于实现**：[test_export.py:24](test_export.py:24) 从固定 JSON 加载预期；[第 48 行](test_export.py:48) 的比较不从导出器内部或源分页数据重新计算答案，避免重复实现中的错误。

因此，正常测试同时检查**退出码成功和内容正确**（[test_export.py:55](test_export.py:55)），两者互补。

本轮仅阅读代码，未运行测试、执行导出或修改文件；上述是测试设计说明，不是测试通过结论。
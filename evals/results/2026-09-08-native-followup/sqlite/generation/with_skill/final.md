实际验收 **5/5 PASS**：联系人导入、跨 CLI 进程读取、JSON 导出、重复 id 可见拒绝、无关数据保留均符合需求。

已留下：

- [pytest 回归包](acceptance/test_onboarding.py)
- [Setup、重跑及清理说明](acceptance/README.md)
- [验收报告及两轮证据索引](acceptance/REPORT.md)

实际运行使用当前目录源码，未修改应用。重复 id 拒绝的原始命令、错误输出和数据库均保留；所有运行进程已退出。

回归包已由作者重跑，尚未经独立执行者复跑；本次结论仅限指定本地 CLI 链路。

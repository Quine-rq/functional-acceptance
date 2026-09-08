# 功能验收 Skill：项目介绍写法调研

核对日期：2026-09-08。仅使用项目自身的公开仓库和官方文档；“开头”指 README 内容顺序，未量测特定浏览器窗口的首屏高度。不用 star 数评判写法。

## 三个项目实际怎么介绍

### Superpowers：学行为叙述，不学抽象首句

About 原文：“An agentic skills framework & software development methodology that works.” README 首段同样先用方法论、skills 和初始指令解释身份，因此它的首句并不是解决我们问题的范本。[仓库与 README](https://github.com/obra/superpowers#readme)

值得学习的是紧随目录的 `How it works`：从用户启动编码助手讲起，依次说明澄清需求、展示设计、制定计划、执行及审查，让读者看见一次工作怎样发生。安装随后按客户端展开，命令放在对应客户端下；Hermes 的长会话限制也紧贴其安装说明。我们可学这种行为叙述与就近说明前提的方式，不宜照搬长安装目录或自动触发、完整方法论等承诺。[工作过程](https://github.com/obra/superpowers#how-it-works)、[安装](https://github.com/obra/superpowers#installation)

### Playwright：先让读者选到自己的任务，再跑一个例子

About 原文：“Playwright is a framework for Web Testing and Automation. It allows testing Chromium, Firefox and WebKit with a single API.” README 开头延续具体用途，接着用“产品／适合什么／安装”表格分流读者。[仓库与 README](https://github.com/microsoft/playwright#readme)

第一个产品段落按安装、写测试、运行测试、能力展开；示例包含导航、操作和结果断言。跨浏览器支持矩阵与其他语言放在后面。应学“输入动作加可观察结果”的演示结构；我们的单一 Skill 无需照搬多产品表，也不能据此宣称全平台支持。[测试示例](https://github.com/microsoft/playwright#playwright-test)、[支持矩阵](https://github.com/microsoft/playwright#cross-browser-support)

它也没有省掉前提：安装文档单列系统要求，并说明怎样打开报告、检查失败详情。对功能验收 Skill，展示结论之后怎样查看证据，同样应属于入门过程。[安装、报告与系统要求](https://playwright.dev/docs/intro)

### uv：用途先说清，性能主张紧跟证明材料

About 与 README 首句一致：“An extremely fast Python package and project manager, written in Rust.” 读者先知道管理什么；Rust 是句尾补充。随后是注明缓存条件的基准图、Highlights、安装、文档入口及各类任务示例。项目示例展示初始化、添加依赖、运行工具以及终端输出。[仓库与 README](https://github.com/astral-sh/uv#readme)

应学具体任务及输出示例，以及主张旁边给依据的顺序；不能照搬速度口号、一工具替代多个工具或生产可用声明。平台详情和生产状态在 FAQ 中链接到专门政策。[示例](https://github.com/astral-sh/uv#projects)、[FAQ](https://github.com/astral-sh/uv#faq)

细节并未被删掉：官方平台政策区分持续测试、只保证构建及尽力支持，版本政策另外说明兼容性边界。可学这种证据分级；功能验收 Skill 目前的 M1 状态会影响试用判断，应比成熟工具的 FAQ 更早出现。[平台政策](https://docs.astral.sh/uv/reference/policies/platforms/)、[版本政策](https://docs.astral.sh/uv/reference/policies/versioning/)

## 对 functional-acceptance 的结构建议

以下是基于上述观察的编辑判断，不是三个项目共同规定的模板。

1. **About：具体动作与结果。** 回答“帮我验收什么、会留下什么”，例如以“按真实使用场景验收功能，记录结果和证据”为方向。不要让读者先理解 stack-independent、技术栈无关或代理技能这些分类词。
2. **README 开头：使用时机及工作过程。** 从“功能写好了，要确认用户能否完成任务”进入，再用两三句说明提供哪些信息、怎样核对场景、最后怎么看结果。Skill 身份可以在用途讲清后补充。
3. **当前状态：在试用入口之前用短段写清。** 明示 M1 开发版；已跑通本地 CLI／CSV 样本；尚无跨项目、全平台或生产使用证据。把目标能力与已验证范围分开，详细证据可链接到后文。
4. **一个能复现的例子。** 用现有真实样本，给实际调用方式、输入、结果片段和证据路径，并解释通过、失败、未验证分别意味着什么。调用命令及产物名称须由本仓库实现核实后填写，不在文案中发明。
5. **安装与接入。** 只列已核实的接入方式；权限、所需工具、环境前提放在使用它们的步骤旁边。
6. **适配、限制与验证记录。** 解释迁移到新项目需要补充哪些信息，以及当前哪些场景尚未覆盖。不要把“未绑定某框架”写成“已经验证适用于所有框架”。

首句的具体程度与后文边界的诚实程度可以同时提高。我们需要调整的是读者获取信息的顺序；M1 的未验证范围仍应清楚可见。

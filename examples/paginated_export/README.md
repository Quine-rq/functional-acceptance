# 离线分页 JSON → CLI → CSV

这是一个独立、受控的原生样本，使用 Python 标准库。上游分页响应来自合成 fixture；实际执行的是 Python 进程、CSV 编码和本机文件落盘。没有安装依赖、联网、账号、真实远端 API 或生产数据，也不表示完整 Skill 或其他平台已经验证。

## 直接运行

以下命令从本目录执行，需要 Python 3.8+ 和支持同目录硬链接的本地文件系统。输出目录由 `mktemp` 新建；每次使用不同文件名，既存输出会被拒绝。

```sh
sample_run_dir="$(mktemp -d "${TMPDIR:-/tmp}/acceptance-export.XXXXXX")"
python3 export.py --source fixtures/pages.json --output "$sample_run_dir/healthy.csv"
python3 export.py --source fixtures/pages.json --output "$sample_run_dir/defective.csv" --fault omit-final-page
python3 export.py --source fixtures/empty_pages.json --output "$sample_run_dir/empty.csv"
```

接口：`--source` 必填本地 UTF-8 JSON 普通文件，最多 2 MiB（2,097,152 字节），拒绝源文件本身为符号链接或特殊文件；`--output` 必填一个新 CSV 路径，父目录必须存在。默认导出所有页面。唯一缺陷开关 `--fault omit-final-page` 显式漏掉最后页，但仍返回 0，用于证明“命令成功不等于用户获得完整结果”。参数/输入/文件错误，包括超限和过深 JSON 嵌套，返回 2 并在 stderr 输出友好错误；不会自动改名、覆盖文件或创建父目录。

CSV 固定 UTF-8、表头 `id,title,notes`。完整内容期望见 [固定用户要求](requirements.md) 与 `fixtures/expected_records.json`。健康样本为 3 页 5 条，缺陷样本为 4 条且缺 `r-005`；空结果仍有表头。CSV 字段包含换行，不能用文件行数作为记录数。

## 无 Skill 的原生检查

从本目录运行：

```sh
python3 -B -m unittest discover -s . -p 'test_export.py' -v
```

或从仓库根目录运行：

```sh
python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v
```

测试启动实际 CLI 子进程，并用标准 CSV 读取器核对独立固定期望，不导入 exporter 内部函数。测试覆盖健康、缺页但返回 0 的反证、空结果、非法输入、大小边界、深嵌套、源符号链接/管道拒绝、Unicode/CSV 转义、源文件保护、既存文件/目录/链接不覆盖，以及同名并发写入。

其中缺陷对照测试确认同一完整性检查对缺陷 CSV 报错，所以整套 unittest 通过表示**成功检出了故意注入的缺陷**，不表示那次缺陷导出满足用户要求。测试临时目录结束时自动清理，无需 Skill、原始 Agent 会话或网络。

## 文件安全与清理

程序限制源文件读取字节数并检查实际打开对象，校验输入和编码完整 CSV 后，才在输出目录创建自己的临时文件并排他发布。健康和缺陷模式均拒绝任何既存输出，包括悬空符号链接；并发写同一路径只有一个能成功。文件系统不支持所需硬链接时明确报错，不改用覆盖写入。这个小样本在明确输入上限内使用内存，不宣称适用任意大数据流或不可信共享目录，也不会为“清洗”而隐式改写正常 CSV 字段。

正常可处理错误会清理本次临时文件。进程被强制终止、系统掉电或磁盘故障可能留下该新目录中的 `.export-*.tmp`；这不是完整发布产物。本样本没有后台任务或自动清理守护进程。

手工运行的输出会保留，方便检查。确认不再需要后，只删除本次 `sample_run_dir` 中明确知道的三个文件，再删除这个空目录：

```sh
rm -- "${sample_run_dir:?}/healthy.csv" "${sample_run_dir:?}/defective.csv" "${sample_run_dir:?}/empty.csv"
rmdir -- "${sample_run_dir:?}"
```

若其中某次没有成功，按实际存在的文件调整明确路径；若目录仍有临时文件，先查看后按完整文件名处理，不递归清空其他目录。保留产物用于证据时，按所属验收运行约定的保留期限处置，不将删除后的原址引用继续当成可复核事实。

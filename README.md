# 填词作品统计工具（Vagary）

帮助你统计填词/歌词作品中的高频词、查看某个词出现在哪些作品、以及统计合作者。项目对中文歌词做分词（支持 jieba 或内置保底算法），并能导出统计表与图表。

---

## 主要功能（快速概览）

- 按作品数统计高频词（同一首歌中重复出现只计一次）。
- 查询某��词在哪些作品中出现，并列出命中的歌词行。
- 按「演唱 / 作曲 / 编曲」统计合作者出现频次。
- 导出 Excel 报表（输出：output/统计结果.xlsx）和图表（output/charts/）。
- 可通过命令行（无需打开 Notebook）完成全部统计或单词查询。

---

## 目录

- [快速开始（命令行）](#快速开始命令行)
- [命令行用法示例](#命令行用法示例)
- [数据格式说明](#数据格式说明)
- [个人词典与排除词](#个人词典与排除词)
- [进阶：在没有 jieba 时如何运行](#进阶在没有-jieba-时如何运行)
- [常见问题 & 排查](#常见问题--排查)
- [开发与测试](#开发与测试)

---

## 快速开始（命令行）

下面演示在 Windows 和 macOS / Linux 上的常见操作（假设你已经把仓库克隆到本地，并在仓库根目录）：

1. 创建并激活虚拟环境

- Windows (cmd):

```
python -m venv .venv
.venv\Scripts\activate
```

- Windows (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- macOS / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
```

2. 安装依赖并安装本包（可编辑模式，方便开发）

```
pip install -r requirements.txt
pip install -e .
```

3. 运行完整统计（把结果保存到 output/）：

```
python -m vagary --data data/vagary.xlsx --output output/
```

4. 查询某个词在哪些作品出现（只输出匹配列表，不生成图表）：

```
python -m vagary --data data/vagary.xlsx --search 夜色
```

运行后会在终端打印摘要，并把 Excel 报表保存到你指定的输出目录，图表会保存在 output/charts/ 下。

---

## 命令行用法示例

vagary 的命令行入口基于 `python -m vagary`，常用选项：

- `--data, -d` : 指定 Excel 数据文件路径，默认 `data/vagary.xlsx`。
- `--output, -o` : 指定输出目录，默认 `output`。
- `--user-dict` : 指定个人词典文件（每行一个词，或 jieba 格式的词典）。
- `--exclude, -e` : 排除词列表（在命令行里空格分隔）。
- `--search, -s` : 只查询某个词在哪些作品中出现。
- `--no-jieba` : 不使用 jieba，改用项目内置的保底分词算法。

示例：

- 使用自定义词典并排除若干词，然后运行完整统计：

```
python -m vagary --data data/vagary.xlsx --output output/ --user-dict data/personal_dict.txt --exclude 我们 你们 一个
```

- 仅查询某个词（快速）：

```
python -m vagary --search 夜色
```

- 如果你���望在没有互联网的环境或没有安装 jieba 的情况下运行：

```
python -m vagary --no-jieba
```

---

## 数据格式说明

程序会读取 Excel（默认第一个工作表），**必须包含以下 5 列**（列名必须一致）：

- `歌曲名`
- `演唱`
- `作曲`
- `编曲`
- `歌词`

注意：
- `歌词` 列内容会按行拆分以便显示命中歌词行；若某行为空会被视为空字符串。
- 合作者字段（演唱 / 作曲 / 编曲）会以半角或全角斜杠 `/` / `／` 拆分为多人，例如 `甲/乙/丙`。

---

## 个人词典与排除词

- 个人词典（user dict）格式：每行一个词（也可使用 jieba 的词频/词性格式，后两列可省略）。示例：`data/personal_dict_example.txt`。
- 使用方法：拷贝示例并命名为 `data/personal_dict.txt`，然后在命令行或 Notebook 中通过 `--user-dict data/personal_dict.txt` 指定。
- 排除词：通过 `--exclude` 在命令行中传入，例如 `--exclude 我们 你们 一个`；在 Notebook 中请修改 `EXCLUDE_WORDS` 常量所在的单元格并重新运行。

---

## 进阶：在没有 jieba 时如何运行

项目默认会尝试使用 jieba（如果已安装），否则自动降级为内置的“2-4 字滑动窗口”分词策略，能保证即使没有 jieba 也能运行，但分词质量会差一些。

如果你想强制不使用 jieba（例如出于可重复性或调试），加 `--no-jieba`。

若想安装 jieba：

```
pip install jieba
```

---

## 常见问题 & 排查

- 报错：ModuleNotFoundError: No module named 'vagary'
  - 原因：没有执行 `pip install -e .`，或没有激活虚拟环境。
  - 解决：激活虚拟环境（终端前缀会显示 `(.venv)`），然后执行 `pip install -e .`。

- 报错：找不到数据文件
  - 请确认 `--data` 指定路径是否正确，或把 `vagary.xlsx` 放到 `data/` 下并使用默认路径。

- 图表中文显示成方框（字体问题）
  - 原因：系统缺中文字体。请在系统中安装中文字体（如微软雅黑 / SimHei），或在绘图代码中指定本地中文字体路径。

- PowerShell 提示无法加载脚本（激活 .venv 失败）
  - 在 PowerShell 中可执行：

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

然后重新运行激活脚本。

- 个人词典未生效
  - 确认 `--user-dict` 指定的路径存在且文件编码为 UTF-8（不带 BOM），再运行命令或在 Notebook 重新运行相关单元格。

---

## 开发与测试

- 运行仓库自带测试（需要先安�� pytest）：

```
pip install pytest
pytest -q
```

- 如果你修改了代码并想在本地测试修改效果，请使用可编辑安装：

```
pip install -e .
```

- 输出结果位置：
  - 报表： `output/统计结果.xlsx`
  - 图表： `output/charts/` 下若干图片（PNG）

---

## 自动化 / 批量运行（示例）

- 在 Linux/macOS 上用 cron 定期运行（示例每周一早上 3 点执行一次）：

```
0 3 * * 1 cd /path/to/Vagary && source .venv/bin/activate && python -m vagary --data data/vagary.xlsx --output output/
```

- 在 Windows 上可以用任务计划程序（Task Scheduler）运行等效命令。

---

## 贡献 & 联系

欢迎提交 issue 或 PR 来改进：
- 修复 bug
- 改进分词或排除策略
- 增加更多可视化样式

---

如果你希望我把这个 README 直接提交到仓库，我可以代为更新（会在仓库根目录提交一个 README.md 的修改）。若需要我现在就提交，请回复“现在提交”。
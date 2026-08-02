# Vagary —— 原创填词作品统计工具

统计你写的歌词中哪些词用得多、谁和你合作最频繁。

---

## 目录

- [这是什么](#这是什么)
- [文件夹里都有些啥](#文件夹里都有些啥)
- [第一次上手（跟着一步步做）](#第一次上手跟着一步步做)
  - [第 0 步：打开"终端"](#第-0-步打开终端)
  - [第 1 步：创建虚拟环境](#第-1-步创建虚拟环境)
  - [第 2 步：激活虚拟环境](#第-2-步激活虚拟环境)
  - [第 3 步：安装依赖](#第-3-步安装依赖)
  - [第 4 步：安装本项目](#第-4-步安装本项目)
  - [第 5 步：打开 Notebook](#第-5-步打开-notebook)
- [之后怎么用](#之后怎么用)
- [常见问题](#常见问题)

---

## 这是什么

Vagary 帮你统计歌词数据——读取 Excel 里的歌词表格，用 jieba 把歌词切成词，然后告诉你：

- 哪些词在你的作品中出现最多（同一首歌唱多次只算 1 次）
- 某个词在哪些歌里出现过（附带命中歌词行）
- 和谁合作最多（演唱、作曲、编曲三种统计）
- 每首歌命中了多少个全局高频词

---

## 文件夹里都有些啥

```
Vagary/
├── README.md                         ← 你正在看的这个文件
├── pyproject.toml                     ← 让 Python 认识这个项目（不需要管它）
├── requirements.txt                   ← 依赖清单（pip install 的时候会自动读）
│
├── src/vagary/                        ← 程序代码
│   ├── __init__.py
│   ├── stats.py                       ← 核心统计：分词、词频、查询、合作者
│   ├── plotting.py                    ← 画图：词频柱状图、合作者柱状图
│   └── __main__.py                    ← 命令行入口（不需要管，Notebook 用户忽略）
│
├── tests/                             ← 测试
│   ├── test_basic.py                  ← 自动测试（不需要管）
│   └── Vagary_统计分析.ipynb          ← ★ 你要打开的文件！Jupyter Notebook
│
├── data/                              ← 数据
│   ├── vagary.xlsx                    ← 你的作品数据表
│   └── personal_dict_example.txt      ← 个人词典示例
│
└── output/                            ← 输出文件（统计表、图表会保存到这里）
```

---

## 第一次上手（跟着一步步做）

下面的步骤**只需要做一次**。做完之后，以后每次只用 2 步就能开始用（见[之后怎么用](#之后怎么用)）。

---

### 第 0 步：打开"终端"

> 终端就是一个黑框框窗口，你在里面打字告诉电脑要干什么。

**Windows 10/11 打开方式：**

1. 在 Vagary 文件夹里，**点一下地址栏**（显示 `...\Vagary` 那个白条）
2. 删掉地址栏里的内容，输入 **`cmd`**，然后按回车
3. 会弹出一个黑色窗口，光标在闪烁——这就是终端

或者：
1. 按键盘上的 **`Win + R`**（Win 键就是键盘左下角那个 Windows 标志键）
2. 输入 `cmd`，点确定
3. 在终端里输入 `cd `（注意 cd 后面有个空格），然后把 Vagary 文件夹**直接拖进终端窗口**，按回车

---

### 第 1 步：创建虚拟环境

> 虚拟环境是什么？你电脑上可能装了多个 Python，或者 pip 装了一堆乱七八糟的包。虚拟环境就是给这个项目**单独划一片干净的地方**，互不干扰。

在终端里输入（复制粘贴也行，在终端里右键粘贴）：

```
python -m venv .venv
```

然后按回车。等几秒钟，**什么都不会显示**——没问题，正常现象。这一步在 Vagary 文件夹里悄悄创建了一个叫 `.venv` 的文件夹。

---

### 第 2 步：激活虚拟环境

终端里输入：

```
.venv\Scripts\activate
```

按回车。如果一切正常，你会发现**终端的行首多了 `(.venv)`**，像这样：

```
(.venv) C:\...\Vagary>
```

这表示你已经进入虚拟环境了。**以后每次打开终端都要先做这一步**。

> 提醒：如果报错说"无法加载文件因为在此系统上禁止运行脚本"，说明你的 PowerShell 执行策略被限制了。输入这条命令解决：
> ```
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> 然后重新激活。

---

### 第 3 步：安装依赖

终端里输入（确保前面有 `(.venv)`）：

```
pip install -r requirements.txt
```

按回车，它会开始下载几个包（pandas、jieba、matplotlib、jupyterlab 等）。**需要联网**，等一两分钟，最后看到 `Successfully installed ...` 就 OK 了。

---

### 第 4 步：安装本项目

终端里输入（确保前面有 `(.venv)`）：

```
pip install -e .
```

**注意最后的那个点 `.` 不要漏掉！** 它的意思是"把当前文件夹当成一个 Python 包安装"。

按回车，很快结束。这一步让 Notebook 里 `from vagary import ...` 能正常工作。

---

### 第 5 步：打开 Notebook

终端里输入（确保前面有 `(.venv)`）：

```
jupyter lab tests/Vagary_统计分析.ipynb
```

按回车。**浏览器会自动打开 JupyterLab**，Notebook 文件已经加载好了。

点击菜单栏的 **Run → Run All Cells**（全部运行），等几秒钟，就能看到：
- 2 字 / 3 字 / 4 字高频词表
- 高频词柱状图
- "夜色"一词的查询结果示例
- 每首歌的高频词命中情况
- 合作者统计（全部合作 / 演唱合作 / 曲合作）

把示例中的查询词换成你想查的词，再运行对应的单元格就行。

---

## 之后怎么用

**以后每次使用就两步：**

1. **打开终端，进入 Vagary 文件夹，激活虚拟环境：**
   ```
   cd Vagary 的路径
   .venv\Scripts\activate
   ```

2. **启动 Jupyter：**
   ```
   jupyter lab tests/Vagary_统计分析.ipynb
   ```

或者如果你用的是 Anaconda：

打开 **Anaconda Navigator** → 启动 **JupyterLab** → 在文件浏览器里导航到 `Vagary/tests/` → 双击 `Vagary_统计分析.ipynb`。

**但是**，用 Anaconda 的话，要先在 Anaconda 的命令行里执行一次上面的第 3、4 步（`pip install -r requirements.txt` 然后 `pip install -e .`）。

---

## 常见问题

### Q: "ModuleNotFoundError: No module named 'vagary'"

说明你没做第 4 步（`pip install -e .`），或者不在虚拟环境中。确认终端前面有 `(.venv)`，然后执行 `pip install -e .`。

### Q: 图表中的中文显示为方框

系统缺中文字体。程序已经配置了 Microsoft YaHei → SimHei → Arial Unicode MS 依次尝试，如果都显示方框，去网上下载一个"微软雅黑"字体安装即可。

### Q: 如何修改排除词？

打开 Notebook，找到 `EXCLUDE_WORDS` 那一行，在大括号里增删词语即可。

### Q: 如何使用个人词典？

1. 把 `data/personal_dict_example.txt` 复制一份，改名为 `data/personal_dict.txt`
2. 在里面写入不希望被切碎的词（每行一个），比如"人间"、"天地"这类
3. Notebook 里会自动检测到 `personal_dict.txt` 并加载

### Q: 我想更新数据怎么办？

把新的 `vagary.xlsx` 放到 `data/` 文件夹里覆盖旧的（确保列名不变），然后重新运行 Notebook 即可。

### Q: "打开终端"我还是不会

如果你实在不想用终端，还有一个保底办法：安装 [Anaconda](https://www.anaconda.com/download)（点击 Download 安装），它自带图形界面。安装后：
1. 打开 Anaconda Navigator
2. 点击 Environments → Create（新建一个环境，起名叫 `vagary`）
3. 点击新环境的绿色三角 → Open Terminal
4. 在终端里做上面的第 3、4 步
5. 以后从 Anaconda Navigator 直接启动 JupyterLab

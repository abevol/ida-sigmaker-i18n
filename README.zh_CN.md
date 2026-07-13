[**English**](./README.md) | [**中文**](./README.zh_CN.md)

---

# Signature Maker 插件 —— 适用于 IDA Pro 9.0+

<img src="https://github.com/mahmoudimus/ida-sigmaker/blob/main/assets/sigmaker-logo.png?raw=true" width="104px" height="100px" alt="放大镜，内含 'sigmaker' 字样，字母 'A' 上带有十字准线" /> [![ida-sigmaker 测试](https://github.com/mahmoudimus/ida-sigmaker/actions/workflows/python.yml/badge.svg)](https://github.com/mahmoudimus/ida-sigmaker/actions/workflows/python.yml)

一款 IDA Pro 9.0+ 的零依赖、跨平台签名生成插件，可选 SIMD（如 AVX2/NEON/SSE2）加速，支持 macOS/Linux/Windows。本插件的主要目标是适配未来版本的 IDA，无需针对 IDA SDK 编译，同时降低社区贡献的门槛。

背景阅读材料见 [mahmoudimus.com](https://mahmoudimus.com)：

- [IDA Pro 与 Cython：为逆向工程的主力工具注入超强动力](https://mahmoudimus.com/blog/2025/08/ida-pro-and-cython-super-charging-the-work-horse-of-reverse-engineering/)：介绍了可选的 SIMD 加速是如何构建的。
- [无需重新扫描二进制文件即可生成唯一函数签名](https://mahmoudimus.com/blog/2026/05/growing-a-unique-function-signature-without-rescanning-the-binary/)：搜索算法详解，含交互式可视化。
- [如何判断你的 Cython 热循环够快？](https://mahmoudimus.com/blog/2026/05/how-do-you-know-your-cython-hot-loop-is-fast-enough/)：如何确认这些内核已是最优（受限于内存带宽，而非计算能力）。

## 目录

- [安装](#安装)
  - [快速安装](#快速安装)
  - [从 Releases 安装](#从-releases-安装)
  - [通过 hcli 安装](#通过-hcli-安装)
  - [需要查找插件目录？](#需要查找插件目录)
  - [默认用户目录在哪？](#默认用户目录在哪)
- [SIMD 加速](#simd-加速)
- [环境要求](#环境要求)
- [什么是 "sigmaker"？](#什么是-sigmaker)
- [使用方法](#使用方法)
  - [查找 XREF](#查找-xref)
  - [签名搜索](#签名搜索)
  - [签名配置](#签名配置)
- [性能](#性能)
  - [基准测试](#基准测试)
  - [工作原理](#工作原理)
- [将 SigMaker 作为库使用](#将-sigmaker-作为库使用)
  - [稳定性契约](#稳定性契约)
  - [已被以下项目使用](#已被以下项目使用)
- [致谢](#致谢)
- [开发与发布](#开发与发布)
  - [贡献](#贡献)
- [联系方式](#联系方式)

## 安装

sigmaker 的核心价值在于其跨平台（Windows、macOS、Linux）的 Python 3 支持。它使用零第三方依赖，代码既便携又易于安装。

### 快速安装

- 将 [`src/sigmaker_loader.py`](./src/sigmaker_loader.py) 和 [`src/sigmaker/`](./src/sigmaker/) 目录复制到你的 IDA Pro `plugins/` 文件夹
- *可选*，如果你想要 `SIMD` 加速，只需执行 `pip install sigmaker`
- 重启 IDA Pro。

### 从 Releases 安装

- 从 [Releases 页面](https://github.com/mahmoudimus/ida-sigmaker/releases) 下载最新的 `sigmaker-*.zip` 发布包
- 将 zip 内容解压到你的 IDA Pro `plugins/` 目录
- *可选*，如果你想要 `SIMD` 加速，只需执行 `pip install sigmaker`
- 重启 IDA Pro

解压后你的 `plugins/` 目录结构如下：

```
plugins/
├── sigmaker_loader.py   (IDA 启动时加载此文件)
└── sigmaker/
    ├── __init__.py       (签名制作核心逻辑)
    ├── i18n.py           (多语言支持)
    └── locale/           (翻译文件)
```

插件同时支持**中文和英文**界面，语言根据系统区域设置自动切换。

### 通过 hcli 安装

[`hcli`](https://hcli.docs.hex-rays.com/) 是 Hex-Rays 的命令行工具，可以从 IDA 插件仓库安装 sigmaker。首先安装 `hcli`：

```bash
curl -LsSf https://hcli.docs.hex-rays.com/install | sh        # macOS/Linux
iwr -useb https://hcli.docs.hex-rays.com/install.ps1 | iex    # Windows (PowerShell)
```

然后进行身份验证（参见 [hcli 文档](https://hcli.docs.hex-rays.com/)）并安装插件：

```bash
hcli plugin search sigmaker
hcli plugin install SigMaker
```

`hcli` 会下载插件并将其放置在 `$IDAUSR/plugins`（macOS/Linux 下为 `~/.idapro/plugins`）目录中，下次启动 IDA 时自动加载。需要 IDA 9.0+。如需 `SIMD` 加速，也请按上述方法执行 `pip install sigmaker`。

插件使用引导加载器（`sigmaker_loader.py`）委托到 `sigmaker/` 子目录，该目录包含插件逻辑、国际化模块和翻译文件。这种设计使业务代码更清晰，更新也更方便 —— 只需替换 `sigmaker/` 子目录即可。

### 需要查找插件目录？

在 IDA 的 Python 控制台中执行以下命令即可找到插件目录：

```python
import idaapi, os; print(os.path.join(idaapi.get_user_idadir(), "plugins"))
```

### 默认用户目录在哪？

用户目录是 IDA 存储部分全局设置的位置，也可用于一些额外定制。默认位置：

- Windows：`%APPDATA%/Hex-Rays/IDA Pro`
- Linux 和 Mac：`$HOME/.idapro`

## SIMD 加速

如果你已按上述安装步骤执行了 `pip install sigmaker`，插件会根据你的系统和架构（即 Windows (x64)、Linux (x64)、Mac (x64)、Mac (ARM/Silicon)）安装相应的 wheel，并在可用时自动启用。你无需做任何额外操作。插件会在右上角菜单栏中显示 SIMD 加速的启用状态：

### SIMD 已启用

![](./assets/simd_enabled.png)

### 未启用 SIMD 加速

![](./assets/no_simd_speedup.png)

## 环境要求

- IDA Pro 9.0+
- IDA Python
- Python 3.10+

## 什么是 "sigmaker"？

Sigmaker 即 "signature maker"（签名生成器）。它使用户能够创建唯一的二进制模式签名，用于识别二进制文件中的特定地址或例程，即使在二进制文件更新后也能准确定位。

在恶意软件分析或二进制逆向工程中，常见的挑战是如何精确定位一个重要地址，例如某个函数或全局变量。然而，当二进制文件更新后，如果这些地址发生变化，之前所有定位工作都可能付诸东流。

为了解决这个问题，逆向工程师利用了一个事实：大多数程序在更新之间不会发生剧烈变化。虽然某些函数或数据可能被修改，但二进制文件的绝大部分保持不变。多数情况下，之前已识别的地址只是被重新定位了。这正是 `sigmaker` 的用武之地。

Sigmaker 让你能够创建独特的模式来追踪程序的重要部分，使你的分析在面对更新时更具弹性。通过为特定函数、数据引用或其他关键位置生成签名，你可以在新版二进制文件中快速重新定位这些点，从而节省未来逆向工程任务中的时间和精力。

## 使用方法

在反汇编视图中，选中要为其生成签名的行，按下 **CTRL+ALT+S**：
![](./assets/gen_signature.png)

*或者* *右键单击*，选择 *SigMaker*：
![](./assets/right_click.png)

生成的签名将输出到控制台，**同时也会复制到剪贴板**：
![](./assets/output_sig.png)

___

| 签名类型 | 示例预览 |
| --- | ----------- |
| IDA 签名 | `E8 ? ? ? ? 45 33 F6 66 44 89 34 33` |
| x64Dbg 签名 | `E8 ?? ?? ?? ?? 45 33 F6 66 44 89 34 33` |
| C 字节数组签名 + 字符串掩码 | `\xE8\x00\x00\x00\x00\x45\x33\xF6\x66\x44\x89\x34\x33 x????xxxxxxxx` |
| C 原始字节签名 + 位掩码 | `0xE8, 0x00, 0x00, 0x00, 0x00, 0x45, 0x33, 0xF6, 0x66, 0x44, 0x89, 0x34, 0x33  0b1111111100001` |

___

### 查找 XREF

支持通过数据或代码交叉引用（xref）生成代码签名，并找出最短签名：
![](./assets/xref_search.png)

___

### 签名搜索

支持对已支持的格式进行签名搜索：

![](./assets/sig_search.png)

还支持通配半字节搜索：

![](./assets/nibble_wildcard_search.png)

只需输入包含签名的任意字符串，插件会自动判断所使用的签名格式：

![](./assets/smart_format_sig_search.png)

目前所有可输出的格式均受支持。

签名的匹配结果将输出到控制台，同时显示所属函数名：

![](./assets/matches_console.png)

如果匹配地址不是函数名或没有函数名，则仅打印地址：

![](./assets/matches_console_no_func.png)

### 签名配置

`sigmaker` 还支持可配置的通配操作数，用于生成唯一签名：

![](./assets/operand_selection.png)

此外，可通过 `Other options`（其他选项）按钮配置各种选项：

![](./assets/optional_configuration.png)

## 性能

SigMaker 的"为当前函数查找最短唯一签名"搜索已经过重度优化。在一个真实的 16 MB 模块上，单个最坏情况的函数搜索曾需要 **462 秒（7.7 分钟）**。通过四层优化，最重搜索降至数十秒，典型搜索几乎瞬时完成。有用户[报告](https://github.com/mahmoudimus/ida-sigmaker/issues/27#issuecomment-4577775008)称，进度等待框现在"对于 26 字节的签名几乎不再出现"。

完整的推导过程，包括匹配集数学原理、计数排序索引、选择性证明以及该方法的创新点，均已写入 **[ALGORITHM.md](./ALGORITHM.md)**。

### 基准测试

在 Apple Silicon 上通过原生 idalib 对 16 MB 模块的最大函数（8486 字节）进行测量。优化效果在四个阶段中累积：

| 优化阶段 | 效果 | PR |
| --- | --- | --- |
| 阶段 1：种子-精炼（seed-then-refine）候选优化 | 函数搜索速度提升约 13 倍 | [#33](https://github.com/mahmoudimus/ida-sigmaker/pull/33) |
| 阶段 2：2 字节桶位置索引 | 在大型数据库上额外提升约 2.48 倍，效果随数据库增长而扩大 | [#35](https://github.com/mahmoudimus/ida-sigmaker/pull/35) |
| 阶段 3：动态种子选择（1 字节或 2 字节） | 每个锚点的种子扫描从 206 次降至 2 次 | [#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36) |
| 阶段 4：Cython 原地精炼 | 每字节精炼从约 14 秒降至约 0.28 秒（约 50 倍）；函数总计从约 24 秒降至约 15.6 秒 | [#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36) |

每次优化前后签名输出字节级别完全一致。测试套件将每条快路径与暴力穷举预言进行交叉校验，并在整个测试二进制文件上对比生成的签名差异。

### 工作原理

简要概览（数学细节见 [ALGORITHM.md](./ALGORITHM.md)）：

- **先种子，再精炼。** 数据库的匹配集随签名增长只会缩小，因此无需为每个候选长度重新扫描整个数据库；SigMaker 扫描一次得到种子候选集，然后在追加每个字节时原地过滤该集合。
- **数据库索引只需构建一次。** 一个针对所有相邻字节对的计数排序索引，使得种子可以从模式中*最稀有*的精确字节序列中获取，所需时间与该字节序列的频率成正比，而非与数据库大小成正比。同一个索引同时支持 1 字节和 2 字节序列，因此总能选择最具选择性的锚点。
- **将热循环推入 C 语言。** 通过可选的 `pip install sigmaker` SIMD wheel，索引构建和每字节精炼在类型化缓冲区上以 `nogil` C 代码运行，零每次调用分配；原始字节扫描使用 AVX2/NEON/SSE2。如果没有该 wheel，纯 Python 回退实现会产生完全相同的结果。

## 将 SigMaker 作为库使用

除了作为 IDA 插件外，`sigmaker` 也可以直接作为 Python 库被其他工具导入（例如批量签名生成流水线）。核心类型可在任何 IDAPython 或 idalib 环境中使用：

```python
import sigmaker

cfg = sigmaker.SigMakerConfig(
    output_format=sigmaker.SignatureType.IDA,
    wildcard_operands=True,
    continue_outside_of_function=False,
    wildcard_optimized=True,
    ask_longer_signature=False,
)
result = sigmaker.SignatureMaker().make_signature(ea, cfg)
print(f"{result.signature:ida}")   # IDA 格式字符串
print(len(result.signature))       # 字节长度

# 交叉引用：
xrefs = sigmaker.XrefFinder().find_xrefs(ea, cfg)
for gen in xrefs.signatures:
    print(str(gen.address), f"{gen.signature:ida}")
```

### 稳定性契约

如果你嵌入使用 `sigmaker`，可以信赖以下保证。这些被视为契约条款，在对公共接口做任何更改前都会进行检查：

1. **仅追加的配置。** `SigMakerConfig` 字段永不会被重排或删除。新功能以带有安全默认值的新字段形式加入，现有构造代码继续正常工作。
2. **稳定的公共名称。** 以下名称及其文档化的属性不会被重命名或删除：`SignatureMaker`、`SigMakerConfig`、`SignatureType`（`IDA`、`x64Dbg`、`Mask`、`BitMask`）、`XrefFinder`、`GeneratedSignature`（`signature`、`address`、`status`、`match_count`）、`XrefGeneratedSignature`（`signatures`）、`Match`（`__str__` 返回十六进制地址）、`Signature`（`__len__`、`__format__`）、`GenerationPolicy`、`GenerationStatus`。
3. **稳定的方法签名。** `SignatureMaker.make_signature(ea, cfg, end=None, *, progress_reporter=None, policy=GenerationPolicy.strict())`、`XrefFinder.find_xrefs(ea, cfg)`、`XrefFinder.count_code_xrefs_to(ea)` 以及 `XrefFinder.iter_code_xrefs_to(ea)`。
4. **稳定的格式规范。** `f"{sig:ida}"`、`f"{sig:x64dbg}"`、`f"{sig:mask}"` 和 `f"{sig:bitmask}"` 始终精确产生当前输出。
5. **字节级别相同的默认值。** 生产环境默认值在优化过程中保持不变：未选择新标志的脚本将获得与之前版本字节级别相同的签名。

### 已被以下项目使用

基于或嵌入 `sigmaker` 库的项目：

- [mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp)，一个 AI 逆向工程 MCP 服务器（8900+ 星标），内置了精简的、仅引擎版本的 `sigmaker`，并通过 `SigMakerConfig`、`SignatureType`、`SignatureMaker().make_signature` 和 `XrefFinder().find_xrefs` 提供签名工具。
- [koyzdev/sigdrift](https://github.com/koyzdev/sigdrift) 是一个批量签名生成脚本，导入该库后调用 `SignatureMaker().make_signature(ea, SigMakerConfig(...))` 和 `XrefFinder()`，并通过 `f"{sig:ida}"` 和 `f"{sig:mask}"` 格式化结果。

正在基于 `sigmaker` 构建项目？请提交 PR 或 Issue，我会将其添加到这里。

## 致谢

感谢 [@A200K](https://github.com/A200K) 的 [IDA-Pro-SigMaker](https://github.com/A200K/IDA-Pro-SigMaker) 插件，它为本插件的初始移植提供了灵感和基础。同时感谢 [@kweatherman](https://github.com/kweatherman) 的 [sigmakerex](https://github.com/kweatherman/sigmakerex) 作为 SigMaker 生态中的独立先行工作。虽然初始移植并未借鉴 sigmakerex，但社区成员后来要求与其部分功能兼容和功能对等（例如参见 [issue #17](https://github.com/mahmoudimus/ida-sigmaker/issues/17)）。正如 [sigmakerex 的 README 致谢](https://github.com/kweatherman/sigmakerex#credits)中所记载的，SigMaker 有着悠久的作者和贡献者历史，在此一并感谢：

> 感谢始于 gamedeception.net 时代的原始 SigMaker 工具，直至当前 C/C++ 和 Python 迭代版本的所有作者：
> P4TR!CK、bobbysing、xero|hawk、ajkhoury、以及 zoomgod 等人。
>
> 感谢 Wojciech Mula 提供的 SIMD 编程资源。

## 开发与发布

### 贡献

1. Fork 本仓库
2. 创建功能分支
3. 进行修改
4. 充分测试
5. 提交 Pull Request

版本号只存在于一个地方：`src/sigmaker/__init__.py` 中的 `__version__`。为使 `ida-plugin.json` 自动与之保持同步，每次克隆后启用仓库的 git hook：

```bash
git config core.hooksPath .githooks
```

pre-commit 钩子（`.githooks/pre-commit`）会运行 `tools/sync_plugin_version.py`，将 `__version__` 复制到 `ida-plugin.json` 并暂存该文件，从而确保 IDA 插件仓库读取的清单不会落后于版本更新。CI 会运行相同的检查（`TestPluginManifestVersion`）作为未使用钩子的提交的后备保障。

## 联系方式

在 X（Twitter）上找我 [@mahmoudimus](https://x.com/mahmoudimus)，或通过 [mahmoudimus.com](https://mahmoudimus.com) 上的任一地址联系我。

# 更新日志

本插件的所有重要用户可见变更均记录在此。格式遵循 [Keep a Changelog](https://keepachangelog.com/)，项目遵循[语义化版本](https://semver.org/)。

## [1.12.0] - 2026-07-13

### 新增

- **多语言支持（中文 + 英文）。** 插件 UI 现在自动检测系统区域设置。中文系统显示翻译后的对话框、工具提示和消息；其他语言环境回退到英文。基于 Python 标准库 `gettext` 实现，零新增运行时依赖。

### 变更

- **发布格式改为 zip + 加载器。** 不再发布单个 `sigmaker.py`，改为 `sigmaker-*.zip`，内含 `sigmaker_loader.py`（放在 `plugins/` 目录供 IDA 加载）和 `sigmaker/` 子目录（包含插件代码、i18n 模块和翻译文件）。解压 zip 到 IDA 的 `plugins/` 目录即可。

- **版本号自动从 git 标签检测。** `__init__.py` 中的硬编码 `__version__` 已移除。包版本在构建时从最近的 `v*` git 标签派生；pip 安装的副本通过 `importlib.metadata` 运行时获取版本。

- **CI 工作流已为 i18n 和 setuptools-scm 更新。** 翻译 `.mo` 文件在 CI 期间编译。`SETUPTOOLS_SCM_PRETEND_VERSION` 传递给 Docker 容器和 cibuildwheel，确保无 git 二进制文件的构建环境中版本号正确。

### 内部

- 新增 `src/sigmaker/i18n.py` 模块，处理区域检测和 gettext 初始化。
- `ida-plugin.json` 入口点更新为 `sigmaker_loader.py`。
- `pyproject.toml` 的 package-data 新增 `*.mo` 和 `*.po`。
- `tools/sync_plugin_version.py` 改为从 `git describe` 读取版本号。

[1.12.0]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.11.0...v1.12.0

## [1.11.0] - 2026-07-05

### 新增

- **可选功能"将唯一性限制和搜索限定于所在程序段"。** 新增复选框，将签名创建和"搜索签名"操作的作用域限定于单个程序段（创建时以锚点所在段为范围，搜索时以光标所在段为范围），而非整个数据库。这使得你可以对跨程序段重复的函数（例如启动代码段和主代码段）进行签名，在没有整个数据库级唯一签名的情况下，在相同程序段内搜索该签名。默认关闭，现有行为不变。（[#64](https://github.com/mahmoudimus/ida-sigmaker/issues/64)、[#67](https://github.com/mahmoudimus/ida-sigmaker/pull/67)、[#70](https://github.com/mahmoudimus/ida-sigmaker/pull/70)）

### 修复

- **签名搜索在非连续程序段间报告正确地址。** SIMD 搜索将匹配项的缓冲区偏移映射为 `min_ea + offset`，这在程序段不连续时是错误的：加载在远端地址（如 `0x1F78000`）的额外二进制文件被报告在 `0x570000` 附近。现在通过记录的程序段映射将匹配项映射回真实地址。签名生成从未受影响（它使用函数地址，而非扫描缓冲区）。（[#68](https://github.com/mahmoudimus/ida-sigmaker/issues/68)、[#69](https://github.com/mahmoudimus/ida-sigmaker/pull/69)）

[1.11.0]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.10.0...v1.11.0

## [1.10.0] - 2026-07-03

### 修复

- **ARM Thumb 操作数现在可被通配。** 操作数通配功能之前只对 4 字节和 8 字节指令计算掩码大小，导致每条 16 位 Thumb-1 指令的通配长度为 0，从而完全保留为字面值（例如 `LDR R5, off_X` 这类 PC 相对字面量加载，其随构建变化的偏移字节未被通配）。现在 2 字节 Thumb 指令在保留操作码字节的同时会对偏移进行通配。（[#61](https://github.com/mahmoudimus/ida-sigmaker/issues/61)、[#62](https://github.com/mahmoudimus/ida-sigmaker/pull/62)）
- **ARM/Thumb 分支指令和 `ADRP` 的高字节偏移现已被完全掩码。** Thumb-2 的 `BL`/`BLX`、长 `B` 以及 AArch64 的 `ADRP` 将偏移位放置在操作码的高字节中；仅对低字节进行掩码会使这些位保持字面量，导致签名可能无法匹配其他构建版本（报告者观察到偏移半字节从 `FF` 变为 `F8`）。这些指令现在对整个指令进行通配。（[#61](https://github.com/mahmoudimus/ida-sigmaker/issues/61)、[#65](https://github.com/mahmoudimus/ida-sigmaker/pull/65)）

### 变更

- **ARM 操作数通配现已考虑地址属性并由操作数对话框驱动。** 默认行为现在仅通配地址相关的操作数（内存引用、位移量、立即数和分支目标），并通过 IDA 的偏移标志进行细化，使得真实地址（`ADRP #x@PAGE`、`LDR #x@PAGEOFF`）被掩码，而裸常量（`#0x40`）和栈槽（`[SP,#var]`）保持精确。对于寄存器在不同构建版本之间会发生变化的场景，请在"配置操作数通配"对话框中启用"通用寄存器"和/或"寄存器列表"。（[#65](https://github.com/mahmoudimus/ida-sigmaker/pull/65)）

[1.10.0]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.9.2...v1.10.0

## [1.9.2] - 2026-06-19

### 修复

- **取消 XREF 签名生成现在会停止 XREF 循环并保留已完成结果。** 如果在生成某个 xref 签名时触发了取消操作，`UserCanceledError` 之前会被当作普通的候选失败捕获，然后循环继续处理下一个 xref。现在 XREF 生成会立即停止，并打印至此找到的完整 xref 签名。此改动不影响 SIMD 加速路径。（[#55](https://github.com/mahmoudimus/ida-sigmaker/issues/55)、[#56](https://github.com/mahmoudimus/ida-sigmaker/pull/56)）

[1.9.2]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.9.1...v1.9.2

## [1.9.1] - 2026-05-30

### 新增

- **签名输出现在用所属函数名标注地址。** `GeneratedSignature.display`、`XrefGeneratedSignature.display` 以及函数签名操作会在打印的地址后附加 ` (函数名)`，前提是该地址位于已命名的函数内，否则仅输出原始地址。地址始终保留，因此同一函数内不同锚点的签名仍可区分。（[#47](https://github.com/mahmoudimus/ida-sigmaker/pull/47)）

[1.9.1]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.9.0...v1.9.1

## [1.9.0] - 2026-05-30

### 变更

- **在大型数据库上，"为当前函数查找最短唯一签名"的最坏情况从约 12 秒降至约 1 秒。** 对 200 MB+ 模块的性能分析发现，剩余开销并非来自索引或精炼内核，而是两个遗留问题，现已修复：种子候选映射在纯 Python 循环中遍历整个种子桶，以及种子化前缀全为通配符的模式回退到全缓冲区扫描。（[#45](https://github.com/mahmoudimus/ida-sigmaker/pull/45)）

### 内部

- 新的 `seed_offsets` Cython 内核在 `nogil` 下将种子桶映射到候选起始数组（`p - s` 偏移、适配守卫、n-1 边界），模式与 `refine_offsets` 相同。这是最后一个留在 Python 中的 `O(C0)` 循环；将其移至 C 语言后，最坏函数搜索从约 12 秒降至约 1 秒。（[#45](https://github.com/mahmoudimus/ida-sigmaker/pull/45)）
- 全通配前缀的种子化被推迟，不再在无比对字节可索引时执行 `O(N)` 掩码扫描。（[#45](https://github.com/mahmoudimus/ida-sigmaker/pull/45)）
- 对抗性精炼微基准测试（`tests/perf/adversarial_refine.py`，含 `--check` 回归守卫）以及交叉校验测试，将 Cython 内核锚定到其 Python 回退版本。块精炼和排序桶间隔种子交集已被测量并搁置。（[#45](https://github.com/mahmoudimus/ida-sigmaker/pull/45)）
- 生成的签名与 1.8.0 字节级别一致；仅查找速度发生变化。（[#45](https://github.com/mahmoudimus/ida-sigmaker/pull/45)）

### 文档

- `ALGORITHM.md` 新增了目录、"被拒绝的优化"章节（解释上述两个升级被搁置的原因），以及关于 `seed_offsets` 内核和推迟种子化的说明。（[#45](https://github.com/mahmoudimus/ida-sigmaker/pull/45)）

[1.9.0]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.8.0...v1.9.0

## [1.8.0] - 2026-05-29

### 变更

- **在大型数据库上，"为当前函数查找最短唯一签名"再次提速，且差距随数据库增长而扩大。** 每个起始点的种子扫描被替换为每次搜索只构建一次的双字节位置索引，因此每个起始点从其模式中最稀有的字节序列中获取种子，所需时间与该序列的频率成正比，而非与数据库大小成正比。在 16 MB 模块上，相对于 1.7.3 版本提升约 2.48 倍。（[#35](https://github.com/mahmoudimus/ida-sigmaker/pull/35)）
- **现在从最具选择性的序列中选择种子，支持 1 字节或 2 字节。** 单个稀有字节可能比常见的双字节对更具选择性，因此搜索会选择索引桶最小的序列。（[#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36)）

### 内部

- 在 Cython `_speedups` 扩展中以 `nogil` 计数排序方式构建双字节桶位置索引；1 字节桶可免费从中获得（作为范围视图，无需第二个索引）。（[#35](https://github.com/mahmoudimus/ida-sigmaker/pull/35)、[#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36)）
- 每字节候选精炼移至 Cython 扩展（`refine_offsets`）：在类型化 uint32 缓冲区上进行零分配、`nogil` 原地压缩。16 MB 模块最大函数的精炼时间从约 14 秒降至约 0.28 秒；该函数的搜索总时间从约 24 秒降至约 15.6 秒。（[#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36)）
- `_ByteIndex` 是一个 frozen slots dataclass；运行时数组模块被别名为 `py_stdlib_arr_mod`，以区别于 cimport 的 C 级 API。（[#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36)）
- 生成的签名与 1.7.3 字节级别一致；仅查找速度发生变化。（[#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36)）

### 文档

- 新增 [`ALGORITHM.md`](./ALGORITHM.md)，推导了匹配集数学原理、计数排序索引、选择性证明以及该方法的创新点。README 新增目录、含基准测试的"性能"章节，以及面向下游嵌入者的库稳定性契约。（[#36](https://github.com/mahmoudimus/ida-sigmaker/pull/36)）

[1.8.0]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.7.3...v1.8.0

## [1.7.3] - 2026-05-28

### 变更

- **在大型数据库上，"为当前函数查找最短唯一签名"大幅提速。** 搜索现在为每个起始点扫描一次数据库以获取候选匹配偏移集合，然后随着签名增长在内存中精炼该集合，不再每字节重新扫描整个数据库。之前需要数分钟的函数现在数秒即可完成。（[#33](https://github.com/mahmoudimus/ida-sigmaker/pull/33)）
- **实时 `Matches:`（匹配数）计数已恢复且精确。** 候选精炼在每个步骤免费跟踪存活的匹配数，因此"创建唯一签名"等待框再次显示真实计数，函数搜索等待框显示精确的内部计数，而非临时的 `2+` 占位符。（[#27](https://github.com/mahmoudimus/ida-sigmaker/issues/27)、[#33](https://github.com/mahmoudimus/ida-sigmaker/pull/33)）

### 修复

- **"开始性能分析"/"停止性能分析"菜单项现在会显示。** 它们之前是在插件初始化时附加的，此时 IDA 尚未构建菜单，因此静默地从未显示。现在它们通过反汇编右键弹出菜单附加，与主操作一起归入 `SigMaker` 子菜单。（[#33](https://github.com/mahmoudimus/ida-sigmaker/pull/33)）

### 内部

- 新增 `SignatureSearcher.find_all_offsets`（种子扫描返回原始缓冲区偏移）和 `_refine_offsets`（内存中候选精炼）。`MIN_USEFUL_SIG_BYTES` 以下的唯一性检查使用低成本提前退出探测，因此枚举性种子扫描被推迟到模式足够长、具备选择性之后才进行。（[#33](https://github.com/mahmoudimus/ida-sigmaker/pull/33)）
- 扫描循环中的取消轮询已被限流（每 65536 个匹配一次），以避免 `idaapi.user_cancelled()`（它会泵送 UI 事件循环）在常见模式的扫描中占据主导地位。（[#33](https://github.com/mahmoudimus/ida-sigmaker/pull/33)）
- 生成的签名与 1.7.2 字节级别一致；变更仅在于查找速度的提升以及精确匹配计数的恢复。（[#33](https://github.com/mahmoudimus/ida-sigmaker/pull/33)）

[1.7.3]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.7.2...v1.7.3

## [1.7.2] - 2026-05-28

### 新增

- **"创建唯一签名"和"为当前函数查找最短唯一签名"操作的实时等待框进度。** 等待框随搜索运行而更新：显示当前签名长度和已用时间（两者皆有），以及函数边界、当前锚点、内部搜索边界、最佳大小和候选计数（函数搜索特有）。（[#27](https://github.com/mahmoudimus/ida-sigmaker/issues/27)、[#30](https://github.com/mahmoudimus/ida-sigmaker/pull/30)）
- **自描述等待框。** 每个操作的等待框现在以操作名称和一行说明开头，提示正在执行的操作，因此截图总能识别出是哪个操作产生的。（[#30](https://github.com/mahmoudimus/ida-sigmaker/pull/30)）
- **`start_profiling` / `stop_profiling` 辅助函数**，作为 `Edit/Plugins` 菜单操作暴露，用于在 IDA 内部捕获慢速运行的 cProfile 转储。（[#30](https://github.com/mahmoudimus/ida-sigmaker/pull/30)）

### 变更

- **"为当前函数查找最短唯一签名"大幅提速。** 唯一性检查现在在找到第二个匹配时即停止，而非枚举数据库中的每一个匹配；段缓冲区每搜索加载一次，而非每增长步骤一次。在大型数据库上之前需要数分钟的函数搜索现在数秒即可完成。（[#31](https://github.com/mahmoudimus/ida-sigmaker/pull/31)）
- **等待框刷新限流默认值现为 1 秒**（之前为 100 毫秒），避免框的刷新速度快于用户的阅读速度。（[#27](https://github.com/mahmoudimus/ida-sigmaker/issues/27)、[#30](https://github.com/mahmoudimus/ida-sigmaker/pull/30)）

### 移除

- **"创建唯一签名"等待框中的实时 `Matches:`（匹配数）计数暂时移除。** 在每个增长步骤计数所有匹配成为搜索的瓶颈；等待框仍显示增长中的长度和已用时间。未来版本将通过增量候选精炼以低成本恢复精确计数。（[#27](https://github.com/mahmoudimus/ida-sigmaker/issues/27)、[#30](https://github.com/mahmoudimus/ida-sigmaker/pull/30)）

### 内部

- `MinimalFunctionSignatureGenerator` 现在一次性预先解码函数每条指令，然后在缓存数据上增长锚点，而非每个锚点重新解码一次。（[#31](https://github.com/mahmoudimus/ida-sigmaker/pull/31)）
- `SignatureSearcher.is_unique` 在找到第二个匹配时即停止；`count_matches` 仍完整枚举，供需要精确计数的调用者使用（如取消时部分输出）。（[#31](https://github.com/mahmoudimus/ida-sigmaker/pull/31)）
- 编译后的 `_speedups` SIMD 扩展现在从兄弟目录加载，当包级导入解析为命名空间包且没有匹配的编译构建时（开发和符号链接布局）。（[#31](https://github.com/mahmoudimus/ida-sigmaker/pull/31)）

[1.7.2]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.7.1...v1.7.2

## [1.7.1] - 2026-05-27

### 新增

- **主表单上新增"为当前函数查找最短唯一签名"操作。** 遍历包含函数中的每条指令作为可能的起始点，从每个起始点增长签名（受函数边界和当前最佳候选大小约束），返回具有最少通配符的最短唯一结果。输出使用函数内偏移标注地址，让你能准确看到唯一序列的位置。（[#17](https://github.com/mahmoudimus/ida-sigmaker/issues/17)、[#26](https://github.com/mahmoudimus/ida-sigmaker/pull/26)）
- **新操作的自动 xref 回退。** 如果函数体内不存在唯一签名（例如函数是一个与许多其他函数相同的小型 thunk），操作会回退到生成以每个指向该函数的代码 xref 为根的签名，并选择最佳结果。输出格式为 `Xref signature into 0x... (from 0x...):`。（[#17](https://github.com/mahmoudimus/ida-sigmaker/issues/17)、[#26](https://github.com/mahmoudimus/ida-sigmaker/pull/26)）

### 变更

- **`WildcardPolicy.for_x86()` 不再通配 `o_imm` 立即数。** 像 `mov rcx, 0x13371338` 中的 `0x13371338` 是嵌入指令编码的字面量值，不会在二进制构建版本之间发生变化，因此通配它只会移除本可使签名唯一的字节。内存地址（`o_mem`）、跳转/调用目标（`o_far`、`o_near`）和架构特定的寄存器操作数仍会被通配。对于所有 `wildcard_operands=True` 的操作（包括现有的"创建唯一签名"和"查找最短 XREF 签名"操作），这都是一项严格改进。（[#26](https://github.com/mahmoudimus/ida-sigmaker/pull/26)）
- **`GeneratedSignature.__lt__` 现在按 `(size, wildcards)` 升序排序**，而非仅按大小排序。相同长度下通配符更少的签名排序更靠前。现有的"查找最短 XREF 签名"操作可免费受益，选择更具体的候选作为"最佳"结果。（[#26](https://github.com/mahmoudimus/ida-sigmaker/pull/26)）
- **README 致谢**已澄清，以更好地反映本插件与更广泛的 SigMaker 生态之间的历史关系。

### 内部

- 新增 `MinimalFunctionSignatureGenerator` 类，实现了带单调最佳大小剪枝和理想候选提前退出（大小 <= 5 字节且零通配符时停止外层循环）的函数级搜索。
- 新增 `Action.FIND_FUNCTION_SIG = 4` 枚举值，用于新的表单操作。
- 集成测试覆盖了函数搜索的端到端流程，以及针对编译测试二进制文件的 x86 立即数保留功能。

[1.7.1]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.7.0...v1.7.1

## [1.7.0] - 2026-05-27

### 新增

- **长签名生成操作可取消的等待框。** 当 sigmaker 搜索时，现在会显示一个非阻塞等待框，内含取消按钮，可随时单击以干净地停止搜索。取代了之前反复弹出的"继续？"模态对话框。取消操作会在输出日志中生成清晰的 `Operation canceled by user` 消息，不带回溯信息。（[#18](https://github.com/mahmoudimus/ida-sigmaker/issues/18)、[#24](https://github.com/mahmoudimus/ida-sigmaker/pull/24)）
- **主表单上的可选"启用继续提示"复选框。** 勾选后可恢复先前的定期提示行为，供需要此功能的用户使用。默认关闭。（[#24](https://github.com/mahmoudimus/ida-sigmaker/pull/24)）
- **"其他选项..."对话框中的可选"提示间隔"字段。** 设置首次定期提示触发前的等待秒数；`-1` 表示完全禁用提示。默认值为 `-1`。（[#24](https://github.com/mahmoudimus/ida-sigmaker/pull/24)）
- **主表单上的可选"取消时输出部分签名"复选框。** 勾选后，取消唯一签名搜索时会输出包含匹配计数的部分签名，而非不输出任何内容。默认关闭；输出仅发送到控制台（不写入剪贴板），以防止意外取消破坏剪贴板内容。（[#22](https://github.com/mahmoudimus/ida-sigmaker/issues/22)、[#25](https://github.com/mahmoudimus/ida-sigmaker/pull/25)）

### 变更

- **默认取消用户体验。** 开箱即用，sigmaker 搜索现在显示带取消按钮的等待框，而非触发定期的"继续？"弹窗。弹窗行为作为上述可选功能保留。（[#18](https://github.com/mahmoudimus/ida-sigmaker/issues/18)、[#24](https://github.com/mahmoudimus/ida-sigmaker/pull/24)）

### 修复

- **取消唯一签名搜索不再误报为"Signature not unique"。** `InstructionWalker` 现在在取消时抛出正确的 `UserCanceledError`，而非将其吞没为 `StopIteration`（生成器曾将其视为"指令耗尽"）。用户现在看到的是 `Operation canceled by user`，而非令人困惑的错误信息。（[#18](https://github.com/mahmoudimus/ida-sigmaker/issues/18)、[#24](https://github.com/mahmoudimus/ida-sigmaker/pull/24)）
- **等待框的取消按钮现在真正生效。** `CheckContinuePrompt.should_cancel` 现在轮询 `idaapi_user_canceled()`，因此等待框的取消按钮通过进度报告器传播，无论是否启用了定期提示。之前该按钮实际上是无操作的，除非被关闭的是模态弹窗本身。（[#18](https://github.com/mahmoudimus/ida-sigmaker/issues/18)、[#24](https://github.com/mahmoudimus/ida-sigmaker/pull/24)）
- **面向用户的取消消息现在与代码库其他部分一致。** 取消时的输出行为 `Operation canceled by user`（美式英语），与插件其他各处的拼写保持一致。
- **取消时部分输出的匹配计数不再显示 `0`。** 当用户在搜索过程中点击取消时，内部匹配计数也会退出（它轮询相同的取消标志），并返回部分计数 `0`。生成器现在改为保留最近完成的迭代的计数，因此用户看到的是 `Partial signature (NOT unique, 3 matches)` 而非 `0 matches` 或 `match count unavailable`。（[#22](https://github.com/mahmoudimus/ida-sigmaker/issues/22)、[#25](https://github.com/mahmoudimus/ida-sigmaker/pull/25)）

### 内部

- 新增 `Action` IntEnum 枚举，替换 `SigMakerPlugin.run` 分发中的裸 `0/1/2/3` 魔数。
- 新增 `GenerationStatus` 枚举和 `GenerationPolicy` 数据类，规范化取消时部分输出的可选行为。
- `GeneratedSignature` 现在携带 `status` 和 `match_count` 字段。
- `SignatureSearcher.count_matches` 公开了 `is_unique` 已计算但丢弃的每次迭代数据库扫描计数。
- `InstructionWalker.end_ea` 默认值通过 `default_factory` 延迟解析，使得对 `idaapi.BADADDR` 的运行时补丁生效（可测试性修复）。

[1.7.0]: https://github.com/mahmoudimus/ida-sigmaker/compare/v1.6.0...v1.7.0

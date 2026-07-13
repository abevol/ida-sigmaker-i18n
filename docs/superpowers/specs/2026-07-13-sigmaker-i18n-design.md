# Sigmaker 国际化设计

## 概述

为 IDA Sigmaker 插件（`src/sigmaker/__init__.py`）添加运行时国际化支持，目标语言为中文和英文。使用 Python stdlib `gettext`，零新增外部依赖。

## 架构

```
src/sigmaker/
├── __init__.py      # 修改：导入 _()，包裹用户可见字符串
├── i18n.py          # 新增：gettext 初始化 + _() 导出
├── _speedups/       # 不变
└── locale/          # 新增
    ├── sigmaker.pot
    ├── en/LC_MESSAGES/sigmaker.po
    └── zh_CN/LC_MESSAGES/sigmaker.po
```

## locale 检测（i18n.py）

模块加载时调用 `locale.getdefaultlocale()` 检测系统语言：

1. `zh_CN` / `zh` → 加载中文翻译
2. 其他 / 失败 → 降级英文（`NullTranslations`）

`gettext.translation(fallback=True)` 确保 `.mo` 文件缺失时静默降级，不抛异常。

## 短 Key 国际化策略（v2）

v1 使用英文原文作为 `_()` 的 msgid，导致 Form 模板中的 IDA 语法（`<Label:{Control}>`）混入翻译键，翻译人员无法理解，改 Form 结构就需改 .po。

v2 改为纯短 Key 方案：所有 `_()` 调用使用 `"form.main.title"` 风格的短标识符，翻译文本与 UI 结构彻底分离。

### 内建英文字典

`i18n.py` 新增 `_EN` 字典，作为 `.mo` 缺失时的英文字跳：

```python
_EN = {
    "ok": "OK",
    "cancel": "Cancel",
    "form.main.select_action": "Select action",
    "msg.no_xrefs": "No XREFs have been found for your address",
    # ~80 keys
}

def t(key: str) -> str:
    r = _catalog.gettext(key)
    return r if r != key else _EN.get(key, key)
```

`_catalog` 是 gettext 的翻译目录，由 `i18n.py` 初始化。`.mo` 找不到时用 `_EN` 兜底，`.mo` 找不到且 `_EN` 也没有时返回 key 本身（便于调试）。

### Form 模板构建

每个 Form 类使用 `_T()` 辅助函数将翻译片段拼接到模板中。`_T()` 做 `str.replace("{name}", value)` 替换，用 `{{name}}` 双花括号保留 IDA Form 的 `{ControlName}`。

```python
def _T(template: str, **kwargs: str) -> str:
    for k, v in kwargs.items():
        template = template.replace("{" + k + "}", v)
    return template
```

Form 模板中的 IDA 控制引用用 `{{...}}` 双花括号：

```python
class ConfigureOptionsForm(idaapi.Form):
    _TEMPLATE = _T(
        "BUTTON YES* OK\n"
        "BUTTON CANCEL Cancel\n"
        "{title}\n\n"
        "<#{top_x_tt}#{top_x}     :{{opt1}}>\n"
        "<#{max_single_tt}#{max_single} :{{opt2}}>\n"
        ...
        title=_("options.title"),
        top_x_tt=_("options.top_x_tt"),
        top_x=_("options.top_x"),
        ...
    )
```

翻译人员只需提供每个 key 对应的本地化文本，完全不需要理解 IDA Form 语法。

### Key 命名规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `ok`, `cancel`, `continue` | 通用短文本 | `_("cancel")` |
| `form.main.*` | 主对话框 | `form.main.select_action` |
| `form.options.*` | 选项对话框 | `form.options.prompt_interval` |
| `form.operand.*` | 操作数通配对话框 | `form.operand.trace_reg` |
| `progress.*` | 进度对话框 | `progress.unique_sig` |
| `msg.*` | 输出消息 | `msg.no_xrefs` |
| `action.*` | 右键菜单 | `action.sigmaker` |
| `plugin.*` | 插件元信息 | `plugin.help` |

### .po 文件

只包含 key→翻译的映射：

```po
msgid "form.main.select_action"
msgstr "选择操作"

msgid "form.operand.general_reg"
msgstr "通用寄存器（al, ax, es, ds...）"
```

永不在 .po 中出现 IDA Form 语法。

### 工具链

`tools/i18n_update.py` 改为从 `_EN` 字典生成 `.pot`，通过 key 查找替代 AST 遍历。

## 翻译范围

### 翻译

约 80 个短 Key，每个 key 对应一句独立的用户可见文本。

### 不翻译

- IDA Form 控制引用（`{opt1}`, `{FormChangeCb}`, `{rAction}` 等）
- hex 地址/字节值
- logging 调试消息
- 异常 traceback
- 代码标识符、枚举名

### 文档翻译

- `README.zh_CN.md` → `README.md` 的中文版
- `CHANGELOG.zh_CN.md` → `CHANGELOG.md` 的中文版
- `ALGORITHM.zh_CN.md` → `ALGORITHM.md` 的中文版

## 测试

`tests/test_i18n.py`：验证英文字典查找、.mo 翻译覆盖、降级行为。

## 未完成项（超出当前范围）

- Git commit 消息翻译
- CI 自动化 `.mo` 验证（可后续添加）
- Poedit / Crowdin 集成（可后续添加）

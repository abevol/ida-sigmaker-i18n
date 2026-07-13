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

## Form 模板国际化策略

`idaapi.Form` 使用 `{ControlName}` 语法，与 Python `str.format()` 冲突。解决：

- 模板中人类可读文本 → `_()` 包裹
- 模板中 Python 动态值（如版本号）→ `%(name)s` 风格，翻译后用 `%` 格式化
- `{ControlName}` 控制引用 → 保留原样

例：

```python
class SignatureMakerForm(idaapi.Form):
    _TEMPLATE = _(
        "STARTITEM 0\n"
        "BUTTON YES* OK\n"
        "BUTTON CANCEL Cancel\n"
        "%(title)s\n"
        "{FormChangeCb}\n"
        "Select action:\n"
        ...
    )
    def __init__(self):
        simd = "(SIMD ENABLED)" if SIMD_SPEEDUP_AVAILABLE else "(NO SIMD SPEEDUP)"
        form_text = self._TEMPLATE % {"title": f"{PLUGIN_NAME} v{PLUGIN_VERSION} {simd}"}
```

## 翻译范围

### 翻译

| 类别 | 条数 | 说明 |
|------|------|------|
| Form 标签/按钮 | ~15 | OK、Cancel、选项标签 |
| Form 工具提示 | ~15 | `#...` 注释 |
| Progress 对话框 | ~8 | wait-box 消息 |
| `idaapi.msg()` 输出 | ~12 | 结果提示、错误消息 |
| Action 菜单文本 | ~3 | 右键菜单项 |
| 用户交互提示 | ~5 | `ask_str`、`ask_addr` 参数 |

### 不翻译

- hex 地址/字节值
- logging 调试消息
- 异常 traceback
- 代码标识符、枚举名
- IDA Form 控制引用（`{FormChangeCb}` 等）

### 文档翻译

- `README.zh_CN.md` → `README.md` 的中文版
- `CHANGELOG.zh_CN.md` → `CHANGELOG.md` 的中文版
- `ALGORITHM.zh_CN.md` → `ALGORITHM.md` 的中文版

## 工具链

`tools/i18n_update.py`：用 `ast` 遍历源码提取 `_()` 调用，更新 `.pot`，合并 `.po`，编译 `.mo`。

```bash
python tools/i18n_update.py           # 完整流程
python tools/i18n_update.py --compile # 仅编译 .mo
```

## 测试

`tests/test_i18n.py`：验证 locale 检测、翻译查找、降级行为。

## 未完成项（超出当前范围）

- Git commit 消息翻译
- CI 自动化 `.mo` 验证（可后续添加）
- Poedit / Crowdin 集成（可后续添加）

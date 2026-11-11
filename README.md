# nonebot-plugin-fishmenu 🐟

> `/菜单` 出一条指令菜单：默认纯文字，`FISHMENU_IMAGE=true` 时渲染成 PNG 卡片。
> **超管命令自动对普通用户隐藏**。零 LLM 开销。

从跑了半年的 QQ 机器人（[肥鱼人设](https://github.com/173ababah)）里拆出来的菜单模块。

## 用法

```
/菜单            → 文字菜单
/菜单 图         → 强制出 PNG（这次只看）
```

`.env`：

```ini
FISHMENU_TITLE=指令菜单
FISHMENU_SUBTITLE=点菜单上的命令就能用
FISHMENU_FOOT=有问题直接问我就行
FISHMENU_IMAGE=false          # true = 每次出图（需要 pillow）
FISHMENU_WIDTH=760
FISHMENU_MASK_ADMIN=true      # 普通用户看不到带 # 的超管命令
FISHMENU_ITEMS=["/画图|让我画一张","/图库|翻我画过的图","/重置#|清空状态 超管"]
```

## 条目格式

```
命令|说明        ← 竖线分隔，中文输入法里好打
命令#|说明       ← 结尾 # 或说明里写「超管」= 只给超管看
```

为什么不用 JSON：手写 `.env` 时一行一条最省事，改动也不用数括号。

## 三个设计选择

1. **PNG 是可选的、能失败**：没装 pillow、找不到中文字体时 `render_png()` 返回 `None`，
   调用方直接退回文字 —— 菜单这种"随时要看"的东西不能因为渲染挂掉。
2. **排版先算再画**：`layout()` 先给出画布尺寸，`render_png()` 照着画，
   避免"画到一半发现高度不够"。
3. **对齐在文字版也做**：命令列按最长的那条 `ljust`，说明列才整齐（手机上看尤其明显）。

## 测试

```bash
python -m pytest tests -q     # 9 passed
```

覆盖：条目解析（含空行/无说明/只有说明的垃圾行）、超管识别三种写法、
按身份过滤、`#`/`admin` 清理、文字对齐、空菜单、画布尺寸、PNG 可选路径。

## License

MIT

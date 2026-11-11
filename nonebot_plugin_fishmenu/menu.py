"""菜单条目的解析 / 排版 / 渲染（纯函数，PNG 那步 pillow 可选）。

条目格式就两种：

```
📮 直接 @我|或者私聊，都能聊      ← 「标题|说明」
/画图                            ← 只有命令
```

为什么不用 JSON：手写 `.env` 时一行一条最省事，竖线在中文输入法里也好打。
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Sequence, Tuple

ADMIN_MARK = ("admin", "superuser", "超管", "#")


def parse_items(items: Iterable[str]) -> List[Dict[str, str]]:
    """`["/画图|让我画一张", "/图库"]` → `[{cmd, desc}]`。空行/空命令丢掉。"""
    out: List[Dict[str, str]] = []
    for raw in items or []:
        s = str(raw or "").strip()
        if not s:
            continue
        cmd, _, desc = s.partition("|")
        cmd, desc = cmd.strip(), desc.strip()
        if not cmd:
            continue
        out.append({"cmd": cmd, "desc": desc})
    return out


def is_admin(item: Dict[str, str]) -> bool:
    """条目里带 `#` 前缀或说明里写 `admin` 就当作超管命令。"""
    cmd = str(item.get("cmd") or "")
    if cmd.endswith("#") or cmd.startswith("#"):
        return True
    return any(m in str(item.get("desc") or "").lower() for m in ADMIN_MARK)


def visible(items: Sequence[Dict[str, str]], *, admin: bool = False,
            mask_admin: bool = True) -> List[Dict[str, str]]:
    """按身份过滤：普通用户看不到超管命令；`mask_admin=False` 则都显示。"""
    if admin or not mask_admin:
        return [dict(it) for it in items]
    return [dict(it) for it in items if not is_admin(it)]


def clean(items: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    """去掉显示用的 `#` 标记。"""
    out = []
    for it in items:
        cmd = str(it.get("cmd") or "").replace("#", "").strip()
        desc = re.sub(r"\b(admin|superuser|超管)\b", "", str(it.get("desc") or ""),
                      flags=re.I).strip(" ，,")
        out.append({"cmd": cmd, "desc": desc})
    return out


def text_menu(items: Sequence[Dict[str, str]], *, title: str = "指令菜单",
              subtitle: str = "", foot: str = "") -> str:
    """文字版菜单：命令左对齐成一列，说明跟在后面。"""
    rows = clean(items)
    if not rows:
        return title
    width = max(len(r["cmd"]) for r in rows)
    lines: List[str] = []
    if title:
        lines.append(title + (("·" + subtitle) if subtitle else ""))
    for r in rows:
        if r["desc"]:
            lines.append("%s  %s" % (r["cmd"].ljust(width), r["desc"]))
        else:
            lines.append(r["cmd"])
    if foot:
        lines.append(foot)
    return "\n".join(lines)


def layout(items: Sequence[Dict[str, str]], *, width: int = 760, pad: int = 28,
           line_h: int = 44) -> Dict[str, int]:
    """算 PNG 画布尺寸（渲染前就知道要多大，避免二次排版）。"""
    rows = clean(items)
    h = pad * 2 + 56 + line_h * max(1, len(rows))
    return {"w": max(320, int(width)), "h": int(h), "rows": len(rows)}


def render_png(items: Sequence[Dict[str, str]], *, title: str = "指令菜单",
               subtitle: str = "", foot: str = "", width: int = 760,
               bg=(24, 26, 30), fg=(232, 236, 240), sub=(150, 158, 168),
               accent=(90, 160, 250), font_path: str = "") -> bytes | None:
    """渲染成 PNG。**没有 pillow 或字体都失败时返回 None**，调用方退回文字。"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None

    rows = clean(items)
    box = layout(rows, width=width)
    try:
        img = Image.new("RGB", (box["w"], box["h"]), bg)
    except Exception:
        return None
    d = ImageDraw.Draw(img)

    def font(size: int):
        for cand in (font_path, "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            try:
                if cand:
                    return ImageFont.truetype(cand, size)
            except Exception:
                continue
        return ImageFont.load_default()

    pad, y = 28, 24
    d.text((pad, y), title, font=font(30), fill=fg)
    y += 50
    if subtitle:
        d.text((pad, y), subtitle, font=font(18), fill=sub)
        y += 28
    for r in rows:
        d.text((pad, y), r["cmd"], font=font(22), fill=accent)
        if r["desc"]:
            d.text((pad + 190, y + 2), r["desc"], font=font(19), fill=sub)
        y += 44
    if foot:
        d.text((pad, y + 6), foot, font=font(17), fill=sub)
    import io
    buf = io.BytesIO()
    try:
        img.save(buf, "PNG")
    except Exception:
        return None
    return buf.getvalue()

"""nonebot-plugin-fishmenu —— 指令菜单。

`/菜单` 或 `/menu` 出一条菜单（文字，或 `FISHMENU_IMAGE=true` 时渲染成 PNG）。
超管能看到带 `#` 的条目，普通用户自动看不到（`FISHMENU_MASK_ADMIN`）。
"""

from __future__ import annotations

from nonebot import get_plugin_config, on_command
from nonebot.adapters import Event, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from . import menu
from .config import MenuConfig

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-fishmenu",
    description="指令菜单：把各插件命令拼成一张卡（文字/PNG），支持按身份过滤",
    usage="/菜单",
    type="application",
    config=MenuConfig,
    homepage="https://github.com/173ababah/nonebot-plugin-fishmenu",
    supported_adapters={"~onebot.v11"},
)

cfg = get_plugin_config(MenuConfig)

menu_cmd = on_command("菜单", aliases={"menu", "help", "指令"}, priority=14, block=True)


@menu_cmd.handle()
async def _(event: Event, arg: Message = CommandArg()):
    if not cfg.fishmenu_enabled:
        await menu_cmd.finish("菜单关着呢（FISHMENU_ENABLED=false）")

    admin = False
    try:
        from nonebot.matcher import current_bot
        admin = await SUPERUSER(current_bot.get(), event)
    except Exception:
        admin = False

    items = menu.parse_items(cfg.fishmenu_items)
    shown = menu.visible(items, admin=bool(admin), mask_admin=cfg.fishmenu_mask_admin)

    want_png = str(arg.extract_plain_text()).strip() in ("图", "img", "png")
    if cfg.fishmenu_image or want_png:
        raw = menu.render_png(shown, title=cfg.fishmenu_title, subtitle=cfg.fishmenu_subtitle,
                              foot=cfg.fishmenu_foot, width=cfg.fishmenu_width)
        if raw:
            from nonebot.adapters.onebot.v11 import MessageSegment
            await menu_cmd.finish(MessageSegment.image(raw))
    await menu_cmd.finish(menu.text_menu(shown, title=cfg.fishmenu_title,
                                         subtitle=cfg.fishmenu_subtitle, foot=cfg.fishmenu_foot))

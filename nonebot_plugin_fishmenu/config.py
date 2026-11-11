"""配置（.env 前缀 FISHMENU_）。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MenuConfig(BaseModel):
    fishmenu_enabled: bool = Field(default=True, description="总开关")
    fishmenu_title: str = Field(default="指令菜单", description="卡片标题")
    fishmenu_subtitle: str = Field(default="", description="副标题（可空）")
    fishmenu_foot: str = Field(default="", description="页脚（可空）")
    fishmenu_items: list = Field(
        default=[
            "📮 直接 @我|或者私聊，都能聊",
            "/画图|让我画一张",
            "/图库|翻我画过的图",
            "/好感度|看你在我这儿的分量",
            "/coin|鲸圆券（打工 / 签到 / 排行）",
            "/记忆|看我记得你什么",
        ],
        description="菜单条目：`命令|说明`，一行一条")
    fishmenu_image: bool = Field(default=False, description="是否渲染成 PNG（需要 pillow，缺了自动退回文字）")
    fishmenu_width: int = Field(default=760, description="PNG 宽度")
    fishmenu_mask_admin: bool = Field(default=True, description="是否按权限隐藏超管命令")

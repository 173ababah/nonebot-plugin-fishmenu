"""菜单解析/排版/渲染的单元测试。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nonebot_plugin_fishmenu"))

import menu  # noqa: E402


def test_parse_items_basic():
    items = menu.parse_items(["/画图|让我画一张", "/图库", "  ", "/coin|鲸圆券"])
    assert items[0] == {"cmd": "/画图", "desc": "让我画一张"}
    assert items[1] == {"cmd": "/图库", "desc": ""}
    assert len(items) == 3


def test_parse_ignores_junk():
    assert menu.parse_items(["|只有说明", "", None]) == []


def test_admin_detection():
    assert menu.is_admin({"cmd": "/重置#", "desc": ""})
    assert menu.is_admin({"cmd": "#后台", "desc": ""})
    assert menu.is_admin({"cmd": "/x", "desc": "超管专用"})
    assert not menu.is_admin({"cmd": "/画图", "desc": "让我画一张"})


def test_visible_masks_admin():
    items = menu.parse_items(["/画图|画画", "/重置#|清空"])
    assert [i["cmd"] for i in menu.visible(items, admin=False)] == ["/画图"]
    assert len(menu.visible(items, admin=True)) == 2
    assert len(menu.visible(items, admin=False, mask_admin=False)) == 2


def test_clean_strips_marks():
    items = menu.parse_items(["/重置#|清空 admin"])
    clean = menu.clean(items)
    assert clean[0]["cmd"] == "/重置"
    assert "admin" not in clean[0]["desc"]


def test_text_menu_alignment():
    items = menu.parse_items(["/画图|画画", "/a|短"])
    text = menu.text_menu(items, title="指令菜单", foot="页脚")
    lines = text.splitlines()
    assert lines[0] == "指令菜单"
    assert lines[1].startswith("/画图")
    assert lines[1].index("画画") == lines[2].index("短")     # 说明列对齐
    assert lines[-1] == "页脚"


def test_text_menu_empty():
    assert menu.text_menu([], title="空") == "空"


def test_layout_proportional():
    items = menu.parse_items(["/a|x"] * 5)
    box = menu.layout(items, width=760)
    assert box["w"] == 760 and box["rows"] == 5
    assert box["h"] >= 56


def test_render_png_optional():
    items = menu.parse_items(["/画图|画画"])
    raw = menu.render_png(items)
    if raw is None:
        assert True          # 没有 pillow/字体时允许返回 None（调用方退回文字）
    else:
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"

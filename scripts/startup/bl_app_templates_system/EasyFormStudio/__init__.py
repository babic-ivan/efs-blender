# SPDX-FileCopyrightText: 2026 EasyFormStudio
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Initialization script for the EasyFormStudio application template.

import bpy
from bpy.app.handlers import persistent

# Extensions activated automatically when present. The application bundles
# efs and measureit in the "system" repository; the other entries cover a
# development setup where they are installed as user extensions instead.
EXTENSIONS_AUTO_ENABLE = (
    "bl_ext.system.efs",
    "bl_ext.system.measureit",
    "bl_ext.user_default.efs",
    "bl_ext.blender_org.measureit",
)


def _scene_defaults(scene):
    # Furniture/carpentry defaults: display lengths in millimeters.
    # Unit scale stays 1.0 (1 unit = 1 m) - EFS models geometry in meters.
    unit = scene.unit_settings
    unit.system = 'METRIC'
    unit.scale_length = 1.0
    unit.length_unit = 'MILLIMETERS'


def _viewport_defaults():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != 'VIEW_3D':
                continue
            space = area.spaces.active
            # Keep the sidebar (EFS panel) open by default.
            space.show_region_ui = True


def _enable_extensions():
    import addon_utils
    for module_name in EXTENSIONS_AUTO_ENABLE:
        try:
            addon_utils.enable(module_name, default_set=True, persistent=True)
        except Exception:
            # The extension is not installed in this configuration; the
            # template still works without it.
            pass


# Sidebar (N-panel) tabs hidden in the 3D viewport - only EFS tabs remain.
SIDEBAR_HIDE_CATEGORIES = {"Item", "Tool", "View"}


def _hide_sidebar_tabs():
    for cls in list(bpy.types.Panel.__subclasses__()):
        if (getattr(cls, "bl_space_type", None) == 'VIEW_3D'
                and getattr(cls, "bl_region_type", None) == 'UI'
                and getattr(cls, "bl_category", None) in SIDEBAR_HIDE_CATEGORIES
                and getattr(cls, "is_registered", False)):
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass


_view3d_menus_draw_orig = None


def _view3d_menus_draw(self, context):
    # Object mode: no Add menu - cabinets and boards are created through EFS.
    if context.mode == 'OBJECT':
        layout = self.layout
        layout.menu("VIEW3D_MT_view")
        layout.menu("VIEW3D_MT_select_object")
        layout.menu("VIEW3D_MT_object")
    else:
        _view3d_menus_draw_orig(self, context)


def _simplify_view3d_menus():
    global _view3d_menus_draw_orig
    menu = bpy.types.VIEW3D_MT_editor_menus
    if _view3d_menus_draw_orig is None:
        _view3d_menus_draw_orig = menu.draw
        menu.draw = _view3d_menus_draw


@persistent
def load_factory_startup_handler(_filepath):
    for scene in bpy.data.scenes:
        _scene_defaults(scene)
    _viewport_defaults()
    _enable_extensions()


def register():
    bpy.app.handlers.load_factory_startup_post.append(load_factory_startup_handler)
    bpy.app.timers.register(_kiosk_ui, first_interval=0.1)


def _kiosk_ui():
    _hide_sidebar_tabs()
    _simplify_view3d_menus()
    return None


def unregister():
    bpy.app.handlers.load_factory_startup_post.remove(load_factory_startup_handler)

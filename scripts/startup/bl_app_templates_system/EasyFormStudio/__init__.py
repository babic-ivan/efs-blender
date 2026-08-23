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
# "Display" is MeasureIt's tab (EFS drives MeasureIt programmatically).
SIDEBAR_HIDE_CATEGORIES = {"Item", "Tool", "View", "Animation", "Display"}


def _hide_panel(cls):
    # Unregister: a post-registration poll swap is ignored by the C side for
    # panels, so this is the only reliable way to hide the category tabs.
    # (The owning add-on's unregister then warns on exit - console only.)
    try:
        bpy.utils.unregister_class(cls)
    except Exception:
        pass


def _hide_sidebar_tabs():
    for cls in list(bpy.types.Panel.__subclasses__()):
        if (getattr(cls, "bl_space_type", None) == 'VIEW_3D'
                and getattr(cls, "bl_region_type", None) == 'UI'
                and getattr(cls, "bl_category", None) in SIDEBAR_HIDE_CATEGORIES
                and getattr(cls, "is_registered", False)):
            _hide_panel(cls)


def _hide_view_layer_core_panels():
    # The View Layer properties tab hosts the EFS "Scene elements" and
    # "Cabinet elements" panels; hide the built-in panels (EEVEE/Cycles
    # passes, Freestyle, filter, overrides) so the EFS panels sit on top.
    for cls in list(bpy.types.Panel.__subclasses__()):
        if (getattr(cls, "bl_context", None) == "view_layer"
                and getattr(cls, "bl_space_type", None) == 'PROPERTIES'
                and not getattr(cls, "__module__", "").startswith("bl_ext.")
                and getattr(cls, "is_registered", False)):
            _hide_panel(cls)


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


# Built-in tools removed from the 3D viewport toolbar.
TOOLBAR_REMOVE = {
    "builtin.cursor",
    "builtin.rotate",
    "builtin.scale", "builtin.scale_cage",
    "builtin.transform",
    "builtin.measure",
    "builtin.breakdowner", "builtin.push", "builtin.relax",
}


def _trim_toolbar():
    from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as tools_panel

    def _keep(tool):
        return getattr(tool, "idname", None) not in TOOLBAR_REMOVE

    def _filter_seq(seq):
        out = []
        for item in seq:
            if item is None:
                if not out or out[-1] is None:
                    continue
                out.append(None)
            elif hasattr(item, "idname"):
                if _keep(item):
                    out.append(item)
            elif isinstance(item, tuple):
                sub = tuple(tool for tool in item if _keep(tool))
                if sub:
                    out.append(sub)
            else:
                out.append(item)
        while out and out[-1] is None:
            out.pop()
        return out

    for mode, seq in list(tools_panel._tools.items()):
        try:
            tools_panel._tools[mode] = _filter_seq(list(seq))
        except Exception:
            pass


def _topbar_draw_right(self, context):
    layout = self.layout
    # Keep report banners when the status bar is hidden; the scene and
    # view-layer selectors are not part of the EasyFormStudio workflow.
    if not context.screen.show_statusbar:
        layout.template_reports_banner()
        layout.template_running_jobs()


def _simplify_topbar():
    bpy.types.TOPBAR_HT_upper_bar.draw_right = _topbar_draw_right


def _activate_efs_tool():
    # Make the EFS tool the active tool in the 3D viewport.
    if bpy.app.background:
        return
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                region = next((r for r in area.regions if r.type == 'WINDOW'), None)
                with bpy.context.temp_override(window=window, area=area, region=region):
                    try:
                        bpy.ops.wm.tool_set_by_id(name="efs.tool")
                    except Exception:
                        pass
                return


def _kiosk_ui():
    _hide_sidebar_tabs()
    _hide_view_layer_core_panels()
    _simplify_view3d_menus()
    _simplify_topbar()
    _trim_toolbar()
    _activate_efs_tool()
    return None


def unregister():
    bpy.app.handlers.load_factory_startup_post.remove(load_factory_startup_handler)

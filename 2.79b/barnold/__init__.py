# -*- coding: utf-8 -*-

__author__ = "Tyler Furby"
__email__ = "tyler@tylerfurby.com"

bl_info = {
    "name"          : "Barnold",
    "description"   : "Solid Angle's Arnold Renderer for Blender",
    "author"        : "Tyler Furby <tyler@tylerfurby.com>", "N.Ildar <nildar@users.sourceforge.net>"
    "version"       : (0, 0, 2),
    "blender"       : (2, 79, 0),
    "location"      : "Info header, render engine menu",
    "category"      : "Render"
}

import bpy
import sys
import os
from .utils import IO

class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD_RENDER"
    bl_label = "Arnold Render"
    bl_use_preview = True
    # bl_use_exclude_layers = False
    # bl_use_postprocess = False
    # bl_use_save_buffers = False
    # bl_use_shading_nodes = False
    bl_use_shading_nodes_custom = True
    # bl_use_spherical_stereo = False
    # bl_use_texture_preview  = False

    _CLASSES = []  # classes for (un)register

    _COMPATIBLE_PANELS = (
        ("properties_render", ((
            "RENDER_PT_render",
            "RENDER_PT_dimensions",
            "RENDER_PT_output",
            "RENDER_PT_post_processing",
        ), False)),
        ("properties_world", ((
            "WORLD_PT_context_world",
            "WORLD_PT_custom_props",
        ), False)),
        ("properties_data_lamp", ((
            "DATA_PT_context_lamp",
            #"DATA_PT_area",
            "DATA_PT_custom_props_lamp",
        ), False)),
        ("properties_material", ((
            "MATERIAL_PT_context_material",
            #"MATERIAL_PT_preview",
            "MATERIAL_PT_custom_props",
        ), False)),
        ("properties_texture", None),
        #("properties_texture", ((
        #    "TEXTURE_PT_context_texture",
        #    "TEXTURE_PT_preview",
        #    "TEXTURE_PT_image",
        #    #"TEXTURE_PT_image_sampling",
        #    #"TEXTURE_PT_image_mapping",
        #    "TEXTURE_PT_mapping",
        #    #"TEXTURE_PT_influence",
        #), False)),
        ("properties_render_layer", None),
        ("properties_scene", None),
        ("properties_data_camera", None),
        ("properties_data_mesh", None),
        ("properties_particle", None),
    )

    def __init__(self):
        self.session = None

    def update(self, data, scene):
        IO.block("\nArnold: - Engine::Update ")
        if not self.session:
            self.session = Session.create(data, scene)

        engine.update(self, data, scene)

    def render(self, scene):
        IO.block("\nArnold: - Engine::Render ")
        engine.render(self, scene)
    
    def preview_update(self, context, id):
        IO.block("\nArnold: - Preview::Update ")
        pass
    
    def preview_render(self):
        IO.block("\nArnold: - Preview::Render ")
        pass

    def view_update(self, context):
        IO.block("\nArnold: - View::Update ")
        engine.view_update(self, context)

    def view_draw(self, context):
        IO.block("\nArnold: - View::Draw ")
        engine.view_draw(self, context)
    
    def __del__(self):
        engine.free(self)


    @classmethod
    def _compatible(cls, mod, panels, remove=False):
        import bl_ui

        mod = getattr(bl_ui, mod)
        if panels is None:
            for c in mod.__dict__.values():
                ce = getattr(c, "COMPAT_ENGINES", None)
                if ce is not None:
                    if remove:
                        ce.remove(cls.bl_idname)
                    else:
                        ce.add(cls.bl_idname)
        else:
            classes, exclude = panels
            if exclude:
                for c in mod.__dict__.values():
                    if c.__name__ not in classes:
                        ce = getattr(c, "COMPAT_ENGINES", None)
                        if ce is not None:
                            if remove:
                                ce.remove(cls.bl_idname)
                            else:
                                ce.add(cls.bl_idname)
            else:
                for c in classes:
                    ce = getattr(mod, c).COMPAT_ENGINES
                    if remove:
                        ce.remove(cls.bl_idname)
                    else:
                        ce.add(cls.bl_idname)

    @classmethod
    def register_class(cls, _cls):
        cls._CLASSES.append(_cls)
        return _cls

    @classmethod
    def register(cls):
        for mod, panels in cls._COMPATIBLE_PANELS:
            cls._compatible(mod, panels)
        for _cls in cls._CLASSES:
            bpy.utils.register_class(_cls)

    @classmethod
    def unregister(cls):
        for mod, panels in cls._COMPATIBLE_PANELS:
            cls._compatible(mod, panels, True)
        for _cls in cls._CLASSES:
            bpy.utils.unregister_class(_cls)

    @classmethod
    def is_active(cls, context):
        return context.scene.render.engine == cls.bl_idname


class Session(dict):
    _id = 0
    camera = None
    scene = None
    meshes = {}
    mesh_instances = {}
    lights = {}
    display = None
    peak = None
    mem = None
    ipr = None
    offset = None
    IO.block("Arnold Global Session: -- ID: %d" % _id)

    def __init__(self, *args, **kwargs):
        IO.block("Session Init: Initializing Class Instance")
        # self._id = id(self)
        if self._id != 0:
            self._id = id(self)
        self.camera = kwargs.setdefault("camera", None)
        self.scene = kwargs.setdefault("scene", None)
        self.meshes = {}
        self.mesh_instances = {}
        self.lights = {}

    @classmethod
    def create(cls, data, scene):
        IO.block("Create Session: Modifying Class Template")
        return cls(camera=scene.camera, scene=scene)

    
    def update(self):
        IO.block("Update Session: Updating Instance Data")
        IO.debug(self.camera)


    @classmethod
    def cache(cls, session):
        IO.block("Cache Sesssion: Storing Blend Data")
        # cls.active_camera = session.active_camera
        # cls.active_scene = session.active_scene
        # print(session)
        # cls.cameras = session['cameras']
        # cls.meshes = session['meshes']
        # cls.mesh_instances = session['mesh_instances']
        # cls.lights = session['lights']
        # cls.scenes = session['scenes']
        cls._id = id(session)


    @classmethod     
    def free(cls):
        return cls()
    
    # @classmethod
    # def reset(cls):
    #     cls.active_camera = None
    #     cls.active_scene = None

def register():
    from . import addon_preferences
    addon_preferences.register()

    from . import props
    from . import nodes
    from . import ops
    from . import ui
    from . import engine
    from . import addon_preferences

    bpy.utils.register_class(ArnoldRenderEngine)
    nodes.register()


def unregister():
    from . import addon_preferences
    from . import props
    from . import nodes
    from . import ops
    from . import ui
    from . import engine
    from . import addon_preferences
    addon_preferences.unregister()
    bpy.utils.unregister_class(ArnoldRenderEngine)
    nodes.unregister()

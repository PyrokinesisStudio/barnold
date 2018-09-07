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
    use_highlight_tiles = True
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
        """
        Constructor a RenderEngine instance() when Blender launches a rendering thread
        """
        self.session = None

    def __del__(self):
        """
        Destructor for a RenderEngine instance when Blender closes a rendering thread
        """
        engine.free(self)
        
    def update(self, data, scene):
        """
        Update the RenderEngine either via creating a session or resetting to the base session
        """
        IO.block("\nArnoldEngine::Update()")
        if not self.session:
            if self.is_preview:
                """Create a preview Session using preview render data"""
                self.session = Session
                engine.create(self, data, scene, None, None, None, preview_osl=False)
            else:
                """Create a final Session using final render data"""
                self.session = Session
                engine.create(self, data, scene)
            """Create Callback - Updates Session"""
            # engine.update(self, data, scene)
        else:
            """Reset Session to defaults. Session should never be initialized for Final Render"""
            engine.reset(self, data, scene)

    def render(self, scene):
        IO.block("\nArnoldEngine::Render()")
        engine.render(self, scene)
    
    def preview_update(self, context, id):
        IO.block("\nAArnoldEngine::PreviewUpdate()")
        pass
    
    def preview_render(self):
        IO.block("\nArnoldEngine::PreviewRender()")
        pass

    def view_update(self, context):
        IO.block("\nArnoldEngine::ViewUpdate()")
        # if not self.session:
        #     self.session = Session.create(self, context.blend_data, context.scene)
        #     engine.create(self, context.blend_data, context.scene,
        #                   context.region, context.space_data, context.region_data)
        # else:
        #     engine.update(self, context.blend_data, context.scene)
        #     pass
        engine.view_update(self, context)

    def view_draw(self, context):
        IO.block("\nArnoldEngine:: ViewDraw()")
        engine.view_draw(self, context)
    

    def update_render_passes(self, scene, srl):
        pass
        #TODO: engine.register_passes(self, scene, srl)


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
    _id     = 0
    camera  = None
    scene   = None
    meshes  = {}
    mesh_instances = {}
    lights  = {}
    display = None
    peak    = None
    mem     = None
    ipr     = None
    offset  = None
    

    def __init__(self, *args, **kwargs):
        IO.block("Session::Init()")
        if self._id != 0:
            IO.block("- New Session")
            self._id = id(self)
            IO.block("Session::ID - Instance: %d" % self._id)
        elif self._id == 0:
            IO.block("- Genesis Session")
            IO.block("Session::ID - Genesis: %d" % self._id)


    @classmethod
    def create(cls, render_engine, data, scene):
        """
        Create a Session, returning a class instance with the current camera and scene
        """
        IO.block("Session::Create()")
        cls.camera = scene.camera
        cls.scene = scene
        return cls()

            
    def sync(self, data, scene, engine):
        """
        Set each data member with updated data from scene
        """
        IO.block("Session::Sync()")
        def _sync_camera():
            pass
        def _sync_scene():
            pass
        def _sync_lamps():
            pass
        def _sync_meshes():
            pass
        pass
        IO.block("Session::ID - Sync: %d" % self._id)
        

    def export(self, data, scene, engine):
        """
        Callback to re-export the scene to the RenderEngine
        """
        IO.block("Session::Export()")
        def _export_camera():
            pass
        IO.block("Session::ID - Export: %d" % self._id)


    @classmethod
    def cache(cls, session):
        IO.block("Session::Cache()")
        cls._id = id(session)
        cls.camera = session.camera
        cls.scene = session.scene
        cls.meshes = session.meshes
        cls.mesh_instances = session.mesh_instances
        cls.lights = session.lights
        cls.display = session['display']
        # cls.ipr = session['ipr']
        cls.mem = session['mem']
        cls.offset = session['offset']
        cls.peak = session['peak']
        

    @classmethod
    def reset(cls):
        """
        Reset after Final Render.
        """
        IO.block("Session::Reset()")
        cls._id     = 0
        cls.camera  = None
        cls.scene   = None
        cls.meshes  = {}
        cls.mesh_instances = {}
        cls.lights  = {}
        cls.display = None
        cls.peak    = None
        cls.mem     = None
        cls.ipr     = None
        cls.offset  = None
        return cls()

    @classmethod     
    def free(cls):
        """
        Free after Viewport Render
        """
        IO.block("Session::Free()")
        return cls()



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

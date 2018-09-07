import os
import sys
import itertools
import re
from contextlib import contextmanager

import bpy

import arnold
from ..utils import IO
from ..nodes import (
    ArnoldNode,
    ArnoldNodeOutput
)


class Shaders:
    def __init__(self, data):
        # print("Shader Init")
        self._data = data
        self._shaders = {}
        self._default = arnold.AiNode('lambert')  # default shader, if used
        self._Name = self._CleanNames("M", itertools.count())

    def get(self, mat):
        if mat:
            node = self._shaders.get(mat)
            if node is None:
                node = self._export(mat)
                if node is None:
                    node = self.default
                self._shaders[mat] = node
        else:
            node = self.default
        return node

    @property
    def default(self):
        node = self._default
        if node is None:
            node = arnold.AiNode('utility')
            arnold.AiNodeSetStr(node, "name", "__default")
            self._default = node
        return node

    def _export(self, mat):
        if mat.use_nodes:
            print("Exporting")
            for n in mat.node_tree.nodes:
                if isinstance(n, ArnoldNodeOutput) and n.is_active:
                    input = n.inputs[0]
                    if input.is_linked:
                        return _AiNode(input.links[0].from_node, self._Name(mat.name), {})
                    break
            return None

        shader = mat.arnold
        if mat.type == 'SURFACE':
            node = arnold.AiNode(shader.type)
            if shader.type == 'lambert':
                arnold.AiNodeSetFlt(node, "Kd", mat.diffuse_intensity)
                arnold.AiNodeSetRGB(node, "Kd_color", *mat.diffuse_color)
                arnold.AiNodeSetRGB(node, "opacity", *shader.lambert.opacity)
            elif shader.type == 'standard_surface':
                standard_surface = shader.standard_surface
                arnold.AiNodeSetFlt(node, "base", mat.diffuse_intensity)
                arnold.AiNodeSetRGB(node, "base_color", *mat.diffuse_color)
                arnold.AiNodeSetFlt(node, "diffuse_roughness", standard_surface.diffuse_roughness)
                arnold.AiNodeSetFlt(node, "metalness", standard_surface.metalness)
                arnold.AiNodeSetFlt(node, "specular", mat.specular_intensity)
                arnold.AiNodeSetRGB(node, "specular_color", *mat.specular_color)
                arnold.AiNodeSetFlt(node, "specular_roughness", standard_surface.specular_roughness)
                #arnold.AiNodeSetFlt(node, "specular_ior", standard_surface.specular_ior)
                arnold.AiNodeSetFlt(node, "specular_anisotropy", standard_surface.specular_anisotropy)
                arnold.AiNodeSetFlt(node, "specular_rotation", standard_surface.specular_rotation)
                arnold.AiNodeSetFlt(node, "emission", mat.emit)
                arnold.AiNodeSetRGB(node, "emission_color", *mat.diffuse_color)
                arnold.AiNodeSetFlt(node, "transmission", standard_surface.transmission)
                arnold.AiNodeSetRGB(node, "transmission_color", *standard_surface.transmission_color)
                arnold.AiNodeSetFlt(node, "transmission_depth", standard_surface.transmission_depth)
                arnold.AiNodeSetRGB(node, "transmission_scatter", *standard_surface.transmission_scatter)
                arnold.AiNodeSetFlt(node, "transmission_scatter_anisotropy", standard_surface.transmission_scatter_anisotropy)
                arnold.AiNodeSetFlt(node, "transmission_dispersion", standard_surface.transmission_dispersion)
                arnold.AiNodeSetFlt(node, "transmission_extra_roughness", standard_surface.transmission_extra_roughness)
                arnold.AiNodeSetBool(node, "transmit_aovs", standard_surface.transmit_aovs)
                #arnold.AiNodeSetFlt(node, "sss_synopsis", standard_surface.sss_synopsis)
                arnold.AiNodeSetFlt(node, "subsurface", standard_surface.subsurface)
                arnold.AiNodeSetRGB(node, "subsurface_color", *standard_surface.subsurface_color)
                arnold.AiNodeSetRGB(node, "subsurface_radius", *standard_surface.subsurface_radius)
                arnold.AiNodeSetFlt(node, "subsurface_scale", standard_surface.subsurface_scale)
                arnold.AiNodeSetFlt(node, "subsurface_anisotropy", standard_surface.subsurface_anisotropy)
                arnold.AiNodeSetStr(node, "subsurface_type", standard_surface.subsurface_type)
                arnold.AiNodeSetBool(node, "thin_walled", standard_surface.thin_walled)
                arnold.AiNodeSetVec(node, "normal", *standard_surface.normal)
                # arnold.AiNodeSetFlt(node, "tangent", standard_surface.tangent)
                arnold.AiNodeSetFlt(node, "coat", standard_surface.coat)
                arnold.AiNodeSetRGB(node, "coat_color", *standard_surface.coat_color)
                arnold.AiNodeSetFlt(node, "coat_roughness", standard_surface.coat_roughness)
                #arnold.AiNodeSetFlt(node, "coat_ior", standard_surface.coat_ior)
                arnold.AiNodeSetVec(node, "coat_normal", *standard_surface.coat_normal)
                arnold.AiNodeSetFlt(node, "coat_affect_color", standard_surface.coat_affect_color)
                arnold.AiNodeSetFlt(node, "coat_affect_roughness", standard_surface.coat_affect_roughness)
                #arnold.AiNodeSetFlt(node, "opacity", standard_surface.opacity)
                arnold.AiNodeSetBool(node, "caustics", standard_surface.caustics)
                arnold.AiNodeSetBool(node, "internal_reflections", standard_surface.internal_reflections)
                arnold.AiNodeSetBool(node, "exit_to_background", standard_surface.exit_to_background)
                arnold.AiNodeSetFlt(node, "indirect_diffuse", standard_surface.indirect_diffuse)
                arnold.AiNodeSetFlt(node, "indirect_specular", standard_surface.indirect_specular)
                # arnold.AiNodeSetStr(node, "sss_set_name", standard_surface.sss_set_name)
                # arnold.AiNodeSetStr(node, "anistropy_tangent", standard_surface.anistropy_tangent)
                arnold.AiNodeSetFlt(node, "thin_film_thickness", standard_surface.thin_film_thickness)
                #arnold.AiNodeSetFlt(node, "thin_film_ior", standard_surface.thin_film_ior)
                # arnold.AiNodeSetRGB(node, "aov_id(1-8)", standard_surface.aov_id(1-8))
                arnold.AiNodeSetFlt(node, "sheen", standard_surface.sheen)
                arnold.AiNodeSetRGB(node, "sheen_color", *standard_surface.sheen_color)
                arnold.AiNodeSetFlt(node, "sheen_roughness", standard_surface.sheen_roughness)
                # TODO: other standard_surface node parmas
            elif shader.type == 'utility':
                utility = shader.utility
                arnold.AiNodeSetStr(node, "color_mode", utility.color_mode)
                arnold.AiNodeSetStr(node, "shade_mode", utility.shade_mode)
                arnold.AiNodeSetStr(node, "overlay_mode", utility.overlay_mode)
                arnold.AiNodeSetRGB(node, "color", *mat.base_color)
                arnold.AiNodeSetFlt(node, "opacity", utility.opacity)
                arnold.AiNodeSetFlt(node, "ao_distance", utility.ao_distance)
            elif shader.type == 'flat':
                arnold.AiNodeSetRGB(node, "color", *mat.base_color)
                arnold.AiNodeSetRGB(node, "opacity", *shader.flat.opacity)
            elif shader.type == 'standard_hair':
                standard_hair = shader.standard_hair
                arnold.AiNodeSetFlt(node, "base", standard_hair.base)
                arnold.AiNodeSetRGB(node, "base_color", *standard_hair.base_color)
                arnold.AiNodeSetFlt(node, "melanin", standard_hair.melanin)
                arnold.AiNodeSetFlt(node, "melanin_redness", standard_hair.melanin_redness)
                arnold.AiNodeSetFlt(node, "melanin_randomize", standard_hair.melanin_randomize)
                arnold.AiNodeSetFlt(node, "roughness", standard_hair.roughness)
                arnold.AiNodeSetFlt(node, "ior", standard_hair.ior)
                arnold.AiNodeSetFlt(node, "shift", standard_hair.shift)
                arnold.AiNodeSetRGB(node, "specular_tint", *standard_hair.specular_tint)
                arnold.AiNodeSetRGB(node, "specular2_tint", *standard_hair.specular2_tint)
                arnold.AiNodeSetRGB(node, "transmission_tint", *standard_hair.transmission_tint)
                arnold.AiNodeSetFlt(node, "diffuse", standard_hair.diffuse)
                arnold.AiNodeSetRGB(node, "diffuse_color", *standard_hair.diffuse_color)
                arnold.AiNodeSetFlt(node, "emission", standard_hair.emission)
                arnold.AiNodeSetRGB(node, "emission_color ", *standard_hair.emission_color)
                arnold.AiNodeSetRGB(node, "opacity", *standard_hair.opacity)
                arnold.AiNodeSetFlt(node, "indirect_diffuse", standard_hair.indirect_diffuse)
                arnold.AiNodeSetFlt(node, "indirect_specular", standard_hair.indirect_specular)
                arnold.AiNodeSetFlt(node, "extra_depth", standard_hair.extra_depth)
                arnold.AiNodeSetFlt(node, "extra_samples", standard_hair.extra_samples)
        elif mat.type == 'WIRE':
            wire = shader.wire
            node = arnold.AiNode('wireframe')
            arnold.AiNodeSetStr(node, "edge_type", wire.edge_type)
            arnold.AiNodeSetRGB(node, "line_color", *mat.diffuse_color)
            arnold.AiNodeSetRGB(node, "fill_color", *wire.fill_color)
            arnold.AiNodeSetFlt(node, "line_width", wire.line_width)
            arnold.AiNodeSetBool(node, "raster_space", wire.raster_space)
        elif mat.type == 'VOLUME':
            standard_volume = shader.standard_volume
            node = arnold.AiNode('standard_volume')
            arnold.AiNodeSetFlt(node, "density", standard_volume.density)
            arnold.AiNodeSetFlt(node, "scatter", standard_volume.scatter)
            arnold.AiNodeSetRGB(node, "scatter_color", *standard_volume.scatter_color)
            arnold.AiNodeSetFlt(node, "scatter_anisotropy", standard_volume.scatter_anisotropy)
            arnold.AiNodeSetRGB(node, "transparent", *standard_volume.transparent)
            arnold.AiNodeSetFlt(node, "transparent_depth", standard_volume.transparent_depth)
            #arnold.AiNodeSetStr(node, "emission_mode", standard_volume.emission_mode)
            arnold.AiNodeSetFlt(node, "emission", standard_volume.emission)
            arnold.AiNodeSetRGB(node, "emission_color", *standard_volume.emission_color)
            arnold.AiNodeSetFlt(node, "temperature", standard_volume.temperature)
            arnold.AiNodeSetFlt(node, "blackbody_kelvin", standard_volume.blackbody_kelvin)
            arnold.AiNodeSetFlt(node, "blackbody_intensity", standard_volume.blackbody_intensity)
            # arnold.AiNodeSetFlt(node, "interpolation", standard_volume.interpolation)
        else:
            return None
        arnold.AiNodeSetStr(node, "name", self._Name(mat.name))
        return node

    @staticmethod
    def _CleanNames(prefix, count):
        def fn(name):
            return "%s%d::%s" % (prefix, next(count), _RN.sub("_", name))
        return fn

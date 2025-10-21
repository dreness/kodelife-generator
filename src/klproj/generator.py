"""
KodeLife project file generator.

This module provides the KodeProjBuilder class for constructing .klproj files.
"""

import xml.etree.ElementTree as ET
import zlib
from typing import List, Optional

from .types import (
    Parameter,
    ProjectProperties,
    RenderPass,
    Vec2,
    Vec3,
    Vec4,
)


class KodeProjBuilder:
    """
    Builder for KodeLife project files.

    This class provides a fluent interface for constructing KodeLife .klproj files.
    Projects are built incrementally by setting properties, adding parameters,
    and adding render passes.

    Attributes:
        version: KodeLife project format version (default: 19)
        api: Default rendering API ("GL3", "MTL", etc.)
        properties: Project properties (resolution, author, etc.)
        global_params: List of global parameters
        passes: List of render passes

    Example:
        # Create a basic project
        builder = KodeProjBuilder(api="MTL")
        builder.set_resolution(1920, 1080)
        builder.set_author("Your Name")
        builder.add_global_param(time_param)
        builder.add_pass(render_pass)
        builder.save("output.klproj")
    """

    def __init__(self, version: int = 19, api: str = "MTL"):
        """
        Initialize the project builder.

        Args:
            version: KodeLife project format version (default: 19)
            api: Default rendering API (default: "MTL")
                 Common values: "GL3", "GL2", "MTL", "ES3"
        """
        self.version = version
        self.api = api
        self.properties = ProjectProperties()
        self.global_params: List[Parameter] = []
        self.passes: List[RenderPass] = []

    def set_resolution(self, width: int, height: int) -> "KodeProjBuilder":
        """
        Set project resolution.

        Args:
            width: Width in pixels
            height: Height in pixels

        Returns:
            Self for method chaining
        """
        self.properties.width = width
        self.properties.height = height
        return self

    def set_author(self, author: str) -> "KodeProjBuilder":
        """
        Set project author.

        Args:
            author: Author name

        Returns:
            Self for method chaining
        """
        self.properties.author = author
        return self

    def set_comment(self, comment: str) -> "KodeProjBuilder":
        """
        Set project comment/description.

        Args:
            comment: Project description

        Returns:
            Self for method chaining
        """
        self.properties.comment = comment
        return self

    def add_global_param(self, param: Parameter) -> "KodeProjBuilder":
        """
        Add a global parameter available to all passes.

        Global parameters are uniforms that can be accessed by any shader stage
        in any pass.

        Args:
            param: Parameter to add

        Returns:
            Self for method chaining
        """
        self.global_params.append(param)
        return self

    def add_pass(self, render_pass: RenderPass) -> "KodeProjBuilder":
        """
        Add a render pass.

        Passes are executed in the order they are added.

        Args:
            render_pass: Render pass to add

        Returns:
            Self for method chaining
        """
        self.passes.append(render_pass)
        return self

    def _create_element(
        self, name: str, text: Optional[str] = None, cdata: bool = False
    ) -> ET.Element:
        """
        Create an XML element.

        Args:
            name: Element tag name
            text: Optional text content
            cdata: Whether text should be CDATA (currently unused)

        Returns:
            XML Element
        """
        elem = ET.Element(name)
        if text is not None:
            elem.text = str(text)
        return elem

    def _vec2_to_xml(self, parent: ET.Element, vec: Vec2):
        """
        Convert Vec2 to XML elements.

        Args:
            parent: Parent XML element
            vec: Vector to convert
        """
        ET.SubElement(parent, "x").text = str(vec.x)
        ET.SubElement(parent, "y").text = str(vec.y)

    def _vec3_to_xml(self, parent: ET.Element, vec: Vec3):
        """
        Convert Vec3 to XML elements.

        Args:
            parent: Parent XML element
            vec: Vector to convert
        """
        ET.SubElement(parent, "x").text = str(vec.x)
        ET.SubElement(parent, "y").text = str(vec.y)
        ET.SubElement(parent, "z").text = str(vec.z)

    def _vec4_to_xml(self, parent: ET.Element, vec: Vec4):
        """
        Convert Vec4 to XML elements.

        Args:
            parent: Parent XML element
            vec: Vector to convert
        """
        ET.SubElement(parent, "x").text = str(vec.x)
        ET.SubElement(parent, "y").text = str(vec.y)
        ET.SubElement(parent, "z").text = str(vec.z)
        ET.SubElement(parent, "w").text = str(vec.w)

    def _build_properties_xml(self, parent: ET.Element):
        """
        Build properties XML section.

        Args:
            parent: Parent XML element to add properties to
        """
        props = ET.SubElement(parent, "properties")

        ET.SubElement(props, "creator").text = self.properties.creator
        ET.SubElement(props, "creatorVersion").text = self.properties.creator_version
        ET.SubElement(props, "versionMajor").text = str(self.properties.version_major)
        ET.SubElement(props, "versionMinor").text = str(self.properties.version_minor)
        ET.SubElement(props, "versionPatch").text = str(self.properties.version_patch)
        ET.SubElement(props, "author").text = self.properties.author
        ET.SubElement(props, "comment").text = self.properties.comment
        ET.SubElement(props, "enabled").text = str(self.properties.enabled)

        size = ET.SubElement(props, "size")
        ET.SubElement(size, "x").text = str(self.properties.width)
        ET.SubElement(size, "y").text = str(self.properties.height)

        ET.SubElement(props, "format").text = self.properties.format

        clear_color = ET.SubElement(props, "clearColor")
        self._vec4_to_xml(clear_color, self.properties.clear_color)

        ET.SubElement(props, "audioSourceType").text = str(self.properties.audio_source_type)
        ET.SubElement(props, "audioFilePath").text = self.properties.audio_file_path
        ET.SubElement(props, "selectedRenderPassIndex").text = "0"
        ET.SubElement(props, "selectedKontrolPanelIndex").text = "0"
        ET.SubElement(props, "uiExpandedPreviewDocument").text = "1"
        ET.SubElement(props, "uiExpandedPreviewRenderPass").text = "1"
        ET.SubElement(props, "uiExpandedProperties").text = "1"
        ET.SubElement(props, "uiExpandedAudio").text = "1"

    def _build_parameter_xml(self, parent: ET.Element, param: Parameter):
        """
        Build parameter XML.

        Args:
            parent: Parent XML element
            param: Parameter to convert to XML
        """
        param_elem = ET.SubElement(parent, "param")
        param_elem.set("type", param.param_type.value)

        ET.SubElement(param_elem, "displayName").text = param.display_name
        ET.SubElement(param_elem, "variableName").text = param.variable_name
        ET.SubElement(param_elem, "uiExpanded").text = str(param.ui_expanded)

        # Add type-specific properties
        for key, value in param.properties.items():
            if isinstance(value, (Vec2, Vec3, Vec4)):
                vec_elem = ET.SubElement(param_elem, key)
                if isinstance(value, Vec2):
                    self._vec2_to_xml(vec_elem, value)
                elif isinstance(value, Vec3):
                    self._vec3_to_xml(vec_elem, value)
                elif isinstance(value, Vec4):
                    self._vec4_to_xml(vec_elem, value)
            elif isinstance(value, dict):
                dict_elem = ET.SubElement(param_elem, key)
                for sub_key, sub_value in value.items():
                    ET.SubElement(dict_elem, sub_key).text = str(sub_value)
            else:
                ET.SubElement(param_elem, key).text = str(value)

    def _build_params_xml(self, parent: ET.Element):
        """
        Build global parameters XML section.

        Args:
            parent: Parent XML element
        """
        params = ET.SubElement(parent, "params")
        ET.SubElement(params, "uiExpanded").text = "1"

        for param in self.global_params:
            self._build_parameter_xml(params, param)

    def _build_shader_stage_xml(self, parent: ET.Element, stage):
        """
        Build shader stage XML.

        Args:
            parent: Parent XML element
            stage: ShaderStage to convert to XML
        """

        stage_elem = ET.SubElement(parent, "stage")
        stage_elem.set("type", stage.stage_type.value)

        # Properties
        props = ET.SubElement(stage_elem, "properties")
        ET.SubElement(props, "enabled").text = str(stage.enabled)
        ET.SubElement(props, "hidden").text = str(stage.hidden)
        ET.SubElement(props, "locked").text = "0"
        ET.SubElement(props, "fileWatch").text = "1" if stage.file_watch else "0"
        ET.SubElement(props, "fileWatchPath").text = stage.file_watch_path
        ET.SubElement(props, "uiExpanded").text = "1"

        # Parameters
        params = ET.SubElement(stage_elem, "params")
        ET.SubElement(params, "uiExpanded").text = "1"
        for param in stage.parameters:
            self._build_parameter_xml(params, param)

        # Shader sources
        shader = ET.SubElement(stage_elem, "shader")
        for source in stage.sources:
            source_elem = ET.SubElement(shader, "source")
            source_elem.set("profile", source.profile.value)
            source_elem.text = source.code

    def _build_pass_xml(self, parent: ET.Element, render_pass: RenderPass):
        """
        Build render pass XML.

        Args:
            parent: Parent XML element
            render_pass: RenderPass to convert to XML
        """
        pass_elem = ET.SubElement(parent, "pass")
        pass_elem.set("type", render_pass.pass_type.value)

        # Properties
        props = ET.SubElement(pass_elem, "properties")
        ET.SubElement(props, "label").text = render_pass.label
        ET.SubElement(props, "enabled").text = str(render_pass.enabled)
        ET.SubElement(props, "selectedShaderStageIndex").text = "4"
        ET.SubElement(props, "primitiveIndex").text = "0"
        ET.SubElement(props, "primitiveType").text = render_pass.primitive_type
        ET.SubElement(props, "instanceCount").text = "1"
        ET.SubElement(props, "uiExpanded").text = "1"

        # Render state
        renderstate = ET.SubElement(props, "renderstate")

        # Color mask
        colormask = ET.SubElement(renderstate, "colormask")
        for c in ["r", "g", "b", "a"]:
            ET.SubElement(colormask, c).text = "1"
        ET.SubElement(colormask, "uiExpanded").text = "0"

        # Blend state
        blendstate = ET.SubElement(renderstate, "blendstate")
        ET.SubElement(blendstate, "enabled").text = "0"
        ET.SubElement(blendstate, "srcBlendRGB").text = "SRC_ALPHA"
        ET.SubElement(blendstate, "dstBlendRGB").text = "ONE_MINUS_SRC_ALPHA"
        ET.SubElement(blendstate, "srcBlendA").text = "ONE"
        ET.SubElement(blendstate, "dstBlendA").text = "ONE_MINUS_SRC_ALPHA"
        ET.SubElement(blendstate, "equationRGB").text = "ADD"
        ET.SubElement(blendstate, "equationA").text = "ADD"
        ET.SubElement(blendstate, "uiExpanded").text = "0"

        # Cull state
        cullstate = ET.SubElement(renderstate, "cullstate")
        ET.SubElement(cullstate, "enabled").text = "1"
        ET.SubElement(cullstate, "ccw").text = "1"
        ET.SubElement(cullstate, "uiExpanded").text = "0"

        # Depth state
        depthstate = ET.SubElement(renderstate, "depthstate")
        ET.SubElement(depthstate, "enabled").text = "1"
        ET.SubElement(depthstate, "write").text = "1"
        ET.SubElement(depthstate, "func").text = "LESS"
        ET.SubElement(depthstate, "uiExpanded").text = "0"

        # Render target
        rendertarget = ET.SubElement(props, "rendertarget")
        size = ET.SubElement(rendertarget, "size")
        ET.SubElement(size, "x").text = str(render_pass.width)
        ET.SubElement(size, "y").text = str(render_pass.height)
        ET.SubElement(rendertarget, "resolutionMode").text = "PROJECT"
        ET.SubElement(rendertarget, "uiExpanded").text = "1"

        color = ET.SubElement(rendertarget, "color")
        ET.SubElement(color, "format").text = "RGBA32F"
        clear = ET.SubElement(color, "clear")
        self._vec4_to_xml(clear, Vec4(0, 0, 0, 1))
        ET.SubElement(color, "uiExpanded").text = "0"

        depth = ET.SubElement(rendertarget, "depth")
        ET.SubElement(depth, "clear").text = "1"
        ET.SubElement(depth, "uiExpanded").text = "0"

        # Transform
        transform = ET.SubElement(props, "transform")
        ET.SubElement(transform, "uiExpanded").text = "1"

        projection = ET.SubElement(transform, "projection")
        ET.SubElement(projection, "type").text = "0"

        perspective = ET.SubElement(projection, "perspective")
        ET.SubElement(perspective, "fov").text = "60"
        z = ET.SubElement(perspective, "z")
        ET.SubElement(z, "x").text = "0.01"
        ET.SubElement(z, "y").text = "10"

        orthographic = ET.SubElement(projection, "orthographic")
        bounds = ET.SubElement(orthographic, "bounds")
        self._vec4_to_xml(bounds, Vec4(-1, 1, -1, 1))
        z = ET.SubElement(orthographic, "z")
        ET.SubElement(z, "x").text = "-10"
        ET.SubElement(z, "y").text = "10"
        ET.SubElement(projection, "uiExpanded").text = "0"

        view = ET.SubElement(transform, "view")
        eye = ET.SubElement(view, "eye")
        self._vec3_to_xml(eye, Vec3(0, 0, 4))
        center = ET.SubElement(view, "center")
        self._vec3_to_xml(center, Vec3(0, 0, 0))
        up = ET.SubElement(view, "up")
        self._vec3_to_xml(up, Vec3(0, 1, 0))
        ET.SubElement(view, "uiExpanded").text = "0"

        model = ET.SubElement(transform, "model")
        scale = ET.SubElement(model, "scale")
        self._vec3_to_xml(scale, Vec3(1, 1, 1))
        rotate = ET.SubElement(model, "rotate")
        self._vec3_to_xml(rotate, Vec3(0, 0, 0))
        translate = ET.SubElement(model, "translate")
        self._vec3_to_xml(translate, Vec3(0, 0, 0))
        ET.SubElement(model, "uiExpanded").text = "0"

        # Pass parameters
        params = ET.SubElement(pass_elem, "params")
        ET.SubElement(params, "uiExpanded").text = "1"
        for param in render_pass.parameters:
            self._build_parameter_xml(params, param)

        # Stages
        stages = ET.SubElement(pass_elem, "stages")
        for stage in render_pass.stages:
            self._build_shader_stage_xml(stages, stage)

    def _build_passes_xml(self, parent: ET.Element):
        """
        Build passes XML section.

        Args:
            parent: Parent XML element
        """
        passes = ET.SubElement(parent, "passes")
        for render_pass in self.passes:
            self._build_pass_xml(passes, render_pass)

    def build_xml(self) -> str:
        """
        Build the complete XML document.

        Returns:
            XML string representation of the project
        """
        root = ET.Element("klxml")
        root.set("v", str(self.version))
        root.set("a", self.api)

        document = ET.SubElement(root, "document")

        self._build_properties_xml(document)
        self._build_params_xml(document)
        self._build_passes_xml(document)

        # Convert to string with proper formatting
        xml_str = ET.tostring(root, encoding="unicode", method="xml")

        # Add XML declaration
        xml_str = "<?xml version='1.0' encoding='UTF-8'?>" + xml_str

        return xml_str

    def save(self, filename: str):
        """
        Save the project as a .klproj file.

        The file is compressed using zlib compression as required by KodeLife.

        Args:
            filename: Output filename (should end with .klproj)

        Example:
            builder.save("my_shader.klproj")
        """
        xml_str = self.build_xml()
        xml_bytes = xml_str.encode("utf-8")
        compressed = zlib.compress(xml_bytes)

        with open(filename, "wb") as f:
            f.write(compressed)

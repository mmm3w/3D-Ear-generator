bl_info = {
    "name": "3D Ear Generator",
    "author": "Jac Petit-Jean-Boret; Blender 4.2 adaptation",
    "version": (1, 2, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Ear",
    "description": "Create and customize human ears with rig and shape-key controls",
    "category": "Add Mesh",
}

import math
from pathlib import Path

import bpy
from bpy.props import EnumProperty, FloatProperty, PointerProperty, StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .localization import tr


ADDON_DIR = Path(__file__).resolve().parent
ASSET_PATH = ADDON_DIR / "assets" / "ear_reference.blend"
PRESET_DIR = ADDON_DIR / "presets"
INSTANCE_KEY = "ear_generator_instance"
RIG_KEY = "ear_generator_rig"
ROOT_KEY = "ear_generator_root"
APPLIED_KEY = "ear_generator_applied"
SOURCE_KEY = "ear_generator_source_name"

BONE_PROPERTIES = (
    ("my_mainh", "Ear height", 0.7, 1.5, 1.0, "Main", "scale", 0, "01mainh"),
    ("my_mainw", "Ear width", 0.5, 1.6, 1.0, "Main", "scale", 1, "02mainw"),
    ("my_maint", "Ear thickness", 0.5, 1.4, 1.0, "Main", "scale", 2, "03maint"),
    ("my_tops", "Top scale", 0.5, 2.0, 1.0, "Top", "scale", 1, "16tops"),
    ("my_rears", "Rear scale", 0.3, 1.8, 1.0, "Rear", "scale", 0, "17rears"),
    ("my_bottoms", "Bottom scale", 0.3, 2.0, 1.0, "Bottom", "scale", 1, "18bottoms"),
    ("my_mainz", "Ear protrusion", -15.0, 30.0, 0.0, "Main", "rotation_quaternion", 1, "04mainz"),
    ("my_mainy", "Ear verticality", -10.0, 10.0, 0.0, "Main", "rotation_quaternion", 3, "05mainy"),
    ("my_mainx", "Ear tilt", -5.0, 10.0, 0.0, "Main", "rotation_quaternion", 2, "06mainx"),
    ("my_topx", "Top curving X", -7.0, 30.0, 0.0, "Top", "rotation_quaternion", 1, "07topx"),
    ("my_topy", "Top curving Y", -7.0, 30.0, 0.0, "Top", "rotation_quaternion", 2, "08topy"),
    ("my_topz", "Top curving Z", -7.0, 30.0, 0.0, "Top", "rotation_quaternion", 3, "09topz"),
    ("my_bottomx", "Bottom curving X", -10.0, 10.0, 0.0, "Bottom", "rotation_quaternion", 3, "10bottomx"),
    ("my_bottomy", "Bottom curving Y", -10.0, 10.0, 0.0, "Bottom", "rotation_quaternion", 1, "11bottomy"),
    ("my_bottomz", "Bottom curving Z", -10.0, 10.0, 0.0, "Bottom", "rotation_quaternion", 2, "12bottomz"),
    ("my_rearx", "Rear curving X", -20.0, 20.0, 0.0, "Rear", "rotation_quaternion", 3, "13rearx"),
    ("my_reary", "Rear curving Y", -20.0, 20.0, 0.0, "Rear", "rotation_quaternion", 2, "14reary"),
    ("my_rearz", "Rear curving Z", -20.0, 20.0, 0.0, "Rear", "rotation_quaternion", 1, "15rearz"),
)

SHAPE_PROPERTIES = (
    ("my_lobno", "No lobule", "lobno", "22lobno"),
    ("my_lobh", "Lobule max height", "lobh", "21lobh"),
    ("my_lobt", "Lobule thickness", "lobt", "23lobt"),
    ("my_helixp", "Helix sharpness", "helixp", "30helixp"),
    ("my_tuber", "Darwin tubercle", "tuber", "27tuber"),
    ("my_toptub", "Top tubercle", "toptub", "28toptub"),
    ("my_helixt", "Helix thickness", "helixt", "29helixt"),
    ("my_antid", "Antihelix depth", "antid", "25antid"),
    ("my_antir", "Antihelix rear", "antir", "26antir"),
    ("my_tragt", "Tragus thickness", "tragt", "33tragt"),
    ("my_tragh", "Tragus protrusion", "tragh", "31tragh"),
    ("my_tragw", "Tragus width", "tragw", "32tragw"),
    ("my_antit", "Antitragus location", "antit", "34antit"),
    ("my_antin", "Antitragus notch", "antin", "35antin"),
    ("my_anti2", "Double antitragus", "anti2", "37anti2"),
    ("my_conca", "Rear concavity", "conca", "24conca"),
    ("my_notch", "Lobule crease", "notch", "36notch"),
    ("my_lobcr", "Lobule mid crease", "lobcr", "38lobcr"),
    ("my_protr", "Rear protrusion", "protr", "39protr"),
    ("my_rearc", "Root crease", "rearc", "40rearc"),
)

BONE_ROWS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14), (15, 16, 17))
SHAPE_ROWS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14), (15, 16, 17), (18,), (19,))


def bone_update(spec):
    def update(rig, context):
        bone = rig.pose.bones.get(spec[5])
        if bone is None:
            return
        value = getattr(rig, spec[0])
        target = getattr(bone, spec[6])
        target[spec[7]] = math.radians(value) if spec[6] == "rotation_quaternion" else value

    return update


def shape_update(spec):
    def update(ear, context):
        keys = ear.data.shape_keys
        if keys is not None:
            key = keys.key_blocks.get(spec[2])
            if key is not None:
                key.value = getattr(ear, spec[0])

    return update


def collection_tree(collection):
    yield collection
    for child in collection.children:
        yield from collection_tree(child)


def active_ear(context):
    obj = context.active_object
    if obj is None:
        return None
    if obj.get(INSTANCE_KEY):
        return obj
    name = obj.get("ear_generator_ear")
    if name:
        ear = bpy.data.objects.get(name)
        if ear is not None:
            return ear
    return None


def instance_root(ear):
    return bpy.data.collections.get(ear.get(ROOT_KEY, ""))


def instance_rig(ear):
    return bpy.data.objects.get(ear.get(RIG_KEY, ""))


def select_only(context, obj):
    for selected in list(context.selected_objects):
        selected.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def model_template():
    for collection in bpy.data.collections:
        if collection.get("ear_generator_template"):
            return collection
    with bpy.data.libraries.load(str(ASSET_PATH), link=False) as (source, target):
        target.collections = ["Coll all"]
    template = target.collections[0]
    template.use_fake_user = True
    template["ear_generator_template"] = True
    for collection in collection_tree(template):
        collection[SOURCE_KEY] = collection.name
    for obj in template.all_objects:
        obj[SOURCE_KEY] = obj.name
    return template


def clone_collection(source):
    copies = {}

    def clone(source_collection):
        destination = bpy.data.collections.new(source_collection.name)
        destination[SOURCE_KEY] = source_collection.get(SOURCE_KEY, source_collection.name)
        for obj in source_collection.objects:
            duplicate = obj.copy()
            if obj.type in {"MESH", "ARMATURE"}:
                duplicate.data = obj.data.copy()
            copies[obj] = duplicate
            destination.objects.link(duplicate)
        for child in source_collection.children:
            destination.children.link(clone(child))
        destination.hide_viewport = source_collection.hide_viewport
        destination.hide_render = source_collection.hide_render
        return destination

    root = clone(source)
    for original, duplicate in copies.items():
        if original.parent in copies:
            duplicate.parent = copies[original.parent]
        for modifier in duplicate.modifiers:
            if hasattr(modifier, "object") and modifier.object in copies:
                modifier.object = copies[modifier.object]
        for constraint in duplicate.constraints:
            if hasattr(constraint, "target") and constraint.target in copies:
                constraint.target = copies[constraint.target]
    return root


def draw_sliders(context, layout, obj, specs, indices):
    row = layout.row(align=True)
    for index in indices:
        spec = specs[index]
        row.prop(obj, spec[0], text=tr(context, spec[1]), slider=True)


class EarGeneratorSettings(bpy.types.PropertyGroup):
    workdir: StringProperty(name="Work directory", subtype="DIR_PATH", default="")
    language: EnumProperty(
        name="Language / 语言",
        items=(
            ("ZH", "中文", "Use Chinese labels"),
            ("EN", "English", "Use English labels"),
        ),
        default="ZH",
    )


class EAR_GENERATOR_OT_create(bpy.types.Operator):
    bl_idname = "ear_generator.create"
    bl_label = "Create Ear"
    bl_description = "Append a new editable ear from the bundled model"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not ASSET_PATH.is_file():
            self.report({"ERROR"}, f"Missing model asset: {ASSET_PATH}")
            return {"CANCELLED"}
        root = clone_collection(model_template())
        context.scene.collection.children.link(root)
        ear = next((obj for obj in root.all_objects if obj.get(SOURCE_KEY) == "Ear"), None)
        rig = next((obj for obj in root.all_objects if obj.get(SOURCE_KEY) == "Rig-ear"), None)
        if ear is None or rig is None:
            self.report({"ERROR"}, tr(context, "The bundled model is missing its ear or rig"))
            return {"CANCELLED"}
        ear[INSTANCE_KEY] = True
        ear[RIG_KEY] = rig.name
        ear[ROOT_KEY] = root.name
        ear[APPLIED_KEY] = False
        rig["ear_generator_ear"] = ear.name
        rig.hide_set(True)
        rig.hide_render = True
        for spec in BONE_PROPERTIES:
            setattr(rig, spec[0], spec[4])
        for spec in SHAPE_PROPERTIES:
            setattr(ear, spec[0], 0.0)
        context.view_layer.update()
        upright = ear.matrix_basis.copy()
        correction = upright @ ear.matrix_world.inverted()
        rig.matrix_world = correction @ rig.matrix_world
        ear.matrix_world = upright
        select_only(context, ear)
        context.view_layer.update()
        self.report({"INFO"}, tr(context, "Ear created. Select it to edit its parameters."))
        return {"FINISHED"}


class EAR_GENERATOR_OT_toggle_subdivision(bpy.types.Operator):
    bl_idname = "ear_generator.toggle_subdivision"
    bl_label = "Toggle Subdivision"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ear = active_ear(context)
        modifier = ear.modifiers.get("Subdivision") if ear else None
        if modifier is None:
            self.report({"WARNING"}, "Subdivision is unavailable after applying the ear")
            return {"CANCELLED"}
        modifier.show_viewport = not modifier.show_viewport
        modifier.show_render = modifier.show_viewport
        return {"FINISHED"}


class EAR_GENERATOR_OT_reset_bones(bpy.types.Operator):
    bl_idname = "ear_generator.reset_bones"
    bl_label = "Reset Proportions and Orientations"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ear = active_ear(context)
        rig = instance_rig(ear) if ear else None
        if rig is None or ear.get(APPLIED_KEY):
            return {"CANCELLED"}
        for spec in BONE_PROPERTIES:
            setattr(rig, spec[0], spec[4])
        context.view_layer.update()
        return {"FINISHED"}


class EAR_GENERATOR_OT_reset_regions(bpy.types.Operator):
    bl_idname = "ear_generator.reset_regions"
    bl_label = "Reset Regions and Shapes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ear = active_ear(context)
        if ear is None or ear.get(APPLIED_KEY):
            return {"CANCELLED"}
        for spec in SHAPE_PROPERTIES:
            setattr(ear, spec[0], 0.0)
        context.view_layer.update()
        return {"FINISHED"}


class EAR_GENERATOR_OT_load_preset(bpy.types.Operator, ImportHelper):
    bl_idname = "ear_generator.load_preset"
    bl_label = "Load Ear Preset"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".ear"
    filter_glob: StringProperty(default="*.ear", options={"HIDDEN"})

    def invoke(self, context, event):
        workdir = context.scene.ear_generator.workdir
        self.filepath = str(Path(workdir) if workdir else PRESET_DIR)
        return super().invoke(context, event)

    def execute(self, context):
        ear = active_ear(context)
        rig = instance_rig(ear) if ear else None
        if rig is None or ear.get(APPLIED_KEY):
            self.report({"WARNING"}, tr(context, "Select an editable ear first"))
            return {"CANCELLED"}
        try:
            values = [float(line.strip()) for line in Path(self.filepath).read_text(encoding="utf-8").splitlines() if line.strip()]
        except (OSError, ValueError) as exc:
            self.report({"ERROR"}, f"Cannot read preset: {exc}")
            return {"CANCELLED"}
        expected = len(BONE_PROPERTIES) + len(SHAPE_PROPERTIES)
        if len(values) != expected or not all(math.isfinite(value) for value in values):
            self.report({"ERROR"}, tr(context, "Preset must contain exactly 38 finite values"))
            return {"CANCELLED"}
        for spec, value in zip(BONE_PROPERTIES, values):
            setattr(rig, spec[0], value)
        for spec, value in zip(SHAPE_PROPERTIES, values[len(BONE_PROPERTIES):]):
            setattr(ear, spec[0], value)
        context.scene.ear_generator.workdir = str(Path(self.filepath).resolve().parent)
        context.view_layer.update()
        self.report({"INFO"}, f"Loaded {Path(self.filepath).name}")
        return {"FINISHED"}


class EAR_GENERATOR_OT_save_preset(bpy.types.Operator, ExportHelper):
    bl_idname = "ear_generator.save_preset"
    bl_label = "Save Ear Preset"
    bl_options = {"REGISTER"}

    filename_ext = ".ear"
    filter_glob: StringProperty(default="*.ear", options={"HIDDEN"})

    def invoke(self, context, event):
        workdir = context.scene.ear_generator.workdir
        self.filepath = str(Path(workdir) / "my_ear.ear") if workdir else "my_ear.ear"
        return super().invoke(context, event)

    def execute(self, context):
        ear = active_ear(context)
        rig = instance_rig(ear) if ear else None
        if rig is None:
            self.report({"WARNING"}, tr(context, "Select an ear first"))
            return {"CANCELLED"}
        values = [getattr(rig, spec[0]) for spec in BONE_PROPERTIES]
        values.extend(getattr(ear, spec[0]) for spec in SHAPE_PROPERTIES)
        try:
            path = Path(self.filepath)
            path.write_text("\n".join(str(value) for value in values), encoding="utf-8")
        except OSError as exc:
            self.report({"ERROR"}, f"Cannot save preset: {exc}")
            return {"CANCELLED"}
        context.scene.ear_generator.workdir = str(path.resolve().parent)
        self.report({"INFO"}, f"Saved {path.name}")
        return {"FINISHED"}


class EAR_GENERATOR_OT_apply(bpy.types.Operator):
    bl_idname = "ear_generator.apply"
    bl_label = "Apply All Changes"
    bl_description = "Bake rig, shape keys and visible subdivision into a standalone mesh; this cannot be edited with the sliders afterward"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ear = active_ear(context)
        if ear is None:
            self.report({"WARNING"}, tr(context, "Select an ear first"))
            return {"CANCELLED"}
        if ear.get(APPLIED_KEY):
            self.report({"WARNING"}, tr(context, "This ear has already been applied"))
            return {"CANCELLED"}
        rig = instance_rig(ear)
        root = instance_root(ear)
        select_only(context, ear)
        if context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        context.view_layer.update()
        evaluated = ear.evaluated_get(context.evaluated_depsgraph_get())
        mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=context.evaluated_depsgraph_get())
        old_mesh = ear.data
        matrix = ear.matrix_world.copy()
        ear.modifiers.clear()
        ear.data = mesh
        ear.parent = None
        ear.matrix_world = matrix
        ear[APPLIED_KEY] = True
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
        if rig is not None:
            armature = rig.data
            bpy.data.objects.remove(rig, do_unlink=True)
            if armature.users == 0:
                bpy.data.armatures.remove(armature)
        if root is not None:
            if ear.name not in context.scene.collection.objects:
                context.scene.collection.objects.link(ear)
            for collection in reversed(list(collection_tree(root))):
                bpy.data.collections.remove(collection)
        for key in (RIG_KEY, ROOT_KEY):
            if key in ear:
                del ear[key]
        select_only(context, ear)
        self.report({"INFO"}, tr(context, "Ear baked to a standalone mesh"))
        return {"FINISHED"}


class EAR_GENERATOR_PT_panel(bpy.types.Panel):
    bl_label = "3D Ear Generator"
    bl_idname = "EAR_GENERATOR_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Ear"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ear_generator
        layout.prop(settings, "language", text="Language / 语言")
        layout.label(text=tr(context, "Work directory"))
        layout.prop(settings, "workdir", text="")
        layout.operator("ear_generator.create", text=tr(context, "Create Ear"), icon="ADD")
        ear = active_ear(context)
        if ear is None:
            layout.label(text=tr(context, "Create or select an ear to edit it."))
            return
        if ear.get(APPLIED_KEY):
            layout.label(text=tr(context, "This ear has been applied."), icon="INFO")
        else:
            layout.operator("ear_generator.toggle_subdivision", text=tr(context, "Subdivision"))
        rig = instance_rig(ear)
        editable = rig is not None and not ear.get(APPLIED_KEY)
        bones = layout.box()
        bones.label(text=tr(context, "Whole ear proportions and orientations"))
        bones.enabled = editable
        if rig is not None:
            for indices in BONE_ROWS:
                draw_sliders(context, bones, rig, BONE_PROPERTIES, indices)
        bones.operator("ear_generator.reset_bones", text=tr(context, "Reset Proportions and Orientations"))
        regions = layout.box()
        regions.label(text=tr(context, "Ear regions and specific shapes"))
        regions.enabled = editable
        for indices in SHAPE_ROWS:
            draw_sliders(context, regions, ear, SHAPE_PROPERTIES, indices)
        regions.operator("ear_generator.reset_regions", text=tr(context, "Reset Regions and Shapes"))
        presets = layout.row(align=True)
        presets.enabled = editable
        presets.operator("ear_generator.load_preset", text=tr(context, "Load preset"))
        presets.operator("ear_generator.save_preset", text=tr(context, "Save preset"))
        layout.operator("ear_generator.apply", text=tr(context, "Apply All Changes"))


CLASSES = (
    EarGeneratorSettings,
    EAR_GENERATOR_OT_create,
    EAR_GENERATOR_OT_toggle_subdivision,
    EAR_GENERATOR_OT_reset_bones,
    EAR_GENERATOR_OT_reset_regions,
    EAR_GENERATOR_OT_load_preset,
    EAR_GENERATOR_OT_save_preset,
    EAR_GENERATOR_OT_apply,
    EAR_GENERATOR_PT_panel,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ear_generator = PointerProperty(type=EarGeneratorSettings)
    for spec in BONE_PROPERTIES:
        prop = FloatProperty(
            name=spec[1],
            min=spec[2],
            max=spec[3],
            default=spec[4],
            update=bone_update(spec),
        )
        setattr(bpy.types.Object, spec[0], prop)
    for spec in SHAPE_PROPERTIES:
        prop = FloatProperty(
            name=spec[1],
            min=0.0,
            max=1.0,
            soft_min=0.0,
            soft_max=1.0,
            default=0.0,
            update=shape_update(spec),
        )
        setattr(bpy.types.Object, spec[0], prop)


def unregister():
    for spec in SHAPE_PROPERTIES:
        delattr(bpy.types.Object, spec[0])
    for spec in BONE_PROPERTIES:
        delattr(bpy.types.Object, spec[0])
    del bpy.types.Scene.ear_generator
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

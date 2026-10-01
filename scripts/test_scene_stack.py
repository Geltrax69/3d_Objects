"""Test scene v2: stacked rectangle (box), circle (disc), cylinder + 3D 'APPLE' text.

Proper Z-up layout so the .glb imports cleanly into Spline / Blender.
Run headless:
    blender --background --python test_scene_stack.py

Outputs:
    ~/workspace/3d model/exports/test_scene.glb
    ~/workspace/3d model/renders/test_scene_*.png
"""
import bpy
import math
import os

HOME = os.path.expanduser("~")
WS = os.path.join(HOME, "workspace", "3d model")
EXPORT_GLB = os.path.join(WS, "exports", "test_scene.glb")
EXPORT_BG = os.path.join(WS, "exports", "background.glb")
EXPORT_TEXT = os.path.join(WS, "exports", "apple_text.glb")
RENDER_A = os.path.join(WS, "renders", "test_scene_angle1.png")
RENDER_B = os.path.join(WS, "renders", "test_scene_angle2.png")
os.makedirs(os.path.dirname(EXPORT_GLB), exist_ok=True)
os.makedirs(os.path.dirname(RENDER_A), exist_ok=True)

# ---------------------------------------------------------------- clear scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
    for x in list(coll):
        coll.remove(x)


def make_mat(name, rgb, roughness=0.55, metallic=0.0):
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m


MAT_BOX = make_mat("Mat_Rectangle", (0.80, 0.30, 0.18))          # terracotta
MAT_DISC = make_mat("Mat_Circle", (0.14, 0.14, 0.16), 0.35)       # near-black
MAT_CYL = make_mat("Mat_Cylinder", (0.15, 0.47, 0.70))            # blue
MAT_TEXT = make_mat("Mat_Text", (0.96, 0.93, 0.86), 0.45)         # warm white
MAT_GROUND = make_mat("Mat_Ground", (0.93, 0.92, 0.90), 0.9)      # studio floor


def finish(obj, name, material):
    obj.name = name
    obj.data.materials.append(material)
    return obj


# ------------------------------------------------- the stack (bottom -> top)
# 1. rectangle -> box, sitting on the ground (z: 0 -> 1)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
box = bpy.context.active_object
box.scale = (3.2, 2.4, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
finish(box, "Rectangle", MAT_BOX)

# 2. circle -> flat disc (z: 1.0 -> 1.3), fits fully on the box
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.15, depth=0.3,
                                    location=(0, 0, 1.15))
finish(bpy.context.active_object, "Circle", MAT_DISC)

# 3. cylinder (z: 1.3 -> 2.7)
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.9, depth=1.4,
                                    location=(0, 0, 2.0))
finish(bpy.context.active_object, "Cylinder", MAT_CYL)

# ------------------------------------------------------- 3D text: APPLE
# stands on the ground in front of the stack, facing the camera (-Y)
bpy.ops.object.text_add(location=(0, -3.4, 0.55))
txt = bpy.context.active_object
txt.name = "APPLE_Text"
txt.rotation_euler = (math.radians(90), 0, 0)  # face -Y, up stays +Z
td = txt.data
td.body = "APPLE"
td.size = 1.15
td.align_x = "CENTER"
td.align_y = "CENTER"
td.extrude = 0.3
td.bevel_depth = 0.035
td.bevel_resolution = 2
# convert to mesh so it exports cleanly to glTF
bpy.ops.object.select_all(action="DESELECT")
txt.select_set(True)
bpy.context.view_layer.objects.active = txt
bpy.ops.object.convert(target="MESH")
finish(bpy.context.active_object, "APPLE_Text", MAT_TEXT)

# ------------------------------------------------------------- studio floor
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
finish(bpy.context.active_object, "Ground", MAT_GROUND)

# ------------------------------------------------------------------ lights
def area_light(name, loc, energy, size=4.0, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.active_object
    l.name = name
    l.data.energy = energy
    l.data.size = size
    l.data.color = color
    return l

area_light("Key", (6, -4, 8), 700, size=5.0)
area_light("Fill", (-6, -2, 5), 250, size=4.0, color=(0.9, 0.95, 1.0))
area_light("Rim", (0, 6, 6), 450, size=3.0)

world = bpy.context.scene.world
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.96, 0.96, 0.97, 1.0)
bg.inputs["Strength"].default_value = 0.85

# ------------------------------------------------------------------ camera
# NOTE: orient the camera directly with to_track_quat (a TRACK_TO constraint
# with up_axis="UP_Z" is degenerate when tracking -Z, and aims wrong).
bpy.ops.object.camera_add(location=(7.5, -7.5, 5.0))
cam = bpy.context.active_object
cam.name = "Camera"
bpy.context.scene.camera = cam
cam.data.lens = 40

import mathutils


def aim(cam_loc, target_loc):
    cam.location = cam_loc
    direction = (mathutils.Vector(target_loc)
                 - mathutils.Vector(cam_loc))
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


TARGET = (0, 0, 1.3)

# ------------------------------------------------------------------ render
# NOTE: EEVEE needs EGL/OpenGL libs not present on this VM, so previews
# render with Cycles on CPU (headless-safe).
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.film_transparent = False


def render_to(path, cam_loc):
    aim(cam_loc, TARGET)
    bpy.context.view_layer.update()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered:", path)


if os.environ.get("SKIP_RENDER") != "1":
    render_to(RENDER_A, (7.5, -7.5, 5.0))
    render_to(RENDER_B, (-7.0, -6.0, 4.2))


# ------------------------------------------------------------------- export
# Three files:
#   test_scene.glb  -> everything (stack + text)
#   background.glb  -> the stack only (rectangle, circle, cylinder, ground)
#   apple_text.glb  -> the APPLE text only (separate, movable object)
def export_selected(obj_names, filepath):
    bpy.ops.object.select_all(action="DESELECT")
    for n in obj_names:
        bpy.data.objects[n].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[obj_names[0]]
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_materials="EXPORT",
        use_selection=True,
        export_cameras=False,
        export_lights=False,
    )
    print("exported:", filepath)


export_selected(["Rectangle", "Circle", "Cylinder", "Ground"], EXPORT_BG)
export_selected(["APPLE_Text"], EXPORT_TEXT)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=EXPORT_GLB,
    export_format="GLB",
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
)
print("exported:", EXPORT_GLB)

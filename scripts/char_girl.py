"""Low-poly girl character (red hair, olive coat, lace-up boots) - detailed build.

Reference: character turnaround (front/side/back) supplied by the user.
Run headless:
    blender --background --python char_girl.py
Set SKIP_RENDER=1 to skip preview renders and only export the .glb.

Outputs:
    ~/workspace/3d model/exports/characters/girl_redhair.glb
    ~/workspace/3d model/renders/characters/girl_front.png
    ~/workspace/3d model/renders/characters/girl_back.png

Character faces +Y. Units ~meters, total height ~3.2.
"""
import bpy
import math
import os
from mathutils import Vector

HOME = os.path.expanduser("~")
WS = os.path.join(HOME, "workspace", "3d model")
EXPORT_GLB = os.path.join(WS, "exports", "characters", "girl_redhair.glb")
RENDER_FRONT = os.path.join(WS, "renders", "characters", "girl_front.png")
RENDER_BACK = os.path.join(WS, "renders", "characters", "girl_back.png")
os.makedirs(os.path.dirname(EXPORT_GLB), exist_ok=True)
os.makedirs(os.path.dirname(RENDER_FRONT), exist_ok=True)

# ---------------------------------------------------------------- clear scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
    for x in list(coll):
        coll.remove(x)

CHAR = []  # character objects (ground/lights excluded from export)


def make_mat(name, rgb, roughness=0.65):
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


MAT = {
    "hair": make_mat("Mat_Hair", (0.62, 0.13, 0.08), 0.55),
    "hair_dark": make_mat("Mat_HairDark", (0.44, 0.10, 0.07), 0.6),
    "skin": make_mat("Mat_Skin", (0.96, 0.82, 0.71), 0.6),
    "skin_shade": make_mat("Mat_SkinShade", (0.88, 0.70, 0.60), 0.6),
    "eye": make_mat("Mat_Eye", (0.13, 0.10, 0.10), 0.25),
    "eye_white": make_mat("Mat_EyeWhite", (0.97, 0.97, 0.97), 0.3),
    "coat": make_mat("Mat_Coat", (0.55, 0.58, 0.37), 0.7),
    "coat_dark": make_mat("Mat_CoatDark", (0.45, 0.48, 0.30), 0.7),
    "dark": make_mat("Mat_Dark", (0.15, 0.12, 0.20), 0.6),
    "cuff": make_mat("Mat_Cuff", (0.88, 0.90, 0.92), 0.75),
    "boot": make_mat("Mat_Boot", (0.70, 0.53, 0.31), 0.65),
    "lace": make_mat("Mat_Lace", (0.42, 0.30, 0.17), 0.7),
    "mouth": make_mat("Mat_Mouth", (0.72, 0.38, 0.33), 0.6),
    "ground": make_mat("Mat_Ground", (0.93, 0.92, 0.90), 0.9),
}


def finish(obj, name, material, char=True):
    obj.name = name
    obj.data.materials.append(material)
    # faceted low-poly look
    for p in obj.data.polygons:
        p.use_smooth = False
    if char:
        CHAR.append(obj)
    return obj


def ball(loc, sx, sy, sz, material, name, seg=12, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=rings, radius=1.0, location=loc)
    obj = bpy.context.active_object
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, material)


def box(loc, dims, material, name, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.scale = dims
    if rot:
        obj.rotation_euler = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, material)


def limb(p1, p2, r1, r2, material, name, verts=10):
    """Tapered cylinder from p1 (radius r1) to p2 (radius r2)."""
    v1, v2 = Vector(p1), Vector(p2)
    d = v2 - v1
    mid = (v1 + v2) / 2
    bpy.ops.mesh.primitive_cone_add(
        vertices=verts, radius1=r1, radius2=r2, depth=d.length, location=mid)
    obj = bpy.context.active_object
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return finish(obj, name, material)


# ================================================================== HEAD
ball((0, 0, 2.78), 0.30, 0.28, 0.34, MAT["skin"], "Head", seg=14, rings=10)
# jaw taper: slight chin
ball((0, 0.03, 2.62), 0.24, 0.22, 0.20, MAT["skin"], "Chin", seg=10, rings=8)
# ears
ball((0.29, 0, 2.78), 0.05, 0.06, 0.08, MAT["skin"], "Ear_L", seg=8, rings=6)
ball((-0.29, 0, 2.78), 0.05, 0.06, 0.08, MAT["skin"], "Ear_R", seg=8, rings=6)
# neck
limb((0, 0, 2.30), (0, 0, 2.52), 0.10, 0.09, MAT["skin"], "Neck")

# ------------------------------------------------------------------ face
# eyes: dark anime eyes with white highlights
for sx in (1, -1):
    x = 0.115 * sx
    ball((x, 0.235, 2.82), 0.075, 0.05, 0.10, MAT["eye"], f"Eye_{'R' if sx>0 else 'L'}", seg=10, rings=8)
    ball((x + 0.015 * sx, 0.26, 2.865), 0.02, 0.016, 0.02, MAT["eye_white"],
         f"EyeGlint_{'R' if sx>0 else 'L'}", seg=8, rings=6)
    # eyebrows: thin angled boxes
    box((x, 0.25, 2.965), (0.15, 0.025, 0.03), MAT["hair_dark"],
        f"Brow_{'R' if sx>0 else 'L'}", rot=(0, 0.18 * -sx, 0))
# nose: tiny wedge
box((0, 0.275, 2.70), (0.035, 0.025, 0.035), MAT["skin_shade"], "Nose")
# mouth: small muted-red bar
box((0, 0.265, 2.615), (0.10, 0.02, 0.018), MAT["mouth"], "Mouth")

# ================================================================== HAIR
# back mass: tapered, flattened
bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.30, radius2=0.20,
                                depth=1.05, location=(0, -0.20, 2.28))
back = bpy.context.active_object
back.scale = (1.0, 0.62, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
finish(back, "Hair_Back", MAT["hair"])
# hair cap over the skull
ball((0, -0.03, 2.86), 0.335, 0.315, 0.375, MAT["hair"], "Hair_Cap", seg=14, rings=10)
# darker under-layer visible at the fringe
ball((0, -0.06, 2.72), 0.30, 0.28, 0.33, MAT["hair_dark"], "Hair_Under", seg=12, rings=8)
# side locks framing the face
for sx in (1, -1):
    box((0.30 * sx, 0.03, 2.52), (0.11, 0.16, 0.55), MAT["hair"],
        f"HairLock_{'R' if sx>0 else 'L'}", rot=(0, 0.06 * sx, 0))
# bangs: 5 wedges across the forehead
for i, bx in enumerate((-0.20, -0.10, 0.0, 0.10, 0.20)):
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.085, radius2=0.012,
                                    depth=0.30, location=(bx, 0.245, 2.98))
    bang = bpy.context.active_object
    bang.rotation_euler = (math.radians(180), 0, bx * 1.2)  # point down, fan out
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(bang, f"Bang_{i}", MAT["hair"])
# (no ahoge - kept the silhouette clean like the reference)

# ============================================================== COAT / BODY
# tunic: tapered cylinder, slightly flattened front-back
bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.46, radius2=0.32,
                                depth=1.10, location=(0, 0, 1.80))
coat = bpy.context.active_object
coat.scale = (1.0, 0.82, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
finish(coat, "Coat", MAT["coat"])
# hood/collar ring resting on shoulders
bpy.ops.mesh.primitive_torus_add(major_radius=0.20, minor_radius=0.085,
                                 major_segments=12, minor_segments=8,
                                 location=(0, 0, 2.38))
hood = bpy.context.active_object
hood.scale = (1.0, 0.9, 0.7)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
finish(hood, "Hood", MAT["coat_dark"])
# coat buttons
for bz in (2.12, 1.92):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.032, depth=0.02,
                                        location=(0, 0.285, bz))
    btn = bpy.context.active_object
    btn.rotation_euler = (math.radians(90), 0, 0)
    finish(btn, f"Button_{bz}", MAT["dark"])

# ------------------------------------------------------------------ arms
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    sh = (0.34 * sx, 0, 2.18)
    wr = (0.60 * sx, 0, 1.80)
    limb(sh, wr, 0.105, 0.085, MAT["coat"], f"Sleeve_{s}")
    # flared sleeve cuff
    limb((0.565 * sx, 0, 1.845), (0.615 * sx, 0, 1.775), 0.085, 0.115,
         MAT["coat_dark"], f"SleeveCuff_{s}")
    # glove
    ball((0.64 * sx, 0, 1.68), 0.085, 0.10, 0.115, MAT["dark"], f"Glove_{s}", seg=10, rings=8)

# ------------------------------------------------------------------ legs
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    x = 0.14 * sx
    limb((x, 0, 1.50), (x, 0, 0.80), 0.105, 0.095, MAT["dark"], f"Leg_{s}")
    # white folded cuff / leg warmer
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.135, radius2=0.16,
                                    depth=0.28, location=(x, 0, 0.68))
    cuff = bpy.context.active_object
    finish(cuff, f"BootCuff_{s}", MAT["cuff"])
    # boot shaft
    limb((x, 0, 0.58), (x, 0, 0.22), 0.125, 0.115, MAT["boot"], f"Boot_{s}", verts=12)
    # boot foot
    box((x, 0.15, 0.13), (0.24, 0.52, 0.20), MAT["boot"], f"BootFoot_{s}")
    # crisscross laces on the boot front
    for j, lz in enumerate((0.36, 0.45, 0.54)):
        for ang in (0.6, -0.6):
            box((x, 0.128, lz), (0.17, 0.018, 0.028), MAT["lace"],
                f"Lace_{s}_{j}_{1 if ang > 0 else 0}", rot=(0, 0, ang))

# ================================================================ staging
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
finish(bpy.context.active_object, "Ground", MAT["ground"], char=False)


def area_light(name, loc, energy, size=4.0, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.active_object
    l.name = name
    l.data.energy = energy
    l.data.size = size
    l.data.color = color
    return l


area_light("Key", (5, -4, 7), 450, size=5.0)
area_light("Fill", (-5, -3, 4), 160, size=4.0, color=(0.9, 0.95, 1.0))
area_light("Rim", (0, 6, 5), 300, size=3.0)

world = bpy.context.scene.world
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.96, 0.96, 0.97, 1.0)
bg.inputs["Strength"].default_value = 0.55

# ------------------------------------------------------------------ camera
import mathutils

bpy.ops.object.camera_add(location=(4.2, -5.8, 3.0))
cam = bpy.context.active_object
cam.name = "Camera"
bpy.context.scene.camera = cam
cam.data.lens = 42
TARGET = (0, 0, 1.55)


def aim(cam_loc):
    cam.location = cam_loc
    direction = mathutils.Vector(TARGET) - mathutils.Vector(cam_loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


# ------------------------------------------------------------------ render
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
    aim(cam_loc)
    bpy.context.view_layer.update()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered:", path)


if os.environ.get("SKIP_RENDER") != "1":
    render_to(RENDER_FRONT, (4.2, 5.8, 3.0))
    render_to(RENDER_BACK, (-4.2, -5.8, 3.2))

# ------------------------------------------------------------------- export
# character only (no ground / lights)
bpy.ops.object.select_all(action="DESELECT")
for o in CHAR:
    o.select_set(True)
bpy.context.view_layer.objects.active = CHAR[0]
bpy.ops.export_scene.gltf(
    filepath=EXPORT_GLB,
    export_format="GLB",
    export_materials="EXPORT",
    use_selection=True,
    export_cameras=False,
    export_lights=False,
)
print("exported:", EXPORT_GLB)

"""Low-poly girl character v5 - rebuilt to match the reference turnaround.

Reference: red-haired girl, olive hooded A-line coat, arms angled outward,
dark leggings/gloves, white boot cuffs, tan lace-up boots.

Geometry-first rebuild: trapezoid coat with real hood, parted broad-section
hair, outward-angled arms, slim tapered boots. Orthographic front camera
for reference comparison.

Run headless:
    blender --background --python char_girl.py
Set SKIP_RENDER=1 to skip preview renders and only export the .glb.

Outputs:
    ~/workspace/3d model/exports/characters/girl_redhair.glb
    ~/workspace/3d model/renders/characters/girl_front.png  (orthographic)
    ~/workspace/3d model/renders/characters/girl_angle.png   (3/4 perspective)
    ~/workspace/3d model/renders/characters/girl_side.png    (orthographic)
    ~/workspace/3d model/renders/characters/girl_back.png    (orthographic)

Shading: smooth on all organic surfaces (face, hair, coat, limbs, boots)
with sharp edges only where rims must stay crisp — low-poly geometry,
clean smooth render, matching the reference's surface quality.

Character faces +Y. Total height ~3.35.
"""
import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector

HOME = os.path.expanduser("~")
WS = os.path.join(HOME, "workspace", "3d model")
EXPORT_GLB = os.path.join(WS, "exports", "characters", "girl_redhair.glb")
RENDER_FRONT = os.path.join(WS, "renders", "characters", "girl_front.png")
RENDER_ANGLE = os.path.join(WS, "renders", "characters", "girl_angle.png")
RENDER_SIDE = os.path.join(WS, "renders", "characters", "girl_side.png")
RENDER_BACK = os.path.join(WS, "renders", "characters", "girl_back.png")
os.makedirs(os.path.dirname(EXPORT_GLB), exist_ok=True)
os.makedirs(os.path.dirname(RENDER_FRONT), exist_ok=True)

# ---------------------------------------------------------------- clear scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
    for x in list(coll):
        coll.remove(x)

CHAR = []  # character objects (staging excluded from export)


def make_mat(name, rgb, roughness=0.7):
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


MAT = {
    "hair": make_mat("Mat_Hair", (0.66, 0.20, 0.10), 0.6),
    "hair_dark": make_mat("Mat_HairDark", (0.46, 0.12, 0.08), 0.65),
    "skin": make_mat("Mat_Skin", (0.96, 0.82, 0.71), 0.65),
    "skin_shade": make_mat("Mat_SkinShade", (0.87, 0.70, 0.60), 0.65),
    "eye": make_mat("Mat_Eye", (0.12, 0.10, 0.10), 0.3),
    "eye_white": make_mat("Mat_EyeWhite", (0.97, 0.97, 0.97), 0.35),
    "coat": make_mat("Mat_Coat", (0.32, 0.35, 0.16), 0.8),
    "coat_dark": make_mat("Mat_CoatDark", (0.24, 0.26, 0.12), 0.8),
    "dark": make_mat("Mat_Dark", (0.13, 0.11, 0.20), 0.65),
    "cuff": make_mat("Mat_Cuff", (0.90, 0.90, 0.88), 0.8),
    "boot": make_mat("Mat_Boot", (0.66, 0.50, 0.30), 0.7),
    "lace": make_mat("Mat_Lace", (0.40, 0.28, 0.16), 0.75),
    "mouth": make_mat("Mat_Mouth", (0.70, 0.38, 0.33), 0.65),
    "ground": make_mat("Mat_Ground", (0.93, 0.92, 0.90), 0.9),
}


def finish(obj, name, material, char=True, smooth=True):
    obj.name = name
    obj.data.materials.append(material)
    for p in obj.data.polygons:
        p.use_smooth = smooth
    if char:
        CHAR.append(obj)
    return obj


def apply_all(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def sharpen(obj, angle_deg=35):
    """Mark edges sharper than angle_deg as sharp, so smooth shading keeps
    crisp rims (hem, cuffs, segment joints) while faces shade smoothly."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.edges.ensure_lookup_table()
    limit = math.radians(angle_deg)
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle() > limit:
            e.smooth = False
    bm.to_mesh(me)
    bm.free()
    me.update()
    return obj


def ball(loc, sx, sy, sz, material, name, seg=16, rings=12, smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=rings, radius=1.0, location=loc)
    obj = bpy.context.active_object
    obj.scale = (sx, sy, sz)
    apply_all(obj)
    return finish(obj, name, material, smooth=smooth)


def box(loc, dims, material, name, rot=None, smooth=True):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.scale = dims
    if rot:
        obj.rotation_euler = rot
    apply_all(obj)
    return finish(obj, name, material, smooth=smooth)


def tapered_lock(loc, dims, taper, material, name, rot=None, smooth=True,
                sharp_angle=30):
    """Box whose local -Z (tip) end is narrowed by `taper` - molded, not blunt."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.scale = dims
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    zmin = min(v.co.z for v in bm.verts)
    for v in bm.verts:
        if v.co.z < zmin + 0.001:
            v.co.x *= taper
            v.co.y *= taper
    bm.to_mesh(me)
    bm.free()
    me.update()
    if rot:
        obj.rotation_euler = rot
    apply_all(obj)
    finish(obj, name, material, smooth=smooth)
    if smooth:
        sharpen(obj, sharp_angle)
    return obj


def limb(p1, p2, r1, r2, material, name, verts=12, smooth=True,
         sharp_angle=40):
    """Tapered low-poly limb from p1 (radius r1) to p2 (radius r2)."""
    v1, v2 = Vector(p1), Vector(p2)
    d = v2 - v1
    mid = (v1 + v2) / 2
    bpy.ops.mesh.primitive_cone_add(
        vertices=verts, radius1=r1, radius2=r2, depth=d.length, location=mid)
    obj = bpy.context.active_object
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    apply_all(obj)
    finish(obj, name, material, smooth=smooth)
    if smooth:
        sharpen(obj, sharp_angle)
    return obj


# ================================================================== HEAD
ball((0, 0, 2.86), 0.34, 0.32, 0.36, MAT["skin"], "Head")
ball((0, 0.02, 2.68), 0.27, 0.25, 0.22, MAT["skin"], "Chin", seg=12, rings=8)
ball((0.325, 0, 2.86), 0.055, 0.06, 0.085, MAT["skin"], "Ear_R", seg=8, rings=6)
ball((-0.325, 0, 2.86), 0.055, 0.06, 0.085, MAT["skin"], "Ear_L", seg=8, rings=6)
limb((0, 0, 2.34), (0, 0, 2.58), 0.105, 0.095, MAT["skin"], "Neck")

# ------------------------------------------------------------------ face
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    x = 0.14 * sx
    # large dark anime eye
    ball((x, 0.275, 2.90), 0.10, 0.06, 0.13, MAT["eye"], f"Eye_{s}", seg=12, rings=10)
    # glint
    ball((x - 0.025 * sx, 0.315, 2.955), 0.024, 0.02, 0.024, MAT["eye_white"],
         f"EyeGlint_{s}", seg=8, rings=6)
    # upper lash line
    box((x, 0.29, 3.00), (0.20, 0.03, 0.035), MAT["eye"], f"Lash_{s}",
        rot=(0.1, 0, -0.12 * sx), smooth=False)
    # brow
    box((x, 0.285, 3.10), (0.16, 0.028, 0.032), MAT["hair_dark"], f"Brow_{s}",
        rot=(0, 0, -0.15 * sx), smooth=False)
box((0, 0.315, 2.80), (0.035, 0.025, 0.035), MAT["skin_shade"], "Nose",
    smooth=False)
box((0, 0.30, 2.71), (0.095, 0.02, 0.02), MAT["mouth"], "Mouth", smooth=False)

# ================================================================== HAIR
# skull cap
ball((0, -0.05, 2.94), 0.375, 0.35, 0.395, MAT["hair"], "Hair_Cap")
# darker under-layer at the hairline
ball((0, -0.07, 2.80), 0.335, 0.31, 0.35, MAT["hair_dark"], "Hair_Under", seg=14, rings=10)

# parted fringe: two molded tapered sweeps from a center part
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    tapered_lock((0.13 * sx, 0.25, 3.03), (0.24, 0.07, 0.28), 0.45,
                 MAT["hair"], f"Fringe_{s}", rot=(0.22, 0, -0.5 * sx))
# small center wedge at the part
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.075, radius2=0.015,
                                depth=0.26, location=(0, 0.29, 3.02))
part = bpy.context.active_object
part.rotation_euler = (math.radians(180), math.radians(45), 0)
apply_all(part)
finish(part, "Fringe_Center", MAT["hair"])
sharpen(part, 30)

# large side sections framing the face in front of the shoulders
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    tapered_lock((0.30 * sx, 0.06, 2.25), (0.22, 0.16, 0.90), 0.8,
                 MAT["hair"], f"HairSide_{s}", rot=(0, -0.14 * sx, 0))

# broad tapered slab down the back (diamond cross-section -> flat faces)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.30, radius2=0.38,
                                depth=1.05, location=(0, -0.22, 2.08))
back = bpy.context.active_object
back.rotation_euler = (0, 0, math.radians(45))
bpy.context.view_layer.objects.active = back
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
back.scale = (1.0, 0.5, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
finish(back, "Hair_Back", MAT["hair"])
sharpen(back, 30)

# ============================================================== COAT (A-line)
# trapezoid torso: narrow shoulders -> wide hem
bpy.ops.mesh.primitive_cone_add(vertices=14, radius1=0.55, radius2=0.35,
                                depth=1.15, location=(0, 0, 1.775))
coat = bpy.context.active_object
coat.scale = (1.0, 0.85, 1.0)
apply_all(coat)
finish(coat, "Coat", MAT["coat"])
sharpen(coat, 35)

# chunky draped hood collar around the neck (reads as a hood, not a scarf)
bpy.ops.mesh.primitive_torus_add(major_radius=0.23, minor_radius=0.11,
                                 major_segments=14, minor_segments=10,
                                 location=(0, 0, 2.40))
cowl = bpy.context.active_object
cowl.scale = (1.0, 0.9, 0.7)
apply_all(cowl)
finish(cowl, "Cowl", MAT["coat_dark"])
# resting hood lump behind the neck
ball((0, -0.20, 2.44), 0.27, 0.17, 0.20, MAT["coat_dark"], "Hood", seg=12, rings=8)
# shoulder caps to soften the arm join
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    ball((0.36 * sx, 0, 2.24), 0.16, 0.14, 0.15, MAT["coat"], f"Shoulder_{s}", seg=10, rings=8)

# ============================================ ARMS (30 deg below horizontal)
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    sh = (0.38 * sx, 0, 2.20)
    el = (0.70 * sx, 0, 2.015)
    wr = (1.00 * sx, 0, 1.845)
    limb(sh, el, 0.125, 0.11, MAT["coat"], f"SleeveUpper_{s}")
    limb(el, wr, 0.11, 0.095, MAT["coat"], f"SleeveFore_{s}")
    # flared sleeve cuff
    limb((0.955 * sx, 0, 1.885), (1.015 * sx, 0, 1.83), 0.095, 0.12,
         MAT["coat_dark"], f"SleeveCuff_{s}")
    # small dark mitt, angled down/out
    ball((1.045 * sx, 0.01, 1.76), 0.075, 0.085, 0.105, MAT["dark"],
         f"Glove_{s}", seg=10, rings=8)

# ------------------------------------------------------------------ LEGS
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    x = 0.13 * sx
    limb((x, 0, 1.50), (x, 0, 0.86), 0.092, 0.085, MAT["dark"], f"Leg_{s}")

# ------------------------------------------------------------------ BOOTS
for sx in (1, -1):
    s = "R" if sx > 0 else "L"
    x = 0.13 * sx
    # slim tapered shaft (reaches the foot - no gap)
    limb((x, 0, 0.86), (x, 0, 0.15), 0.105, 0.095, MAT["boot"], f"BootShaft_{s}")
    # wide white cuff as a separate wrap
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.135, radius2=0.165,
                                    depth=0.24, location=(x, 0, 0.80))
    cuff = bpy.context.active_object
    finish(cuff, f"BootCuff_{s}", MAT["cuff"])
    sharpen(cuff, 35)
    # compact foot
    box((x, 0.11, 0.115), (0.20, 0.44, 0.17), MAT["boot"], f"BootFoot_{s}",
        smooth=False)
    # flat sole
    box((x, 0.12, 0.032), (0.22, 0.48, 0.064), MAT["dark"], f"BootSole_{s}",
        smooth=False)
    # criss-cross laces on the front
    for j, lz in enumerate((0.52, 0.60, 0.68)):
        for k, ang in enumerate((0.55, -0.55)):
            box((x, 0.103, lz), (0.13, 0.016, 0.024), MAT["lace"],
                f"Lace_{s}_{j}_{k}", rot=(0, 0, ang), smooth=False)

# ================================================================ staging
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, 0))
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

# ------------------------------------------------------------------ cameras
bpy.ops.object.camera_add(location=(0, 9, 1.7))
cam = bpy.context.active_object
cam.name = "Camera"
bpy.context.scene.camera = cam
TARGET = (0, 0, 1.65)
ground_obj = bpy.data.objects.get("Ground")


def aim(cam_loc, target=TARGET):
    cam.location = cam_loc
    direction = mathutils.Vector(target) - mathutils.Vector(cam_loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


# orthographic front for reference comparison
cam.data.type = "ORTHO"
cam.data.ortho_scale = 4.1

# ------------------------------------------------------------------ render
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.film_transparent = False


def render_to(path, cam_loc, ortho=True, target=TARGET, hide_ground=False):
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = 4.1
    else:
        cam.data.type = "PERSP"
        cam.data.lens = 45
    if ground_obj:
        ground_obj.hide_render = hide_ground
    aim(cam_loc, target)
    bpy.context.view_layer.update()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered:", path)


if os.environ.get("SKIP_RENDER") != "1":
    render_to(RENDER_FRONT, (0, 9, 1.7), ortho=True, hide_ground=True)
    render_to(RENDER_ANGLE, (4.6, 5.6, 3.1), ortho=False)
    render_to(RENDER_SIDE, (9, 0, 1.7), ortho=True, hide_ground=True)
    render_to(RENDER_BACK, (0, -9, 1.7), ortho=True, hide_ground=True)

# ------------------------------------------------------------------- export
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

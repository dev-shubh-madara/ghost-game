"""Create reference-inspired *starter* meshes, not photoreal likenesses or rigs.
Run in Blender background mode:
  blender --background --python blender/build_reference_characters.py -- --output models
Creates separate new scenes; does not delete the user's existing scene.
"""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--output', default='models')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)

def material(name, rgb, roughness=.85, alpha=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*rgb, 1)
    node.inputs['Roughness'].default_value = roughness
    node.inputs['Alpha'].default_value = alpha
    mat.diffuse_color = (*rgb, alpha)
    if alpha < 1 and hasattr(mat, 'surface_render_method'):
        mat.surface_render_method = 'DITHERED'
    return mat

cloth = material('Olive cotton', (.10, .14, .085))
vest = material('Worn field vest', (.075, .09, .055))
boots = material('Black leather', (.016, .022, .021), .68)
skin = material('Skin', (.55, .39, .30))
hair = material('Dark hair', (.02, .027, .023))
pale = material('Spectral skin', (.55, .65, .63), .95, .72)
dress_mat = material('Weathered pale linen', (.58, .65, .62), 1, .65)
socket = material('Hollow eyes', (.012, .019, .018))

def sphere(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj

def box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Soft seams', 'BEVEL')
    bevel.width = .025
    bevel.segments = 2
    return obj

def limb(name, start, end, radius, mat):
    delta = Vector(end) - Vector(start)
    obj = sphere(name, (Vector(start)+Vector(end))/2, (radius, radius, delta.length/2+radius), mat)
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return obj

def new_scene(name):
    scene = bpy.data.scenes.new('Wraith_' + name)
    bpy.context.window.scene = scene
    scene.unit_settings.system = 'METRIC'
    return scene

def export(name):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(out / (name+'.glb')), export_format='GLB', use_selection=True, export_yup=True)

new_scene('Ghost')
sphere('Face', (0, 0, 1.96), (.16, .14, .23), pale)
sphere('Bodice', (0, .015, 1.38), (.25, .17, .41), dress_mat)
for x in [-.07, .07]:
    sphere('Hollow socket', (x, -.13, 1.99), (.037, .025, .028), socket)
sphere('Nose', (0, -.146, 1.945), (.024, .025, .047), pale)
sphere('Mouth', (0, -.138, 1.87), (.038, .015, .017), socket)
verts, faces = [], []
for ring in range(9):
    z = .08 + ring*.14
    radius = .62 - ring*.04
    for j in range(40):
        a = j*math.tau/40
        r = radius*(1+.07*math.cos(a*12))
        verts.append((r*math.cos(a), r*.8*math.sin(a), z + (.035*math.sin(a*7) if ring==0 else 0)))
for ring in range(8):
    for j in range(40):
        k = ring*40+j
        faces.append((k, ring*40+(j+1)%40, (ring+1)*40+(j+1)%40, k+40))
mesh = bpy.data.meshes.new('Pleated dress mesh')
mesh.from_pydata(verts, [], faces)
mesh.materials.append(dress_mat)
obj = bpy.data.objects.new('Long tattered dress', mesh)
bpy.context.collection.objects.link(obj)
for face in mesh.polygons:
    face.use_smooth = True
for sign in [-1,1]:
    limb('Sleeve', (sign*.26, 0, 1.62), (sign*.35, -.01, 1.08), .075, dress_mat)
    limb('Hand', (sign*.35, -.01, 1.08), (sign*.37, -.03, .94), .048, pale)
for j in range(24):
    a = math.tau*j/24
    x,y = math.cos(a)*.18, math.sin(a)*.145
    if y < -.08 and abs(x)<.10:
        continue
    limb('Long hair lock', (x,y,2.11), (x*1.4,y*1.5,1.28+(j%3)*.06), .028, hair)
export('ghost')

for name, female in [('ethan', False), ('maya', True)]:
    new_scene(name)
    width = .19 if female else .23
    sphere('Jacket', (0,0,1.28), (width,.14,.32), cloth)
    box('Vest', (0,-.045,1.32), (width*1.9,.24,.42), vest)
    box('Backpack', (0,.2,1.3), (.32,.22,.43), vest)
    for x in [-.11,.11]:
        box('Vest pouch', (x,-.19,1.25), (.12,.075,.15), cloth)
    sphere('Head', (0,0,1.77), (.135,.12,.19), skin)
    sphere('Hair cap', (0,.025,1.88), (.14,.125,.1), hair)
    if female:
        limb('Ponytail', (0,.12,1.88), (0,.19,1.50), .055, hair)
    for sign in [-1,1]:
        limb('Sleeve', (sign*(width+.035),0,1.47), (sign*.30,-.03,1.12), .074, cloth)
        limb('Forearm', (sign*.30,-.03,1.12), (sign*.31,-.14,.94), .051, skin)
        sphere('Hand', (sign*.31,-.14,.91), (.05,.044,.075), skin)
        limb('Trouser leg', (sign*.11,0,1.01), (sign*.13,0,.25), .095, cloth)
        box('Boot', (sign*.13,-.055,.11), (.17,.29,.22), boots)
    for x in [-.052,.052]:
        sphere('Eye', (x,-.116,1.8), (.018,.01,.013), socket)
    export(name)

# GLBs load only after all exports succeed; browser fallback remains usable otherwise.
(out/'manifest.json').write_text(json.dumps({'enabled':True,'ghost':'ghost.glb','male':'ethan.glb','female':'maya.glb'}, indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'wraith_character_starters.blend'))
print('Exported reference-inspired starter meshes to', out)

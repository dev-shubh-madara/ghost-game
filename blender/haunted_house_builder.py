import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, rough=.9, metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Roughness'].default_value=rough
    bsdf.inputs['Metallic'].default_value=metal
    return m

WALL=mat('Aged Plaster',(0.13,0.14,0.13),.96)
WOOD=mat('Rotten Wood',(0.20,0.12,0.07),.98)
FLOOR=mat('Old Floor',(0.10,0.09,0.07),1)
METAL=mat('Oxidized Metal',(0.12,0.14,0.14),.7,.3)

def cube(name, loc, scale, material, game_type=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if game_type: o['game_type']=game_type
    return o

cube('Ground_Floor',(0,0,-.2),(26,22,.4),FLOOR,'collision')
cube('Second_Floor',(0,0,3.0),(26,22,.25),FLOOR,'collision')
for y in (1.4,4.4):
    cube('Wall_L',(-12.8,0,y),(.35,22,3),WALL,'collision')
    cube('Wall_R',(12.8,0,y),(.35,22,3),WALL,'collision')
    cube('Wall_Back',(0,-10.8,y),(26,.35,3),WALL,'collision')
    cube('Wall_Front',(0,10.8,y),(26,.35,3),WALL,'collision')
for i in range(11):
    cube(f'Stair_{i:02d}',(0,2-i*.42,.12+i*.25),(3,.52,.22),WOOD,'collision')
for i in range(12):
    o=cube(f'Breakable_Board_{i:02d}',(-2.6+i*.48,5.8,3.14),(.42,3.0,.12),WOOD,'breakable')
    o['break_group']='upper_corridor'
    o['noise_alert']=1.0

bpy.ops.object.light_add(type='AREA',location=(0,0,6.5))
bpy.context.object.data.energy=350
bpy.context.object.data.color=(0.45,0.60,0.72)
bpy.context.object.data.shape='DISK'
bpy.context.object.data.size=9

bpy.ops.object.camera_add(location=(0,16,7),rotation=(math.radians(68),0,math.radians(180)))
bpy.context.scene.camera=bpy.context.object

scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1920
scene.render.resolution_y=1080
scene.world.color=(0.005,0.006,0.008)
print('Wraith House blockout created. Export as GLB for the web runtime.')

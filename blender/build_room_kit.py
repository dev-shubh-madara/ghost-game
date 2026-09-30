"""Build modular haunted interiors with Blender. 17m square, 3m high.
Coordinates: Blender Z up, doorway at Y=-8.5 (glTF +Z).
Exports a shared-material GLB containing six named room templates.
"""
import bpy, math, random, json, sys
import numpy as np
from pathlib import Path
from mathutils import Vector
random.seed(73)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'models';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'

# PBR texture maps generated in Blender: colour, normal, and roughness.
def texture_set(name, kind, base):
    n=256; rng=np.random.default_rng(17 if kind=='wood' else 23)
    yy,xx=np.mgrid[0:n,0:n]/n
    fine=rng.normal(0,.025,(n,n))
    if kind=='wood':
        h=.35+.10*np.sin(yy*100+3*np.sin(xx*10))+.06*np.sin(yy*420+6*np.sin(xx*16))+fine
        seam=((yy*8)%1<.025)|((xx*2+(np.floor(yy*8)%2)*.5)%1<.012)
        h[seam]=.05
    else:
        h=.6+.10*np.sin(xx*18+np.sin(yy*22))+.07*np.cos(yy*31)+fine
        cracks=np.abs(np.sin(xx*35+np.sin(yy*18)*1.7))<.021
        h[cracks]=.1
    mats={}
    for channel in ['color','normal','rough']:
        pixels=np.ones((n,n,4),dtype=np.float32)
        if channel=='color':
            rgb=np.array(base);pixels[:,:,:3]=np.clip(rgb[None,None,:]*(.7+h[:,:,None]*.55),0,1)
        elif channel=='rough':pixels[:,:,:3]=np.clip(.65+h[:,:,None]*.25,.4,1)
        else:
            gy,gx=np.gradient(h);normal=np.stack((-gx*2,-gy*2,np.ones_like(h)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);pixels[:,:,:3]=normal*.5+.5
        im=bpy.data.images.new(name+'_'+channel,width=n,height=n)
        if channel!='color':im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(pixels.ravel());im.pack();mats[channel]=im
    return mats

def material(name, color, rough=.8, metal=0, tex=None, emission=None):
    m=bpy.data.materials.new(name);m.use_nodes=True
    nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if tex:
        for channel,socket in [('color','Base Color'),('rough','Roughness')]:
            t=nodes.new('ShaderNodeTexImage');t.image=tex[channel];links.new(t.outputs['Color'],p.inputs[socket])
        t=nodes.new('ShaderNodeTexImage');t.image=tex['normal'];nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.45;links.new(t.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
    if emission:
        p.inputs['Emission Color'].default_value=(*emission,1);p.inputs['Emission Strength'].default_value=2
    return m
wood=material('Aged oak',(.19,.10,.047),tex=texture_set('oak','wood',(.22,.13,.065)))
wall=material('Stained plaster',(.28,.29,.23),tex=texture_set('plaster','wall',(.30,.32,.26)))
trim=material('Dark wainscot',(.055,.071,.060),.78)
fabric=material('Faded linen',(.33,.29,.23),.98)
red=material('Oxblood textile',(.16,.033,.025),.9)
metal=material('Aged brass',(.23,.17,.08),.42,.7)
black=material('Iron',(.033,.04,.036),.6,.5)
light=material('Warm bulb',(.8,.53,.2),emission=(1,.53,.16))
paper=material('Aged paper',(.46,.40,.28),.98)
all_objects=[]

def box(name,loc,size,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Worn edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
    all_objects.append(o);return o

def cyl(name,loc,r,depth,mat,vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat);all_objects.append(o);return o

def sphere(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    all_objects.append(o);return o

def chair(x,y):
    box('Upholstered seat',(x,y,.46),(.55,.56,.13),red,.035)
    box('Carved chair back',(x,y+.23,.91),(.54,.09,.90),wood,.025)
    for dx in [-.21,.21]:
        for dy in [-.21,.21]:box('Chair leg',(x+dx,y+dy,.23),(.055,.055,.46),wood,.008)

def desk(x,y,w=2.4):
    box('Desk surface',(x,y,.79),(w,1.0,.14),wood,.035)
    for dx in [-w/2+.18,w/2-.18]:
        for dy in [-.34,.34]:box('Desk leg',(x+dx,y+dy,.38),(.12,.12,.76),wood,.015)
    box('Desk drawer',(x,y-.02,.6),(w-.3,.75,.22),wood,.02)
    for dx in [-.4,.4]:box('Drawer pull',(x+dx,y-.43,.6),(.15,.055,.035),metal,.01)
    box('Open journal',(x-.2,y,.89),(.36,.28,.04),paper,.005)
    cyl('Lamp base',(x+.65,y+.1,.9),.16,.07,metal);cyl('Lamp stem',(x+.65,y+.1,1.12),.025,.4,metal)
    bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.25,radius2=.12,depth=.22,location=(x+.65,y+.1,1.4));o=bpy.context.object;o.data.materials.append(trim);all_objects.append(o)
    sphere('Lamp bulb',(x+.65,y+.1,1.29),(.06,.06,.06),light)

def shelf(x,y,w=2):
    box('Bookcase back',(x,y,1.15),(w,.18,2.3),wood,.025)
    for dx in [-w/2,w/2]:box('Bookcase side',(x+dx,y-.15,1.15),(.09,.47,2.3),wood,.02)
    for z in [.12,.64,1.16,1.68,2.22]:
        box('Bookcase shelf',(x,y-.14,z),(w,.48,.08),wood,.012)
        if z<2:
            for j in range(10):
                h=.30+random.random()*.13;book=box('Book',(x-w/2+.15+j*(w-.25)/10,y-.18,z+h/2+.05),(.11,.25,h),[red,paper,trim][j%3],.003);book.rotation_euler.y=random.uniform(-.09,.09)

def bed(x,y,hospital=False):
    frame=black if hospital else wood
    box('Bed frame',(x,y,.38),(2.1,2.7,.22),frame,.05)
    box('Mattress',(x,y,.57),(2,2.6,.25),fabric,.08)
    box('Folded blanket',(x,y-.45,.73),(1.98,1.5,.09),red if not hospital else trim,.04)
    for dx in [-.48,.48]:sphere('Pillow',(x+dx,y+.8,.76),(.46,.35,.10),fabric)
    box('Headboard',(x,y+1.38,.86),(2.15,.15,1.2),frame,.03)
    for dx in [-.94,.94]:
        for dy in [-1.25,1.25]:box('Bed foot',(x+dx,y+dy,.2),(.09,.09,.40),frame,.01)

names=['Bedroom','Library','Infirmary','Dining','Nursery','Ritual']
for index,name in enumerate(names):
    all_objects=[]
    # Open 1.9m entrance, full walls, moulding and a paneled ceiling.
    for x in [-8.5,8.5]:box('Side wall',(x,0,1.5),(.22,17,3),wall)
    box('Rear wall',(0,8.5,1.5),(17,.22,3),wall)
    for x in [-4.74,4.74]:box('Front wall',(x,-8.5,1.5),(7.58,.22,3),wall)
    box('Door lintel',(0,-8.5,2.72),(1.9,.22,.56),wall)
    for x in [-1.02,1.02]:box('Door jamb',(x,-8.4,1.2),(.12,.2,2.4),wood,.015)
    box('Door frame top',(0,-8.4,2.41),(2.18,.2,.14),wood,.018)
    # Continuous wainscoting and battens, left and right.
    for x in [-8.34,8.34]:
        box('Wainscot',(x,0,.56),(.08,16.8,1.1),trim)
        for z in [.12,1.12,2.82]:box('Wall moulding',(x,0,z),(.13,16.8,.10),wood,.008)
        for y in range(-8,9,2):box('Panel stile',(x,y,.57),(.14,.07,1.1),wood,.008)
    box('Rear panel',(0,8.34,.56),(16.7,.08,1.1),trim)
    for z in [.12,1.12,2.82]:box('Rear moulding',(0,8.32,z),(16.7,.13,.10),wood,.008)
    box('Ceiling',(0,0,2.98),(17,17,.06),trim)
    for y in [-6,-2,2,6]:box('Ceiling beam',(0,y,2.86),(16.9,.16,.18),wood,.015)
    for x in [-6,-2,2,6]:box('Ceiling crossbeam',(x,0,2.86),(.16,16.9,.18),wood,.015)
    for row in range(34):
        for col in range(4):box('Floor plank',(-6.375+col*4.25,-8.25+row*.5,.018),(4.23,.488,.035),wood)
    box('Carpet',(0,0,.055),(6,8,.035),red,.02)
    for x in [-5,5]:
        box('Wall portrait frame',(x,8.18,1.91),(1.35,.13,1.35),wood,.02)
        box('Faded portrait',(x,8.10,1.91),(1.15,.02,1.15),trim)
        sphere('Portrait silhouette',(x,8.07,1.99),(.19,.013,.28),paper)
    # Wall sconces and exposed conduit.
    for x in [-8.18,8.18]:
        for y in [-5,5]:
            box('Sconce plate',(x,y,2.08),(.06,.16,.35),metal,.01)
            sphere('Sconce globe',(x*.985,y,2.16),(.09,.09,.17),light)
    if name=='Bedroom':
        bed(-4,3);desk(4,5);chair(4,3.9);shelf(5,8,2.5)
        box('Trunk',(-5,-4,.42),(2,.85,.84),wood,.06)
    elif name=='Library':
        for x in [-5,-2,2,5]:shelf(x,8,2.1)
        desk(-4,2);desk(4,2);chair(-4,.8);chair(4,.8)
        for x in [-5,5]:shelf(x,-4,2.4)
    elif name=='Infirmary':
        for x in [-5,5]:
            for y in [-3,3]:bed(x,y,True)
        desk(0,6);cyl('IV stand',(-3,3,1.1),.025,2.2,metal)
        sphere('IV bottle',(-3,3,1.96),(.09,.09,.18),fabric)
    elif name=='Dining':
        desk(0,1,5.2)
        for x in [-2,-.7,.7,2]:chair(x,-.25);chair(x,2.2)
        shelf(-5,7,3);shelf(5,7,3)
        for x in [-1.8,-.6,.6,1.8]:cyl('Plate',(x,1,.88),.21,.025,paper,24)
    elif name=='Nursery':
        for x in [-4,4]:
            box('Cot mattress',(x,3,.6),(1.4,2.1,.15),fabric,.07)
            for dx in [-.78,.78]:
                for dy in np.arange(-1,1.1,.2):cyl('Cot rail',(x+dx,3+dy,.8),.025,1.3,wood)
                box('Cot top rail',(x+dx,3,1.45),(.09,2.2,.09),wood,.02)
        sphere('Toy ball',(-4,-2,.22),(.22,.22,.22),red);desk(4,-3)
        sphere('Toy bear body',(4,-3,1.12),(.15,.12,.22),paper);sphere('Toy bear head',(4,-3,1.41),(.14,.12,.13),paper)
    else:
        cyl('Ritual dais',(0,3,.11),2.1,.15,black,48)
        box('Ritual altar',(0,3,.55),(1.8,1.2,.9),wood,.04)
        for j in range(12):
            a=j*math.tau/12;x,y=math.cos(a)*2.7,3+math.sin(a)*2.7
            cyl('Candle',(x,y,.27),.065,.48,paper);sphere('Flame',(x,y,.53),(.035,.035,.075),light)
        shelf(-5,7);shelf(5,7)
    # Deterministic small debris around edges; central travel/mission point stays clear.
    for j in range(24):
        x=random.choice([-1,1])*random.uniform(6.5,7.9);y=random.uniform(-7.5,7.5)
        shard=box('Plaster debris',(x,y,.06),(random.uniform(.08,.3),random.uniform(.06,.2),.05),paper);shard.rotation_euler.z=random.random()*math.pi
    # Join all meshes into one multi-material mesh: exporter makes a primitive per material.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in all_objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=all_objects[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=name
    bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');obj['room_type']=name
    # All prototypes overlap intentionally; the client instantiates them separately.

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT/'haunted-rooms.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'haunted-rooms.blend'),compress=True)
manifest={'blender':bpy.app.version_string,'room_names':names,'room_size_m':[17,3,17],'rooms_per_floor':2500,'floors':2,'source':'blender/build_room_kit.py'}
(OUT/'room-kit.json').write_text(json.dumps(manifest,indent=2))
print('ROOM_KIT_COMPLETE',json.dumps(manifest))

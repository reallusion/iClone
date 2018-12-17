import bpy
from mathutils import *
from math import *
from random import *

def createAnimation( ori, tar, base_distance, push_distance, spin_rate, push_rate, bake_frame ):
    s = bpy.context.scene
    
    bpy.ops.object.empty_add(type='ARROWS')
    bpy.ops.object.location_clear()
    obj_root = bpy.context.object
    temp_cube = ori.copy()
    temp_cube.matrix_local = Matrix()
    temp_cube.parent = obj_root
    s.objects.link( temp_cube )
    temp_cube.select = True
    s.objects.active = temp_cube
    bpy.ops.object.modifier_add(type='MASK')
    #temp_cube.modifiers['Mask'].show_viewport = False
    #temp_cube.draw_type = 'WIRE'
    
    def caculatePos(p, f):
        sinValue = sin( f / push_rate ) * push_distance
        
        m = temp_cube.matrix_local
        lc = p.center + p.normal * ( sinValue + base_distance )
        
        gc = m * lc
        ln = p.normal
        gn = m.to_3x3() * ln
        
        vec1 = Vector((0,0,1))
        vec2 = gn
        vec3 = vec1.cross( vec2 ).normalized()
        
        angle = vec1.angle( vec2 )
        
        tm = Matrix.Translation( gc )
        rm = Matrix.Rotation( angle, 4, vec3 )
         
        return tm * rm
        
    seed = randint(1,10000)
    for f in range( bake_frame ):
        s.frame_set(f)
        temp_cube.rotation_euler[0] = ( f + seed ) / spin_rate
        temp_cube.rotation_euler[1] = ( f + seed ) / spin_rate
        temp_cube.keyframe_insert('rotation_euler')
        s.objects.update()
        
    for p in temp_cube.data.polygons:
        geo = tar.copy()
        geo.parent = obj_root
        s.objects.link( geo )
        
        for f in range( bake_frame ):
            s.frame_set(f)
            
            geo.matrix_local = caculatePos(p, f + seed).copy()
            geo.keyframe_insert('location')
            geo.keyframe_insert('rotation_euler')
            
        s.frame_set( 1 )
    for o in s.objects:
        o.select = False
    temp_cube.select = True
    bpy.ops.object.delete()
    
    obj_root.select = True
    
class vic_object_around_object_pick_base(bpy.types.Operator):
    bl_idname = 'vic.vic_object_around_object_pick_base'
    bl_label = 'Pick Base'
    def execute(self, context):
        if context.scene.objects.active == None:
            return {'CANCELLED'}
        try:
            context.object.data.polygons
            if len( context.object.data.polygons ) > 50:
                self.report({'ERROE'}, '' );
                return {'CANCELLED'}
            context.scene.txt_base = context.scene.objects.active.name
            return {'FINISHED'}
        except:
            self.report( {'ERROR'}, 'base object is not geometry! or polygon is too much!' )
            context.scene.txt_base = ''
            return {'CANCELLED'}
        
class vic_object_around_object_pick_instancer(bpy.types.Operator):
    bl_idname = 'vic.vic_object_around_object_pick_instancer'
    bl_label = 'Pick Instancer'
    def execute(self, context):
        if context.scene.objects.active == None:
            return {'CANCELLED'}
        context.scene.txt_instancer = context.scene.objects.active.name
        return {'FINISHED'}    

class vic_object_around_object_create_animation(bpy.types.Operator):
    bl_idname = 'vic.vic_object_around_object_create_animation'
    bl_label = 'Create Animation'
    def execute(self, context):
        try:
            obj_base = context.scene.objects[ context.scene.txt_base ]
            obj_instancer = context.scene.objects[ context.scene.txt_instancer ]
            createAnimation( obj_base, obj_instancer, 
                base_distance = context.scene.num_baseDistance,
                push_distance = context.scene.num_pushDistance,
                spin_rate = context.scene.num_spinRate,
                push_rate = context.scene.num_pushRate,
                bake_frame = context.scene.num_bakeFrame
            )
            return {'FINISHED'}
        except:
            context.scene.txt_base = ''
            context.scene.txt_instancer = ''
            self.report( {'ERROR'}, 'should pick base and instancer first!' )
            return {'CANCELLED'}  
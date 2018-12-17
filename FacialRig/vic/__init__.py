bl_info = {
    "name": "Vic Tools",
    "author": "Vic",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "View3D > Tool Shelf > Vic",
    "description": "Some useful function created by VicYu",
    "warning": "",
    "wiki_url": "",
    "category": "Tools"
}

if "bpy" in locals():
    import imp
    imp.reload(vic_particle_rigidbody)
    #imp.reload(vic_json_importer_execute)
    #imp.reload(vic_make_meshs_plane)
    #imp.reload(vic_create_camera_target)
    imp.reload(vic_object_around_object_create_animation)
    imp.reload(vic_bge_pure_particle)
    imp.reload(vic_bge_hand_drag)
    imp.reload(vic_bge_quick_motion)
    imp.reload(vic_object_hand_drag)
    imp.reload(vic_make_it_voxel)
    imp.reload(vic_actions)

else:
    from . import vic_particle_rigidbody
   #from . import vic_json_importer_execute
   #from . import vic_make_meshs_plane
    #from . import vic_create_camera_target
    from . import vic_object_around_object_create_animation
    from . import vic_bge_pure_particle
    from . import vic_bge_hand_drag
    from . import vic_bge_quick_motion
    from . import vic_object_hand_drag
    from . import vic_make_it_voxel
    from . import vic_actions

import bpy, bmesh

class VIC_ACTION_PANEL(bpy.types.Panel):
    bl_category = "Vic Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Actions"

    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.operator("vic.mirror_cube_add")
        col.operator("vic.vic_create_camera_target")
        #col.operator("vic.make_meshs_plane")
        col.operator("vic.particle_rigidbody")
        row = col.row(align=True)
        row.prop(context.scene, 'string_select_name' )
        row.operator("vic.select_by_name")
        
        col.label('Drag Effect')
        col.operator("vic.hand_drag")
        col.operator("vic.healing_all_effect_objects")
        col.label("BGE")
        col.operator("vic.pure_particle")
        #col.operator("vic.pure_particle_sprite")
        col.operator("vic.pure_particle_sprite_rotable")
        col.operator("vic.bge_hand_drag")
        col.operator("vic.bge_quick_motion")
#=======================================

import bpy, math
from mathutils import Vector
from mathutils import Matrix
from mathutils import Quaternion

def clearAllBonesKey( bones, start_frame, end_frame):
    for f in range( start_frame, end_frame ):
        for b in bones:
            try:
                b.keyframe_delete(data_path="rotation_quaternion" ,frame=f)
            except RuntimeError:
                print( "no action!" )
            b.rotation_quaternion = Quaternion( Vector(), 1 )
            
def getLocalQuaternion( m, axis, angle ):
    b_rot_mat = getRotationMatrixFromMatrix( m )
    localAxis = b_rot_mat.inverted() * axis
    return Quaternion (localAxis, angle)            
    
def getRotationMatrixFromMatrix( m ):
    return m.to_quaternion().to_matrix().to_4x4().copy()    

def getTailMatrix( body, bone, pos ):
    qua_mat = body.matrix_world * bone.matrix
    qua_mat = qua_mat.to_quaternion().to_matrix().to_4x4()
    pos_mat = Matrix.Translation( body.matrix_world * pos )
    return pos_mat * qua_mat

def collectBonesFromRoot( root_bone ):
    bones = []
    temp_bone = root_bone
    while( len( temp_bone.children ) != 0 ):
        bones.append( temp_bone.children[0] )
        temp_bone = temp_bone.children[0]
    return bones   

def getBoneRelativeData( root, pts):
    pos_data = []
    dist_data = []
    
    for i, p in enumerate( pts, 0 ):
        first_point = None
        if i == 0:
            first_point = root
        else:
            first_point = pts[i-1]
        pos_data.append( first_point.inverted().copy() * p.to_translation().copy() )
        dist_data.append( (first_point.to_translation().copy() - p.to_translation().copy()).magnitude )
    return pos_data, dist_data     

def saveRootPosition( root, root_locs ):
    root_locs.append( root.to_translation().copy() )
    if len( root_locs ) > 100:
        root_locs.pop(0)
        
def getDiffPosition(root_locs, prev_count):
    last = len(root_locs)-1
    target = last - prev_count
    if target < 0:
        return Vector()
    if len( root_locs ) < target + 1:
        return Vector()
    pa = root_locs[target]
    pb = root_locs[target-1]
    return pa-pb

def setTranslationForMatrix( mat, pos ):
    return Matrix.Translation( pos ) * mat.to_quaternion().to_matrix().to_4x4()

def setRotationForMatrix( mat, qua ):
    return Matrix.Translation( mat.to_translation() ) * qua.to_matrix().to_4x4()
    
def addForce(pts, pts_spd, root, root_locs, pos_data, gravity):
    for i, p in enumerate( pts, 0 ):
        first_point = None
        if i == 0:
            first_point = root
        else:
            first_point = pts[i-1]
        
        back_pos = first_point * pos_data[i].copy()
        back_force = back_pos - p.to_translation().copy()
        
        if bpy.context.scene.spring_bone_keep_is_spring:
            spd = pts_spd[i]
        
            diff = getDiffPosition( root_locs, i * 3 )
            
            spd += diff * bpy.context.scene.spring_bone_extend_factor
            spd += back_force * bpy.context.scene.spring_bone_spring_factor
            spd += gravity * bpy.context.scene.spring_bone_gravity_factor
            spd *= bpy.context.scene.spring_bone_friction_factor
            pts[i] = setTranslationForMatrix( p, p.to_translation() + spd )
        else:
            pts[i] = setTranslationForMatrix( p, p.to_translation() + back_force * bpy.context.scene.spring_bone_spring_factor )
        
def setRotation(root, pts, up_vec):
    for i, p in enumerate( pts, 0 ):
        first_point = None
        if i == 0:
            first_point = root
        else:
            first_point = pts[i-1]
        
        z_vec = ( first_point.to_translation() - p.to_translation() ).normalized()
        rot_quat = z_vec.to_track_quat('-Y', 'Z')
        pts[i] = setRotationForMatrix( p, rot_quat )
        
        # another method I offen used
        '''
        z_vec = ( first_point.to_translation() - p.to_translation() ).normalized()
        spin_vec = z_vec.cross( up_vec ).normalized()
        spin_angle = z_vec.angle( up_vec )
        pts[i] = setRotationForMatrix( p, Quaternion( spin_vec, spin_angle ).inverted() )
        '''
        
def limitDistance(root, pts, pts_len):
    for i, p in enumerate( pts, 0 ):
        first_point = None
        if i == 0:
            first_point = root
        else:
            first_point = pts[i-1]
        len = pts_len[i] 
        pts[i] = setTranslationForMatrix( p, ( p.to_translation() - first_point.to_translation() ).normalized() * len + first_point.to_translation() )     
        
def syncToDebugView( f, start_frame, body, debug_views, pts ):
    for i, v in enumerate( debug_views, 0 ):
        v.matrix_world = pts[i]
        if f >= start_frame:
            v.keyframe_insert(data_path="rotation_quaternion" ,frame=f)     
            v.keyframe_insert(data_path="location" ,frame=f)     
    
def mapToBone( f, start_frame, body, root, root_bone, bones, pts ):
    for i, b in enumerate( bones, 0 ):
        b.matrix = body.matrix_world.inverted() * pts[i]
        
        # this update is very important, blender will update matrix with this function call, if not call will occur strange performance
        bpy.context.scene.update()
        if f >= start_frame:
            b.keyframe_insert(data_path="rotation_quaternion" ,frame=f)        
    
    # another method, using quaternion
    '''
    global_proxy_qua = pts[i].to_quaternion()
    global_bone_gua = ( body.matrix_world * b.matrix ).to_quaternion()
    global_diff_qua = global_bone_gua.inverted() * global_proxy_qua
    
    b.rotation_quaternion *= global_diff_qua
    
    if f >= start_frame:
        b.keyframe_insert(data_path="rotation_quaternion" ,frame=f)   
    '''

class vic_spring_bone(bpy.types.Operator):
    bl_idname = 'vic.spring_bone'
    bl_label = 'Bake Spring Bone'
    
    def process(self,context):
        
        objs = bpy.data.objects
        body = bpy.context.object
        
        up_vec = Vector([0, -1, 0])        
        gravity = Vector([0,0,-1])   
        
        start_frame = context.scene.spring_bone_frame_start
        end_frame = context.scene.spring_bone_frame_end
        
        selected_pose_bones = context.selected_pose_bones

        for root_bone in selected_pose_bones:
            root = getTailMatrix( body, root_bone, root_bone.tail )
            bones = collectBonesFromRoot( root_bone ) 

            pts = [ getTailMatrix( body, b, b.tail ) for b in bones ]
            pts_spd = [Vector() for p in pts]
            
            # for prev force
            root_locs = []
            
            # set new mat for relative data
            setRotation( root, pts, up_vec )  
            
            # save relative data for children
            pos_data, dist_data = getBoneRelativeData( root, pts )
            
            # debug view
            # maybe will add new method for create fake bone
            '''
            debug_views = []
            for b in bones:
                bpy.ops.mesh.primitive_cone_add()
                bpy.context.object.rotation_mode = 'QUATERNION'
                debug_views.append( bpy.context.object )
            '''
            
            # -20 for get more real simulation
            for i in range( start_frame, end_frame ): 
                bpy.context.scene.frame_set( i )
                
                root = getTailMatrix( body, root_bone, root_bone.tail )
                saveRootPosition( root, root_locs )
                setRotation( root, pts, up_vec )  
                addForce( pts, pts_spd, root, root_locs, pos_data, gravity )
                limitDistance( root, pts, dist_data )   
                mapToBone( i, start_frame, body, root, root_bone, bones, pts )
                
                # maybe will add new method for create fake bone
                #syncToDebugView( i, start_frame, body, debug_views, pts )
                
                print( 'On Bone: ' + root_bone.name + ', Frame Complete: ' + str( i ) )
            bpy.context.scene.frame_set( 1 )             
        
    def execute(self, context):
        if context.object == None:
            return {'FINISHED'}
        else:
            if not hasattr( context.object, 'pose' ):
                return {'FINISHED'}
        if context.active_pose_bone == None:
            return {'FINISHED'}
        self.process( context )
        return {'FINISHED'}
        
class vic_bones_clear_key(bpy.types.Operator):
    bl_idname = 'vic.bones_clear_key'
    bl_label = 'Clear All Bones Key'      

    def process( self, context ):
        selected_pose_bones = context.selected_pose_bones

        for root_bone in selected_pose_bones:
            bones = collectBonesFromRoot( root_bone ) 
            
            start_frame = context.scene.spring_bone_frame_start
            end_frame = context.scene.spring_bone_frame_end
            
            clearAllBonesKey( bones, start_frame, end_frame )

    def execute(self, context):
            if context.object == None:
                return {'FINISHED'}
            else:
                if not hasattr( context.object, 'pose' ):
                    return {'FINISHED'}
            if context.active_pose_bone == None:
                return {'FINISHED'}                    
            self.process( context )
            return {'FINISHED'}
        
class VIC_SPRING_BONE_TOOL(bpy.types.Panel):
    bl_category = "Vic Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Spring Bone Tool"

    def draw(self, context):
        layout = self.layout     
        
        col = layout.column(align=True)
        col.operator("vic.spring_bone")        
        col.operator("vic.bones_clear_key")        
        col.prop(context.scene, 'spring_bone_frame_start' ) 
        col.prop(context.scene, 'spring_bone_frame_end' ) 
        col = layout.column(align=True)
        col.prop(context.scene, 'spring_bone_extend_factor', 'Extend' ) 
        col.prop(context.scene, 'spring_bone_spring_factor', 'Keep' ) 
        col.prop(context.scene, 'spring_bone_gravity_factor', 'Gravity' ) 
        col.prop(context.scene, 'spring_bone_friction_factor', 'Friction' ) 
        col.prop(context.scene, 'spring_bone_keep_is_spring', 'Spring' ) 
       # col = layout.column(align=True)
       # col.prop(context.scene, 'spring_bone_roop_gravity', 'Roop Gravity' ) 
        
#=======================================


        
# developing...        
'''        
class VIC_JSON_IMPORTER_PANEL(bpy.types.Panel):
    bl_category = "Vic Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Json Importer"

    def draw(self, context):
        layout = self.layout     
        
        col = layout.column(align=True)
        col.prop(context.scene, 'conf_path')
        col.operator("vic.vic_json_importer_execute", text="Execute")
        col.separator()
'''        
        
class VIC_VOXEL_PANEL(bpy.types.Panel):
    bl_category = "Vic Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Voxel Tool"

    def draw(self, context):
        layout = self.layout     
        
        col = layout.column(align=True)
        col.operator("vic.make_it_voxel")
        
        #col.prop(context.scene, 'int_voxel_pool' )
        col.prop(context.scene, 'float_voxel_size' ) 
        col.prop(context.scene, 'float_voxel_sensor_distance' ) 
        #col.prop(context.scene, 'float_voxel_border_distance' ) 
        col.prop(context.scene, 'string_voxel_color_map' ) 
        col.prop(context.scene, 'bool_sensor_as_size' ) 
        col.prop(context.scene, 'bool_voxel_attach' ) 
        col.prop(context.scene, 'bool_voxel_animation' )
        col.prop(context.scene, 'int_frame_start' )
        col.prop(context.scene, 'int_frame_end' )
        
        #col.prop(context.scene, 'bool_voxel_simple_way' )  

class VIC_AROUND_PANEL(bpy.types.Panel):
    bl_category = "Vic Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Object Around Object"

    def draw(self, context):
        layout = self.layout     
        
        col = layout.column(align=True)
        col.prop(context.scene, 'num_baseDistance', 'Distance' )
        col.prop(context.scene, 'num_pushDistance', 'Push Dist' )
        col.prop(context.scene, 'num_spinRate', 'Spin Rate' )
        col.prop(context.scene, 'num_pushRate', 'Push Rate' )
        col.prop(context.scene, 'num_bakeFrame', 'Frames' )
        
        row = col.row(align=True)
        row.operator('vic.vic_object_around_object_pick_base')
        row.prop(context.scene, 'txt_base', '' )
        
        row = col.row(align=True)
        row.operator('vic.vic_object_around_object_pick_instancer')
        row.prop(context.scene, 'txt_instancer', '' )
        col.operator( 'vic.vic_object_around_object_create_animation', icon='COLOR_RED' )  

'''
def menu_func(self, context):
    self.layout.separator()
    self.layout.operator("vic.mirror_cube_add")
    self.layout.operator("vic.vic_create_camera_target")
'''    
    
def register():
    # quick actions
    bpy.types.Scene.string_select_name = bpy.props.StringProperty(
            name="", description="Name of select objects", default="")     

    # json importer
    '''
    bpy.types.Scene.conf_path = bpy.props.StringProperty(
      name = "Path",
      default = "",
      description = "Define the root  path of the project",
      subtype = 'FILE_PATH'
    )
    '''
    # make it voxel
    bpy.types.Scene.int_frame_start = bpy.props.IntProperty(
            name="Start Frame", description="Start frame of animation", 
            default=1, step=1, min=1, max=100000)
            
    bpy.types.Scene.int_frame_end = bpy.props.IntProperty(
            name="End Frame", description="End frame of animation", 
            default=2, step=1, min=2, max=100000)            
            
    bpy.types.Scene.bool_voxel_animation = bpy.props.BoolProperty(
            name="Animation", description="",
            default=False)            
    
    '''
    bpy.types.Scene.int_voxel_pool = bpy.props.IntProperty(
            name="Count", description="Count of Voxel", 
            default=10, step=1, min=10, max=100000)
    
    bpy.types.Scene.bool_voxel_simple_way = bpy.props.BoolProperty(
            name="Simple Way", description="Simple way for sensor",
            default=True)
    '''        
    bpy.types.Scene.bool_voxel_attach = bpy.props.BoolProperty(
            name="Single Voxel", description="Attach all voxels together",
            default=True)
            
    bpy.types.Scene.bool_sensor_as_size = bpy.props.BoolProperty(
            name="Sensor As Size", description="As same as size",
            default=True)
            
    bpy.types.Scene.float_voxel_size = bpy.props.FloatProperty(
            name="Size", description="Size for voxel.", 
            default=1.0, step=1.0, min=0.1, max=100.0)
            
    bpy.types.Scene.float_voxel_sensor_distance = bpy.props.FloatProperty(
            name="Sensor", description="Sensor distance for ray.", 
            default=1.0, step=1.0, min=0.01, max=100.0)
    '''        
    bpy.types.Scene.float_voxel_border_distance = bpy.props.FloatProperty(
            name="Border Size Scale", description="Border size scale value, less value more speed", 
            default=2.0, step=1.0, min=1.0, max=4.0)
    '''        
    bpy.types.Scene.string_voxel_color_map = bpy.props.StringProperty(
            name="Color Map", description="Color map for voxel", default="Col")
            
    # object around object
    bpy.types.Scene.txt_base = bpy.props.StringProperty()
    bpy.types.Scene.txt_instancer = bpy.props.StringProperty()
    bpy.types.Scene.num_baseDistance = bpy.props.FloatProperty(
        default=3.0,
        min=0.0
    )
    bpy.types.Scene.num_pushDistance = bpy.props.FloatProperty(
        default=3.0,
        min=0.0
    )
    
    bpy.types.Scene.num_spinRate = bpy.props.IntProperty(
        default=10,
        min=1
    )
    bpy.types.Scene.num_pushRate = bpy.props.IntProperty(
        default=10,
        min=1
    )
    bpy.types.Scene.num_bakeFrame = bpy.props.IntProperty(
        default=100,
        min=1
    )
    
    bpy.types.Scene.spring_bone_extend_factor = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.spring_bone_spring_factor = bpy.props.FloatProperty(
        default=.6,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.spring_bone_gravity_factor = bpy.props.FloatProperty(
        default=0.0,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.spring_bone_friction_factor = bpy.props.FloatProperty(
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.spring_bone_keep_is_spring = bpy.props.BoolProperty(
        default=True)
    
    bpy.types.Scene.spring_bone_frame_start = bpy.props.IntProperty(
        name="Start Frame", description="Start frame of animation", 
        default=1, step=1, min=1, max=100000)
            
    bpy.types.Scene.spring_bone_frame_end = bpy.props.IntProperty(
        name="End Frame", description="End frame of animation", 
        default=2, step=1, min=2, max=100000)       
    '''        
    bpy.types.Scene.spring_bone_roop_gravity = bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, -1.0)
    )
    '''
    bpy.utils.register_module(__name__)
    #bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    # quick actions
    del bpy.types.Scene.string_select_name
    
    # json importer
    #del bpy.types.Scene.conf_path
    
    # make it voxel
    del bpy.types.Scene.bool_voxel_animation
    del bpy.types.Scene.int_frame_start
    del bpy.types.Scene.int_frame_end
    #del bpy.types.Scene.int_voxel_pool
    del bpy.types.Scene.bool_voxel_attach
   # del bpy.types.Scene.bool_voxel_simple_way
    del bpy.types.Scene.bool_sensor_as_size
    del bpy.types.Scene.float_voxel_size
    del bpy.types.Scene.float_voxel_sensor_distance
    #del bpy.types.Scene.float_voxel_border_distance
    del bpy.types.Scene.string_voxel_color_map
    
    del bpy.types.Scene.txt_base
    del bpy.types.Scene.txt_instancer
    del bpy.types.Scene.num_baseDistance
    del bpy.types.Scene.num_pushDistance
    del bpy.types.Scene.num_spinRate
    del bpy.types.Scene.num_pushRate
    del bpy.types.Scene.num_bakeFrame
    
    del bpy.types.Scene.spring_bone_keep_is_spring
    del bpy.types.Scene.spring_bone_frame_end
    del bpy.types.Scene.spring_bone_frame_start
    #del bpy.types.Scene.spring_bone_roop_gravity
    del bpy.types.Scene.spring_bone_extend_factor
    del bpy.types.Scene.spring_bone_spring_factor
    del bpy.types.Scene.spring_bone_gravity_factor
    del bpy.types.Scene.spring_bone_friction_factor
    
    bpy.utils.unregister_module(__name__)
    #bpy.types.INFO_MT_mesh_add.remove(menu_func) 

#if __name__ == "__main__":
#    register()

      
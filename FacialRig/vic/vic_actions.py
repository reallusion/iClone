import bpy, bmesh

def createCameraTarget( currobj, targetName ):
    bpy.ops.object.empty_add(type='ARROWS')
    currArrow = bpy.context.object
    currArrow.name = 'vic_camera_target'
    bpy.ops.object.location_clear()
    currArrow.select = False
    currobj.select = True
    bpy.context.scene.objects.active = currobj
    bpy.ops.object.constraint_add(type='TRACK_TO')
    currConstraint = currobj.constraints[len(currobj.constraints)-1]
    currConstraint.name = targetName
    currConstraint.target = currArrow
    currConstraint.track_axis = 'TRACK_NEGATIVE_Z'
    currConstraint.up_axis = 'UP_Y'

class vic_create_camera_target(bpy.types.Operator):
    bl_idname = 'vic.vic_create_camera_target'
    bl_label = 'Create Camera Target'
    
    target_name = "vic_camera_constraint_name"
    
    def execute(self, context):
        currobj = context.object
        cons = currobj.constraints
        for con in cons:
            if con.name == self.target_name:
                self.report( {'ERROR'}, 'already done!' )
                return {'CANCELLED'}
        createCameraTarget( currobj, self.target_name )
        return {'FINISHED'}
        
#==================================================        
        
class vic_select_by_name(bpy.types.Operator):
    bl_idname = 'vic.select_by_name'
    bl_label = 'Select By Name'
    
    def execute(self, context):
        delete_name = context.scene.string_select_name
        for b in bpy.data.objects:
            find_str = b.name.find( delete_name )
            b.select = False
            if find_str != -1:
                b.hide = False
                b.select = True
        return {'FINISHED'}       
        
#==================================================        

def createMirrorCube():
    bpy.ops.mesh.primitive_cube_add()
    bpy.ops.object.editmode_toggle()

    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
    for e in mesh.edges:
        e.select = ( e.index == 2 )
        
    bpy.ops.mesh.loop_multi_select(ring=True)
    bpy.ops.mesh.subdivide()

    for v in mesh.verts:
        v.select = v.co[1] < 0
        
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.editmode_toggle()

    bpy.ops.object.modifier_add(type='MIRROR')
    bpy.context.object.modifiers['Mirror'].use_x = False
    bpy.context.object.modifiers['Mirror'].use_y = True

    bpy.ops.object.modifier_add(type='SUBSURF')
        
class mirror_cube_add(bpy.types.Operator):
    bl_idname = 'vic.mirror_cube_add'
    bl_label = 'Create Mirror Cube'
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if bpy.context.object != None and bpy.context.object.mode == 'EDIT':
            self.report( {'ERROR'}, 'can not using this function in the EDIT mode!' )
            return {'CANCELLED'}
        else:
            createMirrorCube()
        return {'FINISHED'}        

import bpy
from mathutils import Vector
from mathutils import geometry

class vic_make_meshs_plane(bpy.types.Operator):
    bl_idname = 'vic.make_meshs_plane'
    bl_label = 'Make Meshs Plane'
    
    def doPlane(self, context):
        mode = context.object.mode
        
        #for blender to update selected verts, faces
        bpy.ops.object.mode_set(mode='OBJECT')
        selectedFaces = [f for f in bpy.context.object.data.polygons if f.select]
        selectedVerts = [v for v in bpy.context.object.data.vertices if v.select]
        
        if len( selectedFaces ) == 0:
            self.report( {'ERROR'}, 'select one meshs at least.' )
        else:
            norms = Vector()
            centers = Vector()
            for f in selectedFaces:
                norms += f.normal
                centers += f.center
                
            count = len( selectedFaces ) 

            norms_aver = norms / count
            center_aver = centers / count

            try:
                for v in selectedVerts:
                    res = geometry.intersect_line_plane( v.co, v.co + norms_aver, center_aver, norms_aver )
                    v.co = res
            except:
                self.report( {'ERROR'}, 'sorry for unknown error, please retry.' )
            bpy.ops.object.mode_set(mode=mode)
            
    def execute(self, context):
        if context.scene.objects.active == None:
            self.report( {'ERROR'}, 'please pick one object!' )
            return {'FINISHED'}
        else:
            if context.object.mode != 'EDIT':
                self.report( {'ERROR'}, 'should be in the edit mode!' )
            else:
                self.doPlane(context)
            return {'FINISHED'}
        
#bpy.utils.register_module(__name__)
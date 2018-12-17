import bpy, json

def createGeometryByConf( conf ):
    for ob in conf['cmds']:
        cg = ob['category']
        cmdstr = ob['name']
        if cg == 'mesh':
            meshName = ob['props']['name']
            execfunc = getattr(bpy.ops.mesh, cmdstr )
            execfunc()
            currobj = bpy.context.object
            currobj.name = meshName
            
class vic_json_importer_execute(bpy.types.Operator):
    bl_idname = 'vic.vic_json_importer_execute'
    bl_label = ''
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        try:
            loadConfig = open( context.scene.conf_path ).read()
            createGeometryByConf( json.loads( loadConfig ) )
        except:
            self.report( {'ERROR'}, 'format is wrong! must be json format.' )
            return {'CANCELLED'}
        return {'FINISHED'}
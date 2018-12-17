import bpy

def loadScriptFile( root, file ):
    if not file.replace('/','') in bpy.data.texts:
        scriptPath = bpy.utils.script_paths(root)
        file = scriptPath[0] + file
        bpy.ops.text.open(filepath=file, filter_blender=False, filter_image=False, filter_movie=False, filter_python=True, filter_font=False, filter_sound=False, filter_text=True, filter_btx=False, filter_collada=False, filter_folder=True, filemode=9, internal=True)

def addProps( name, type, value ):
    if not name in bpy.context.object.game.properties:
        bpy.ops.object.game_property_new()
        bpy.context.object.game.properties['prop'].name = name
        bpy.context.object.game.properties[name].type = type
        bpy.context.object.game.properties[name].value = value
    
def addAlwaysSensor( sensor_name, use_pulse_true_level ):
    if not sensor_name in bpy.context.object.game.sensors:
        bpy.ops.logic.sensor_add(type='ALWAYS',name=sensor_name)
    bpy.context.object.game.sensors[sensor_name].use_pulse_true_level = use_pulse_true_level
    bpy.context.object.game.sensors[sensor_name].show_expanded = False
    
def addPythonController( cont_name, link_name, script_name ):
    if not cont_name in bpy.context.object.game.controllers:
        bpy.ops.logic.controller_add(type='PYTHON', name=cont_name, object="")
    bpy.context.object.game.controllers[cont_name].mode = 'SCRIPT'
    bpy.context.object.game.controllers[cont_name].text = bpy.data.texts[script_name]
    bpy.context.object.game.controllers[cont_name].link(bpy.context.object.game.sensors[link_name])    
    bpy.context.object.game.controllers[cont_name].show_expanded = False
            
class vic_bge_hand_drag(bpy.types.Operator):
    bl_idname = 'vic.bge_hand_drag'
    bl_label = 'Make It Drag'
    
    def loadScript( self ):
        loadScriptFile( "addons/vic/bge_hand_drag", '/InitEffect.py' )
        loadScriptFile( "addons/vic/bge_hand_drag", '/UpdateEffect.py' )
        
    def makeEffect( self ):
        addAlwaysSensor( 'Always_DragEffectInit', False)
        addAlwaysSensor( 'Always_DragEffectUpdate', True)
        addPythonController('Python_DragEffectInit_Init', 'Always_DragEffectInit','InitEffect.py')
        addPythonController('Python_DragEffectInit_Update', 'Always_DragEffectUpdate','UpdateEffect.py')
        
        addProps( 'init_pos', 'STRING', '' )
        addProps( 'force_pos', 'STRING', '' )
        addProps( 'proxy_pos', 'STRING', '' )
        addProps( 'detail', 'FLOAT', 1 )
            
    def execute(self, context):
        if context.object is None:
            self.report( {'ERROR'}, 'need one object selected!' )
        else:
            self.loadScript()
            self.makeEffect()
            return {'FINISHED'}
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

def addKeyboardSensor( sensor_name,  use_pulse_true_level, key ):
    if not sensor_name in bpy.context.object.game.sensors:
        bpy.ops.logic.sensor_add(type='KEYBOARD',name=sensor_name)
    bpy.context.object.game.sensors[sensor_name].use_pulse_true_level = use_pulse_true_level
    bpy.context.object.game.sensors[sensor_name].key = key
    bpy.context.object.game.sensors[sensor_name].show_expanded = False
    
def addLogicController( sensor_name, link_name ):
    if not sensor_name in bpy.context.object.game.controllers:
        bpy.ops.logic.controller_add(type='LOGIC_AND',name=sensor_name)
    bpy.context.object.game.controllers[sensor_name].link(bpy.context.object.game.sensors[link_name])    
    bpy.context.object.game.controllers[sensor_name].show_expanded = False

def addMotionActuator( sensor_name, link_name, loc, rot ):
    if not sensor_name in bpy.context.object.game.actuators:
        bpy.ops.logic.actuator_add(type='MOTION',name=sensor_name)
    bpy.context.object.game.actuators[sensor_name].link(bpy.context.object.game.controllers[link_name])         
    bpy.context.object.game.actuators[sensor_name].offset_location[0] = loc[0]
    bpy.context.object.game.actuators[sensor_name].offset_location[1] = loc[1]
    bpy.context.object.game.actuators[sensor_name].offset_location[2] = loc[2]
    bpy.context.object.game.actuators[sensor_name].offset_rotation[0] = rot[0]
    bpy.context.object.game.actuators[sensor_name].offset_rotation[1] = rot[1]
    bpy.context.object.game.actuators[sensor_name].offset_rotation[2] = rot[2]
    bpy.context.object.game.actuators[sensor_name].show_expanded = False
            
class vic_bge_quick_motion(bpy.types.Operator):
    bl_idname = 'vic.bge_quick_motion'
    bl_label = 'Quick Character'
    
    def makeEffect( self ):
        addKeyboardSensor( 'Keyboard_QuickMotion_W', False, 'W' )
        addKeyboardSensor( 'Keyboard_QuickMotion_S', False, 'S' )
        addKeyboardSensor( 'Keyboard_QuickMotion_A', False, 'A' )
        addKeyboardSensor( 'Keyboard_QuickMotion_D', False, 'D' )
        addKeyboardSensor( 'Keyboard_QuickMotion_SPACE', False, 'SPACE' )
        addLogicController( 'Logic_QuickMotion_W', 'Keyboard_QuickMotion_W' )
        addLogicController( 'Logic_QuickMotion_S', 'Keyboard_QuickMotion_S' )
        addLogicController( 'Logic_QuickMotion_A', 'Keyboard_QuickMotion_A' )
        addLogicController( 'Logic_QuickMotion_D', 'Keyboard_QuickMotion_D' )
        addLogicController( 'Logic_QuickMotion_SPACE', 'Keyboard_QuickMotion_SPACE' )
        addMotionActuator( 'Motion_QuickMotion_W', 'Logic_QuickMotion_W', [0,.1,0], [0,0,0] )
        addMotionActuator( 'Motion_QuickMotion_S', 'Logic_QuickMotion_S', [0,-.1,0], [0,0,0] )
        addMotionActuator( 'Motion_QuickMotion_A', 'Logic_QuickMotion_A', [-.1,0,0], [0,0,0] )
        addMotionActuator( 'Motion_QuickMotion_D', 'Logic_QuickMotion_D', [.1,0,0], [0,0,0] )
        addMotionActuator( 'Motion_QuickMotion_SPACE', 'Logic_QuickMotion_SPACE', [0,0,0], [0,0,0] )
        bpy.context.object.game.actuators['Motion_QuickMotion_SPACE'].mode = 'OBJECT_CHARACTER'
        bpy.context.object.game.actuators['Motion_QuickMotion_SPACE'].use_character_jump = True
        bpy.context.object.game.physics_type = 'CHARACTER'
        
    def execute(self, context):
        if context.object is None:
            self.report( {'ERROR'}, 'need one object selected!' )
        else:
            self.makeEffect()
            return {'FINISHED'}
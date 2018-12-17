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
    
def addAlwaysSensor():
    if not 'Always_PureParticle' in bpy.context.object.game.sensors:
        bpy.ops.logic.sensor_add(type='ALWAYS',name='Always_PureParticle')
    bpy.context.object.game.sensors['Always_PureParticle'].use_pulse_true_level = True
    
def addPythonController( cont_name, script_name ):
    if not cont_name in bpy.context.object.game.controllers:
        bpy.ops.logic.controller_add(type='PYTHON', name=cont_name, object="")
    bpy.context.object.game.controllers[cont_name].mode = 'SCRIPT'
    bpy.context.object.game.controllers[cont_name].text = bpy.data.texts[script_name]
    bpy.context.object.game.controllers[cont_name].link(bpy.context.object.game.sensors['Always_PureParticle'])    
    
def addLogicController():
    if not 'Logic_PureParticle' in bpy.context.object.game.controllers:
        bpy.ops.logic.controller_add(type='LOGIC_AND',name='Logic_PureParticle')
    bpy.context.object.game.controllers['Logic_PureParticle'].link(bpy.context.object.game.sensors['Always_PureParticle'])    
    
def addEditObjectActuator():
    if not 'EditObject_PureParticle' in bpy.context.object.game.actuators:
        bpy.ops.logic.actuator_add(type='EDIT_OBJECT',name='EditObject_PureParticle')
    bpy.context.object.game.actuators['EditObject_PureParticle'].mode = 'TRACKTO'
    if 'Camera' in bpy.data.objects:
        bpy.context.object.game.actuators['EditObject_PureParticle'].track_object = bpy.data.objects["Camera"]
    bpy.context.object.game.actuators['EditObject_PureParticle'].up_axis = 'UPAXISY'
    bpy.context.object.game.actuators['EditObject_PureParticle'].track_axis = 'TRACKAXISZ'
    bpy.context.object.game.actuators['EditObject_PureParticle'].use_3d_tracking = True
    bpy.context.object.game.actuators['EditObject_PureParticle'].link(bpy.context.object.game.controllers['Logic_PureParticle'])       

class vic_pure_particle_sprite_rotable(bpy.types.Operator):
    bl_idname = 'vic.pure_particle_sprite_rotable'
    bl_label = 'Make It Sprite'
    
    def loadScript( self ):
        loadScriptFile( "addons/vic/bge_pure_particle", '/Sprite.py' )
            
    def makeSprite( self ):
        addAlwaysSensor()
        addPythonController('Python_PureParticle_Sprite','Sprite.py')
        addProps( 'look_at', 'STRING', 'Camera' )
        addProps( 's_rotation', 'FLOAT', 0 )
        
    def execute(self, context):
        if context.object is None:
            self.report( {'ERROR'}, 'need one object selected!' )
        else:
            self.loadScript()
            self.makeSprite()
            return {'FINISHED'}
'''            
class vic_pure_particle_sprite(bpy.types.Operator):
    bl_idname = 'vic.pure_particle_sprite'
    bl_label = 'Make Sprite'
    
    def makeSprite( self ):
        addAlwaysSensor()
        addLogicController()
        addEditObjectActuator()
        
    def execute(self, context):
        if context.object is None:
            self.report( {'ERROR'}, 'need one object selected!' )
        else:
            self.makeSprite()
            return {'FINISHED'}
'''
class vic_pure_particle(bpy.types.Operator):
    bl_idname = 'vic.pure_particle'
    bl_label = 'Make It Emitter'
    
    def loadScript( self ):
        loadScriptFile( "addons/vic/bge_pure_particle", '/Emitter.py' )
        
    def makeParticle( self ):
        addAlwaysSensor()
        addPythonController('Python_PureParticle_Emitter','Emitter.py')
        
        #props with 'e_' is meaning that is emitter properties, here is for self
        addProps( 'e_born_name', 'STRING', '' )
        addProps( 'e_frequence', 'INT', 10 )
        addProps( 'e_duration', 'INT', 0 )
        addProps( 'e_rand_duration', 'INT', 0 )
        addProps( 'e_size_in', 'INT', 0 )        
        addProps( 'e_size_out', 'INT', 0 ) 
        addProps( 'e_alpha_in', 'INT', 0 ) 
        addProps( 'e_alpha_out', 'INT', 0 ) 
        addProps( 'e_rot_align_speed', 'BOOL', False ) 
        addProps( 'e_is_rigid', 'BOOL', False )
        
        #props with 'p_' is meaning that is particle properties, here is for the children
        addProps( 'p_friction', 'FLOAT', 1 )
        addProps( 'p_gravity', 'FLOAT', 0 )        
        addProps( 'p_size', 'FLOAT', 1 )      
        addProps( 'p_rand_size', 'FLOAT', 0 )        
        addProps( 'p_alpha', 'FLOAT', 1 )  
        addProps( 'p_rand_alpha', 'FLOAT', 0 ) 
        addProps( 'p_rand_pos_x', 'FLOAT', 0 ) 
        addProps( 'p_rand_pos_y', 'FLOAT', 0 )            
        addProps( 'p_rand_pos_z', 'FLOAT', 0 ) 
        addProps( 'p_rand_rot_x', 'FLOAT', 0 ) 
        addProps( 'p_rand_rot_y', 'FLOAT', 0 ) 
        addProps( 'p_rand_rot_z', 'FLOAT', 0 ) 
        addProps( 'p_vel_x', 'FLOAT', 0 )
        addProps( 'p_vel_y', 'FLOAT', 0 )
        addProps( 'p_vel_z', 'FLOAT', 0 )
        addProps( 'p_rand_vel_x', 'FLOAT', 0 )
        addProps( 'p_rand_vel_y', 'FLOAT', 0 )
        addProps( 'p_rand_vel_z', 'FLOAT', 0 )
        addProps( 'p_rot_vel_x', 'FLOAT', 0 )
        addProps( 'p_rot_vel_y', 'FLOAT', 0 )
        addProps( 'p_rot_vel_z', 'FLOAT', 0 )
        addProps( 'p_rand_rot_vel_x', 'FLOAT', 0 )
        addProps( 'p_rand_rot_vel_y', 'FLOAT', 0 )
        addProps( 'p_rand_rot_vel_z', 'FLOAT', 0 )   

        #props with 's_' is meaning that is system properties, not need to set value
        addProps( 's_inited', 'BOOL', False )
        addProps( 's_time', 'INT', 0 )
        addProps( 's_gravity', 'FLOAT', 0 )
        addProps( 's_friction', 'FLOAT', 1 )
        addProps( 's_vel_x', 'FLOAT', 0 )
        addProps( 's_vel_y', 'FLOAT', 0 )
        addProps( 's_vel_z', 'FLOAT', 0 )
        addProps( 's_rot_vel', 'FLOAT', 0 )
        addProps( 's_rotation', 'FLOAT', 0 )
        addProps( 's_size', 'FLOAT', 1 )
        addProps( 's_alpha', 'FLOAT', 1 )
        addProps( 's_max_size', 'FLOAT', 1 )
        addProps( 's_max_alpha', 'FLOAT', 1 )
            
    def execute(self, context):
        if context.object is None:
            self.report( {'ERROR'}, 'need one object selected!' )
        else:
            self.loadScript()
            self.makeParticle()
            return {'FINISHED'}
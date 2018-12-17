import bpy
from mathutils import Vector
from mathutils import noise
from mathutils import Color

def collectVertexColor( mesh, color_layer ):
    ret = {}
    i = 0
    for poly in mesh.polygons:
        for idx in poly.loop_indices:
            loop = mesh.loops[idx]
            v = loop.vertex_index
            linked = ret.get(v, [])
            linked.append(color_layer.data[i].color)
            ret[v] = linked
            i += 1
    return ret    
    
def avg_col(cols):
    avg_col = Color((0.0, 0.0, 0.0))
    for col in cols:
        avg_col += col/len(cols)
    return avg_col    

def addProps( target, name, value, override = False ):
    if not name in target or override:
        target.data[name] = value
        
def back_to_origin_vertex_position( target ):
    for i, v in enumerate( target.data.vertices, 0 ):
        target.data.vertices[i].co = target.data['vic_init_vertex_position'][i]
        to_proxy = target.matrix_world * Vector( target.data['vic_init_vertex_position'][i] )
        target.data['vic_proxy_vertex_position'][i][0] = to_proxy.x
        target.data['vic_proxy_vertex_position'][i][1] = to_proxy.y
        target.data['vic_proxy_vertex_position'][i][2] = to_proxy.z
        
def save_vertex_position( target ):
    # active when 1, or close by 0
    addProps( target, 'vic_active', True )
    # no nagetive number, the higher value the more detail
    addProps( target, 'vic_detail', 1.0 )
    # 0.0~1.0 will be best!    
    addProps( target, 'vic_effective', 1.0 )
    # using vertex color
    addProps( target, 'vic_using_vertex_color_map', False  )
    # using vertex color for effective value
    addProps( target, 'vic_effective_by_vertex_color', 'Col' )
    
    detail = target.data['vic_detail']
    map_vertex_color = target.data['vic_effective_by_vertex_color'] 

    addProps( target, 'vic_init_vertex_position', [ v.co.copy() for v in target.data.vertices ], True)
    addProps( target, 'vic_proxy_vertex_position', [ target.matrix_world * v.co.copy() for v in target.data.vertices ], True )
    
    if map_vertex_color in target.data.vertex_colors:
        collect_color = collectVertexColor( target.data, target.data.vertex_colors[map_vertex_color] )  
        map_vertexs = [avg_col(v).hsv[2] for k, v in collect_color.items() ]
        addProps( target, 'vic_force_for_each_vertex_by_vertex_color', map_vertexs, True )            
    else:
        addProps( target, 'vic_force_for_each_vertex_by_vertex_color', [ .2 for v in target.data.vertices ], True )
    addProps( target, 'vic_force_for_each_vertex', [ ((noise.noise(Vector(v)*detail)) + 1) / 2 for v in target.data['vic_init_vertex_position'] ], True )            
    
def move_vertice( target ):
    mat = target.matrix_world
    vs = target.data.vertices
    
    # check the object is not in the scene
    if not 'vic_init_vertex_position' in target.data: return None

    active = target.data['vic_active']
    if active == 0: return None

    init_pos = target.data['vic_init_vertex_position']
    proxy_pos = target.data['vic_proxy_vertex_position']
    force_pos = target.data['vic_force_for_each_vertex_by_vertex_color'] if target.data['vic_using_vertex_color_map'] else target.data['vic_force_for_each_vertex']
    effective = target.data['vic_effective']
    
    for i, v in enumerate(vs,0):
        toPos = mat * Vector( init_pos[i] )
        proxy_pos_vec = Vector(proxy_pos[i])
        proxy_pos_vec += (toPos - proxy_pos_vec) * force_pos[i] * effective   
        set_pos = mat.inverted() * proxy_pos_vec
        v.co = set_pos
                
        proxy_pos[i][0] = proxy_pos_vec.x
        proxy_pos[i][1] = proxy_pos_vec.y
        proxy_pos[i][2] = proxy_pos_vec.z
        
def filterCanEffect( objs ):   
    return [ o for o in objs if o.data is not None and hasattr( o.data, 'vertices' ) ]   

def update( scene ):
    eff_objects = filterCanEffect( bpy.data.objects )
    for o in eff_objects:
        if 'vic_active' in o.data:
            move_vertice( o )
            
def addListener():
    #if update in bpy.app.handlers.frame_change_pre:
    try:
        bpy.app.handlers.frame_change_pre.remove( update )
    except:
        print( 'update handler is not in the list' )
    bpy.app.handlers.frame_change_pre.append( update )   

class vic_hand_drag(bpy.types.Operator):
    bl_idname = 'vic.hand_drag'
    bl_label = 'Make It Drag'
        
    def doEffect( self ):
        init_objects = filterCanEffect( bpy.context.selected_objects.copy() )
        for o in init_objects:
            save_vertex_position( o )
        addListener() 
    def execute(self, context):
        self.doEffect()
        return {'FINISHED'}
        '''
class vic_set_value_to_all_effect_object( bpy.types.Operator):
    bl_idname = 'vic.set_value_to_all_effect_object'
    bl_label = 'Rewalk All Active Object'
        
    def doEffect( self ):
        init_objects = filterCanEffect( bpy.data.objects )
        for o in init_objects:
            if 'vic_active' in o:
                save_vertex_position( o )
        addListener()
    def execute(self, context):
        self.doEffect()
        return {'FINISHED'}     
    '''
class vic_healing_all_effect_objects( bpy.types.Operator):
    bl_idname = 'vic.healing_all_effect_objects'
    bl_label = 'Healing All'
        
    def doEffect( self ):
        bpy.context.scene.frame_current = 1
        bpy.ops.object.paths_calculate()
        init_objects = filterCanEffect( bpy.data.objects )
        for o in init_objects:
            if 'vic_active' in o.data:
                back_to_origin_vertex_position( o )
        bpy.ops.object.paths_clear()
        addListener()        
    def execute(self, context):
        self.doEffect()
        return {'FINISHED'}         
    
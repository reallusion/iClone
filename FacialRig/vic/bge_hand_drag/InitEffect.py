from bge import logic
from mathutils import Vector
from mathutils import noise
import json

cont = logic.getCurrentController()
owner = cont.owner

init_pos = []
detail = owner['detail']

def push_init_pos( add_point ):
    global init_pos
    need_add = True
    for p in init_pos:
        if p[0] == add_point[0] and p[1] == add_point[1] and p[2] == add_point[2]:
            need_add = False
            p[3].append( add_point[3][0] )
    if need_add:
        init_pos.append( add_point )        
        
for mesh_index, mesh in enumerate( owner.meshes, 0 ):
    for m_index in range(len(mesh.materials)):
        for v_index in range(mesh.getVertexArrayLength(m_index)):
            vertex = mesh.getVertex(m_index, v_index)
            push_init_pos( [vertex.x,vertex.y,vertex.z, [[mesh_index, m_index, v_index]]] )
 
force_pos = [ ( noise.noise( Vector([p[0],p[1],p[2]]) * detail ) + 1 ) / 2 for p in init_pos ]
proxy_pos_vec = [ owner.worldTransform * Vector([p[0],p[1],p[2]]) for p in init_pos ]
proxy_pos = [[p[0],p[1],p[2]] for p in proxy_pos_vec ]

owner['init_pos'] = json.dumps( init_pos )   
owner['proxy_pos'] = json.dumps( proxy_pos )   
owner['force_pos'] = json.dumps( force_pos )   
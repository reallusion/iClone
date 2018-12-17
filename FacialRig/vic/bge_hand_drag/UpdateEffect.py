from bge import logic
from mathutils import Vector
import json

cont = logic.getCurrentController()
owner = cont.owner

init_pos = json.loads( owner['init_pos'] )
force_pos = json.loads( owner['force_pos'] )
proxy_pos = json.loads( owner['proxy_pos'] )

for i,v in enumerate( init_pos, 0 ):
    moveTo = Vector( [init_pos[i][0],init_pos[i][1],init_pos[i][2]] )
    moveTo = owner.worldTransform * moveTo
    current_pos = Vector( proxy_pos[i] )
    current_pos += ( moveTo - current_pos ) * force_pos[i]
    
    proxy_pos[i][0] = current_pos.x
    proxy_pos[i][1] = current_pos.y
    proxy_pos[i][2] = current_pos.z
    
    current_pos = owner.worldTransform.inverted() * current_pos
    for v in init_pos[i][3]:
        vertex = owner.meshes[v[0]].getVertex( v[1], v[2] )
        vertex.setXYZ( current_pos )
        
owner['proxy_pos'] = json.dumps(proxy_pos)  
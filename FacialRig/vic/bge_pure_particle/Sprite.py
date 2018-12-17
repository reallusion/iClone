import bge
from mathutils import Vector 
from mathutils import Euler
from mathutils import Matrix

scene = bge.logic.getCurrentScene()
cont = bge.logic.getCurrentController()
owner = cont.owner
lookat = owner['look_at']
spriteRotation = owner['s_rotation']

if lookat in scene.objects:
    # Matrix for facing to camera
    m1 = scene.objects[lookat].orientation
    # Matrix for rotate sprite    
    m2 = Matrix.Rotation( spriteRotation / 180 * 3.14, 4, Vector([0,0,1]) ).to_3x3()
    m_result = m1 * m2
    owner.orientation = m_result.to_euler()

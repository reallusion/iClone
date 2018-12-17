import bge 
from mathutils import Vector
from mathutils import Matrix
from mathutils import Euler
from random import random

scene = bge.logic.getCurrentScene()
cont = bge.logic.getCurrentController()
owner = cont.owner

size = owner['p_size']
randomSize = owner['p_rand_size']
alpha = owner['p_alpha']
randomAlpha = owner['p_rand_alpha']
randomPosition = Vector([owner['p_rand_pos_x'],owner['p_rand_pos_y'],owner['p_rand_pos_z']])
randomRotation = Vector([owner['p_rand_rot_x'],owner['p_rand_rot_y'],owner['p_rand_rot_z']])
initForce = Vector([owner['p_vel_x'],owner['p_vel_y'],owner['p_vel_z']])
randomForce = Vector([owner['p_rand_vel_x'],owner['p_rand_vel_y'],owner['p_rand_vel_z']])
initRotForce = Vector([owner['p_rot_vel_x'],owner['p_rot_vel_y'],owner['p_rot_vel_z']])
randomRotForce = Vector([owner['p_rand_rot_vel_x'],owner['p_rand_rot_vel_y'],owner['p_rand_rot_vel_z']])
friction = owner['p_friction']
gravity = owner['p_gravity']

inited = owner['s_inited']
time = owner['s_time']
selfAcc = Vector([0,0,owner['s_gravity']])
selfVel = Vector([owner['s_vel_x'],owner['s_vel_y'],owner['s_vel_z']])
selfFric = owner['s_friction']
selfRotVel = owner['s_rot_vel']
selfRot = owner['s_rotation']
selfSize = owner['s_size']
selfAlpha = owner['s_alpha']
selfMaxSize = owner['s_max_size']
selfMaxAlpha = owner['s_max_alpha']

sizeIn = owner['e_size_in']
sizeOut = owner['e_size_out']
alphaIn = owner['e_alpha_in']
alphaOut = owner['e_alpha_out']
duration = owner['e_duration']
randomDuration = owner['e_rand_duration']
bornName = owner['e_born_name']
isRigid = owner['e_is_rigid']
frequence = owner['e_frequence']
rotAlignSpeed = owner['e_rot_align_speed']

def createParticle():
    s = scene.addObject(bornName)
    s.localScale = [0,0,0]
    
    addPos = Vector()
    addPos.x = random() * randomPosition.x - randomPosition.x / 2
    addPos.y = random() * randomPosition.y - randomPosition.y / 2
    addPos.z = random() * randomPosition.z - randomPosition.z / 2    
    s.worldPosition = owner.worldPosition + addPos
    
    addPos.x = random() * randomRotation.x - randomRotation.x / 2
    addPos.y = random() * randomRotation.y - randomRotation.y / 2
    addPos.z = random() * randomRotation.z - randomRotation.z / 2    
    s.orientation = Euler( addPos )
    
    s['s_rotation'] = addPos.z
    
    addPos.x = random() * randomForce.x - randomForce.x / 2
    addPos.y = random() * randomForce.y - randomForce.y / 2
    addPos.z = random() * randomForce.z - randomForce.z / 2 
    addPos = addPos + initForce
    s.applyForce( addPos )
        
    s['s_vel_x'] = addPos.x
    s['s_vel_y'] = addPos.y
    s['s_vel_z'] = addPos.z
    
    addPos.x = random() * randomRotForce.x - randomRotForce.x / 2
    addPos.y = random() * randomRotForce.y - randomRotForce.y / 2
    addPos.z = random() * randomRotForce.z - randomRotForce.z / 2        
    addPos = addPos + initRotForce    
    s.applyTorque( addPos )
    
    s['s_rot_vel'] = addPos.z
    s['s_friction'] = friction
    s['s_gravity'] = gravity
    s['s_size'] = 0
    s['s_max_alpha'] = alpha + ( random() * randomAlpha - randomAlpha / 2 )
    s['s_max_size'] = size + ( random() * randomSize - randomSize / 2 )
    
def processEmitter():
    if bornName is not '':
        if frequence is 0:
            createParticle()
        elif frequence is not 0 and time % frequence is 0:
            createParticle()
            
def getScalePercent( valueIn, valueOut):
    if time < valueIn:
        retValue = time / valueIn
    elif time > (duration - valueOut):
        retValue = 1 - (( time - ( duration - valueOut )) / valueOut )  
    else:
        retValue = 1
    return retValue       
        
def update():
    global time, selfSize
    time = time + 1
    owner['s_time'] = time
    owner.localScale.x = owner.localScale.y = owner.localScale.z = selfSize
    owner.color[3] = selfAlpha

    if not isRigid:
        global selfVel, selfRot
        selfVel = selfVel + selfAcc
        selfVel = selfVel * selfFric
        owner.worldPosition = owner.worldPosition + selfVel
        
        owner['s_vel_x'] = selfVel.x
        owner['s_vel_y'] = selfVel.y
        owner['s_vel_z'] = selfVel.z      
        
        if rotAlignSpeed:
            row1 = selfVel.normalized()
            row2 = row1.cross( Vector([0,0,1])).normalized()
            row3 = row1.cross( row2 ).normalized()
            rm = Matrix([row3,row2,row1])
            owner.orientation  = rm.transposed().to_euler()
        else:
            selfRot = selfRot + selfRotVel
            owner['s_rotation'] = selfRot
            
    if duration is 0:
        owner['s_size'] = selfMaxSize
        owner['s_alpha'] = selfMaxAlpha
        processEmitter()
    else:
        if time < duration:
            owner['s_size'] = getScalePercent(sizeIn, sizeOut) * selfMaxSize
            owner['s_alpha'] = getScalePercent(alphaIn, alphaOut) * selfMaxAlpha
            
            processEmitter()
        else:
            owner.endObject()

def init():
    global duration
    duration = duration + random() * randomDuration * 2 - randomDuration
    owner['e_duration'] = duration
    if duration <= 0:
        duration = 0
    owner['s_inited'] = True
    
if not inited:
    init()
            
update()        

    
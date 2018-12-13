import os
import sys
import math
import copy
import RLPy
import BoneData
import KeyData
from KeyData import Keys
from enum import IntEnum

# constants
CHANNELS = 6     #translation (x, y, z) and rotation (x, y ,z) in each bone
NUM_OF_HAND_BONE = 20
HAND_BONE_INDEX_OFFSET = 16
NUM_OF_KEYS = 7

class HandRiggerState(IntEnum):
    Disable = 0
    Ready   = 1
    Running = 2

class BlendMode(IntEnum):
    InverseSquareDistance = 0
    NearestTwoKeys = 1
    Count = 2  #number of blend modes

sys.dont_write_bytecode = True

# global data
avatar = None
hand_device = None
keys = []
device_data = None

# RL API data member
mocap_manager = RLPy.RGlobal.GetMocapManager()

class HandRigger(object):
    def __init__(self):
        global mocap_manager
        global hand_device
        global keys

        self.state = HandRiggerState.Disable
        self.blend_mode = BlendMode.NearestTwoKeys

        key_data = Keys()
        keys = key_data.get_data()
        hand_device = mocap_manager.AddHandDevice('hand_rigger')

        if hand_device != None:
            # device setting
            device_setting = hand_device.GetDeviceSetting()
            device_setting.SetMocapCoordinate(RLPy.ECoordinateAxis_Y, RLPy.ECoordinateAxis_Z, RLPy.ECoordinateSystem_RightHand)
            pos_setting = device_setting.GetPositionSetting()
            pos_setting.SetCoordinateSpace(RLPy.ECoordinateSpace_Local)
            pos_setting.SetUnit(RLPy.EPositionUnit_Centimeters)
            rot_setting = device_setting.GetRotationSetting()
            rot_setting.SetCoordinateSpace(RLPy.ECoordinateSpace_Local)
            rot_setting.SetType(RLPy.ERotationType_Euler)
            rot_setting.SetUnit(RLPy.ERotationUnit_Degrees)
            rot_setting.SetEulerOrder(RLPy.EEulerOrder_ZXY)

            bone_list = BoneData.get_bone_list()
            hand_device.Initialize(bone_list)

    def __del__(self):
        global mocap_manager
        global hand_device
        global keys

        mocap_manager.RemoveAllDevices()
        del hand_device
        hand_device = None
        keys = []
    
    def set_state(self, state):
        global mocap_manager
        self.state = state

        if self.state is HandRiggerState.Disable:
            mocap_manager.Stop()

    def get_state(self):
        return self.state

    def set_blend_mode(self, mode):
        self.blend_mode = mode

    def get_blend_mode(self):
        return self.blend_mode

    def update_state(self):
        global avatar
        global hand_device

        if avatar:
            hand_device.RemoveAvatar(avatar)
            avatar = None

        selection_list = RLPy.RScene.GetSelectedObjects()
        if len(selection_list) > 0:
            for object in selection_list:  # find first avatar
                object_type = object.GetType()
                if object_type == RLPy.EObjectType_Avatar:
                    avatar = object
                    if hand_device is not None:
                        hand_device.AddAvatar(avatar)
                        hand_device.SetProcessDataIndex(avatar, 0)
                        self.set_state(HandRiggerState.Ready)
                        return

        self.set_state(HandRiggerState.Disable)

    def run(self):
        global mocap_manager
        global hand_device
        global avatar

        if self.state == HandRiggerState.Ready:
            if mocap_manager is not None:
                hand_device.SetEnable(avatar, True)
                self.initialize_avatar()
                mocap_manager.Start(RLPy.EMocapState_Preview)
                self.set_state(HandRiggerState.Running)

        elif self.state == HandRiggerState.Running:
            if mocap_manager is not None:
                mocap_manager.Stop()
                self.set_state(HandRiggerState.Ready)

    def initialize_avatar(self):
        global hand_device
        global avatar

        if hand_device is not None and avatar is not None:
            # avatar's hand setting
            hand_setting = hand_device.GetHandSetting(avatar)
            hand_setting.SetRightHandJoin(RLPy.EHandJoin_Wrist)
            hand_setting.SetLeftHandJoin(RLPy.EHandJoin_Wrist)
            hand_setting.SetHandJoinType(RLPy.EHandJoinType_UseParentBone)
            hand_setting.SetRightHandDataSource(RLPy.EHandDataSource_RightHand)
            hand_setting.SetLeftHandDataSource(RLPy.EHandDataSource_RightHand)
            hand_setting.SetActivePart(RLPy.EBodyActivePart_Hand_R | RLPy.EBodyActivePart_Finger_R |
                                       RLPy.EBodyActivePart_Hand_L | RLPy.EBodyActivePart_Finger_L)

    def process_data(self, square_dist):
        global keys
        global hand_device
        global mocap_manager
        global device_data
        global avatar
        key_weights = []

        if hand_device.IsTPoseReady(avatar) == False:
            t_pose = BoneData.get_t_pose()
            device_data = copy.deepcopy(t_pose)
            hand_device.SetTPoseData(avatar, t_pose)
            key_weights = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            if self.blend_mode == BlendMode.InverseSquareDistance:
                key_weights = inverse_square_distance(square_dist)
            elif self.blend_mode == BlendMode.NearestTwoKeys:
                key_weights = nearest_two_keys(square_dist)
            hand_device.ProcessData(0, device_data, -1)

        return key_weights

def inverse_square_distance(square_dist):
    global keys
    global device_data
    key_weights = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    channel_offset = CHANNELS * HAND_BONE_INDEX_OFFSET
    num_of_hand_bone_channels = CHANNELS * NUM_OF_HAND_BONE
    for i in range(NUM_OF_KEYS):
        if square_dist[i] < 0.4:  #set gesture to key[i] and return
            key_weights[i] = 1.0
            for j in range(num_of_hand_bone_channels):
                device_data[channel_offset+j] = keys[i][j]
            return key_weights

    for i in range(NUM_OF_KEYS):
        square_dist[i] = 1/square_dist[i]
    sum = 0
    for i in range(NUM_OF_KEYS):
        sum = sum + square_dist[i]
    for i in range(NUM_OF_KEYS):
        square_dist[i] = square_dist[i]/sum
    for i in range(num_of_hand_bone_channels):
        device_data[channel_offset+i] = 0
        for j in range(NUM_OF_KEYS):
            device_data[channel_offset+i] = device_data[channel_offset+i] + square_dist[j] * keys[j][i]

    key_weights = copy.deepcopy(square_dist)
    return key_weights

def nearest_two_keys(square_dist):
    global keys
    global device_data
    key_weights = []

    channel_offset = CHANNELS * HAND_BONE_INDEX_OFFSET
    num_of_hand_bone_channels = CHANNELS * NUM_OF_HAND_BONE
    weights = []

    for i in range(NUM_OF_KEYS):
        weights.append([i, square_dist[i]])
    sorted_weights = sorted(weights, key = lambda w: w[1])

    key_1_index = sorted_weights[0][0]
    key_2_index = sorted_weights[1][0]
    key_1_dist = math.sqrt(square_dist[key_1_index])
    key_2_dist = math.sqrt(square_dist[key_2_index])
    dist_sum = key_1_dist + key_2_dist
    w1 = key_2_dist/dist_sum
    w2 = key_1_dist/dist_sum
    for i in range(num_of_hand_bone_channels):
        device_data[channel_offset+i] = w1 * keys[key_1_index][i] + w2 * keys[key_2_index][i]

    for i in range(NUM_OF_KEYS):
        if i == key_1_index:
            key_weights.append(w1)
        elif i == key_2_index:
            key_weights.append(w2)
        else:
            key_weights.append(0.0)

    return key_weights

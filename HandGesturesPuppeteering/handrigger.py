# Copyright 2018 The Reallusion Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
import sys
import math
import copy
import RLPy
import BoneData
import time
from enum import IntEnum

# constants
CHANNELS = 6  # translation (x, y, z) and rotation (x, y ,z) in each bone
NUM_OF_HAND_BONE = 17
HAND_BONE_INDEX_OFFSET = 14
NUM_OF_KEYS = 7
KEY_DIST_THRESHOLD = 8.1  # square distance


sys.dont_write_bytecode = True

# global data
avatar = None
hand_device = None
keys = [0, 0, 0, 0, 0, 0, 0]
device_data = None
local_data = [None]*NUM_OF_KEYS
slerped_local = [None]*(NUM_OF_HAND_BONE*7)  # 2keys, 7keys 共用
slerped_local_11 = [None]*(NUM_OF_HAND_BONE*7)
slerped_local_12 = [None]*(NUM_OF_HAND_BONE*7)
slerped_local_13 = [None]*(NUM_OF_HAND_BONE*7)
slerped_local_21 = [None]*(NUM_OF_HAND_BONE*7)
slerped_local_22 = [None]*(NUM_OF_HAND_BONE*7)
key_weights = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# for 2keys interpolation
key_1_index = 0
key_2_index = 0
w1 = 0.0
w2 = 0.0

parent_idx = [-1, 0,
              1, 2, 3,
              1, 5, 6,
              1, 8, 9,
              1, 11, 12,
              1, 14, 15]

# RL API data member
mocap_manager = RLPy.RGlobal.GetMocapManager()

start_time = RLPy.RTime(0)


class QuaternionQ:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def getData(self):
        return {"X": self.x, "Y": self.y, "Z": self.z, "W": self.w}


class HandRiggerState(IntEnum):
    Disable = 0
    Ready = 1
    ReadyToRun = 2
    Preview = 3
    Record = 4


class BlendMode(IntEnum):
    InverseSquareDistance = 0
    NearestTwoKeys = 1


class JoinMode(IntEnum):
    Both = 0
    Right = 1
    Left = 2


class HandRigger(object):
    def __init__(self):
        global mocap_manager
        global hand_device
        global keys

        self.state = HandRiggerState.Disable
        self.blend_mode = BlendMode.InverseSquareDistance
        self.join_mode = JoinMode.Both
        self.edit_gesture_id = 0
        self.clip_transition_frames = 6

        hand_device = mocap_manager.AddHandDevice('hand_rigger')

        if hand_device is not None:
            # device setting
            device_setting = hand_device.GetDeviceSetting()
            device_setting.SetMocapCoordinate(RLPy.ECoordinateAxis_Z, RLPy.ECoordinateAxis_NegativeY, RLPy.ECoordinateSystem_RightHand)
            pos_setting = device_setting.GetPositionSetting()
            pos_setting.SetCoordinateSpace(RLPy.ECoordinateSpace_World)
            pos_setting.SetUnit(RLPy.EPositionUnit_Centimeters)
            rot_setting = device_setting.GetRotationSetting()
            rot_setting.SetCoordinateSpace(RLPy.ECoordinateSpace_World)
            rot_setting.SetType(RLPy.ERotationType_Euler)
            rot_setting.SetUnit(RLPy.ERotationUnit_Degrees)
            rot_setting.SetEulerOrder(RLPy.EEulerOrder_XYZ)

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

    def set_join_mode(self, mode):
        self.join_mode = mode

    def set_clip_transition_frames(self, frames):
        self.clip_transition_frames = frames

    def replace_gesture(self, gesture_id, key_data):
        global keys
        keys[gesture_id] = key_data

    def get_clip_and_end_time(self, cur_time):
        global avatar
        skel_comp = avatar.GetSkeletonComponent()
        if skel_comp == None:
            return
        find_clip = None
        clip_count = skel_comp.GetClipCount()
        clip_start_time = RLPy.RTime(0)
        clip_end_time = RLPy.RTime(0)
        for i in range(clip_count):
            clip = skel_comp.GetClip(i)
            clip_length = clip.GetClipLength()
            clip_start_time = clip.ClipTimeToSceneTime(RLPy.RTime(0))
            clip_end_time = clip.ClipTimeToSceneTime(clip_length)
            if cur_time >= clip_start_time and cur_time <= clip_end_time:
                find_clip = clip
        return find_clip, clip_end_time

    def find_next_clip_transition_by_time(self, cur_time):
        global avatar
        skel_comp = avatar.GetSkeletonComponent()
        if skel_comp == None:
            return
        find_clip = None
        transition_time = RLPy.RTime(0)
        clip_count = skel_comp.GetClipCount()
        for i in range(clip_count):
            clip = skel_comp.GetClip(i)
            clip_start_time = clip.ClipTimeToSceneTime(RLPy.RTime(0))
            transition_time = clip.GetTransitionRange()
            transition_begin_time = clip_start_time - transition_time
            if transition_begin_time < RLPy.RTime(0):
                continue
            if cur_time >= transition_begin_time and cur_time < clip_start_time:
                find_clip = clip
        return find_clip, transition_time

    def merge_next_clip(self, clip, cur_time, end_time):
        global avatar
        global mocap_manager
        global start_time
        global hand_device
        global device_data
        if avatar is None or clip is None:
            return
        skel_comp = avatar.GetSkeletonComponent()
        if skel_comp is None:
            return

        # break time
        fps = RLPy.RGlobal.GetFps()
        buffer_time = RLPy.RTime.IndexedFrameTime(2, fps)
        break_time = cur_time + RLPy.RTime.IndexedFrameTime(1, fps)

        # break & merge clips
        result = skel_comp.BreakClip(break_time)

        # stop and generate mocap clip
        hand_device.ProcessData(0, device_data, -1)
        mocap_manager.Stop()
        mocap_clip, mocap_time = self.get_clip_and_end_time(start_time)
        remaining_clip, remaining_time = self.get_clip_and_end_time(break_time + RLPy.RTime.IndexedFrameTime(1, fps))

        # merge clips
        if remaining_clip is not None:
            transition_time = RLPy.RTime.IndexedFrameTime(self.clip_transition_frames, fps)
            remaining_clip.SetTransitionRange(transition_time)
            result = skel_comp.MergeClips(mocap_clip, remaining_clip)
            # merge middle clip
            if result.IsError():
                clip_length = mocap_clip.GetClipLength()
                mocap_end_time = mocap_clip.ClipTimeToSceneTime(clip_length)
                remaining_start_time = remaining_clip.ClipTimeToSceneTime(RLPy.RTime(0))
                middle_start_time = RLPy.RTime(0)
                middle_clip, middle_clip_end_time = self.get_clip_and_end_time(remaining_start_time-RLPy.RTime.IndexedFrameTime(1, fps))
                if middle_clip != None:
                    middle_start_time = middle_clip.ClipTimeToSceneTime(RLPy.RTime(0))
                    if middle_start_time != remaining_start_time:
                        skel_comp.MergeClips(mocap_clip, middle_clip)
                        remaining_clip, remaining_time = self.get_clip_and_end_time(end_time)
                        mocap_clip, mocap_time = self.get_clip_and_end_time(start_time)
                        skel_comp.MergeClips(mocap_clip, remaining_clip)

        RLPy.RGlobal.SetTime(cur_time)
        RLPy.RGlobal.ObjectModified(avatar, RLPy.EObjectModifiedType_Transform)
        return True

    def _generate_data(self, motion_bones, right):
        key_data = [
            0, 0, 0, 0, 0, 0,  # 0: forearm
            0, 0, 0, 0, 0, 0,  # 1: hand
            0, 0, 0, 0, 0, 0,  # 2: right_hand_thumb_1
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,  # 5: right_in_hand_index
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,  # 8: right_in_hand_middle
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,  # 11: right_in_hand_ring
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,  # 14 right_in_hand_pinky
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, ]

        # get [forearm/hand] transform
        hand_bone_count = 0
        for bone in motion_bones:
            bone_data_idx = -1
            bone_name = bone.GetName()
            if ((bone_name == "RL_R_Forearm") and right) or ((bone_name == "RL_L_Forearm") and not right):
                bone_data_idx = 0
            elif ((bone_name == "RL_R_Hand") and right) or ((bone_name == "RL_L_Hand") and not right):
                bone_data_idx = 1

            if bone_data_idx > 0:
                translate, euler_angle = self._BoneWorldTransform(bone)
                key_data[6*bone_data_idx+0] = translate.x
                key_data[6*bone_data_idx+1] = translate.y
                key_data[6*bone_data_idx+2] = translate.z
                key_data[6*bone_data_idx+3] = euler_angle.x  # degree
                key_data[6*bone_data_idx+4] = euler_angle.y  # degree
                key_data[6*bone_data_idx+5] = euler_angle.z  # degree
                hand_bone_count += 1

                if hand_bone_count == 2:
                    break

        # modify finger-bone transform
        prefix = "RL_R_Finger" if right else "RL_L_Finger"
        for bone in motion_bones:
            if(prefix in bone.GetName()):
                for finger in range(5):
                    for joint in range(3):
                        if bone.GetName() == f"{prefix}{finger}{joint}":
                            joint_index = 12 + 18*finger + 6*joint  # 12: forearm & hand
                            translate, euler_angle = self._BoneWorldTransform(bone)
                            key_data[joint_index] = translate.x
                            key_data[joint_index+1] = translate.y
                            key_data[joint_index+2] = translate.z
                            key_data[joint_index+3] = euler_angle.x  # degree
                            key_data[joint_index+4] = euler_angle.y  # degree
                            key_data[joint_index+5] = euler_angle.z  # degree
        return key_data

    def _BoneWorldTransform(self, bone):
        world_transform = bone.WorldTransform()
        rot_matrix = world_transform.Rotate()
        translate = world_transform.T()

        rx = ry = rz = 0
        euler_angle_result = rot_matrix.ToEulerAngle(RLPy.EEulerOrder_XYZ, rx, ry, rz)
        euler_angle = RLPy.RVector3(euler_angle_result[0]*RLPy.RMath.CONST_RAD_TO_DEG,
                                    euler_angle_result[1]*RLPy.RMath.CONST_RAD_TO_DEG,
                                    euler_angle_result[2]*RLPy.RMath.CONST_RAD_TO_DEG)
        return translate, euler_angle  # angle (degree)

    def get_avatar(self):
        global avatar
        return avatar

    def all_keys(self):
        global keys
        return keys

    def update_state(self):
        global avatar
        global hand_device

        if avatar:
            hand_device.RemoveAvatar(avatar)
            avatar = None

        selection_list = RLPy.RScene.GetSelectedObjects()
        if len(selection_list) == 1:
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

    def run(self, state):
        global mocap_manager
        global hand_device
        global avatar
        global local_data
        global start_time

        if self.state == HandRiggerState.Ready or self.state == HandRiggerState.ReadyToRun:
            if mocap_manager is not None:
                hand_device.SetEnable(avatar, True)
                self.initialize_avatar()

                local_data[0] = world_to_local(keys[0])
                local_data[1] = world_to_local(keys[1])
                local_data[2] = world_to_local(keys[2])
                local_data[3] = world_to_local(keys[3])
                local_data[4] = world_to_local(keys[4])
                local_data[5] = world_to_local(keys[5])
                local_data[6] = world_to_local(keys[6])

                start_time = RLPy.RGlobal.GetTime()
                if state == HandRiggerState.Preview:
                    mocap_manager.Start(RLPy.EMocapState_Preview)
                elif state == HandRiggerState.Record:
                    mocap_manager.Start(RLPy.EMocapState_Record)
                    self.process_data(int(start_time.GetValue()))
                self.set_state(state)

        elif self.state == HandRiggerState.Preview or self.state == HandRiggerState.Record:
            if mocap_manager is not None:
                stop_manager = True
                next_clip_modified = False
                next_clip_begin_time = RLPy.RTime(0)
                transition_time = RLPy.RTime(0)
                if self.state == HandRiggerState.Record:
                    # check ap version
                    product_min_ver = RLPy.RApplication.GetProductMinorVersion()
                    skel_comp = avatar.GetSkeletonComponent()
                    if skel_comp is not None and hasattr(skel_comp, "BreakClip"):
                        fps = RLPy.RGlobal.GetFps()
                        cur_time = RLPy.RGlobal.GetTime()
                        next_clip, transition_time = self.find_next_clip_transition_by_time(cur_time)
                        if next_clip != None:
                            next_clip_modified = True
                            next_clip_begin_time = next_clip.ClipTimeToSceneTime(RLPy.RTime(0))
                            next_clip.SetTransitionRange(RLPy.RTime(0))
                            
                        merge_clip, end_time = self.get_clip_and_end_time(cur_time)
                        if merge_clip != None:
                            self.merge_next_clip(merge_clip, cur_time, end_time)
                            stop_manager = False
                            
                if stop_manager is True:
                    mocap_manager.Stop()
                
                if next_clip_modified is True:
                    next_clip, end_time = self.get_clip_and_end_time(next_clip_begin_time)
                    next_clip.SetTransitionRange(transition_time)
                    RLPy.RGlobal.ObjectModified(avatar, RLPy.EObjectModifiedType_Transform)
                self.set_state(HandRiggerState.Ready)

    def initialize_avatar(self):
        global hand_device
        global avatar

        if hand_device is not None and avatar is not None:
            # avatar's hand setting
            hand_setting = hand_device.GetHandSetting(avatar)

            ##########################################################################################
            hand_setting.SetRightHandJoin(RLPy.EHandJoin_Hand)
            hand_setting.SetLeftHandJoin(RLPy.EHandJoin_Hand)
            # hand_setting.SetRightHandJoin(RLPy.EHandJoin_Wrist)
            # hand_setting.SetLeftHandJoin(RLPy.EHandJoin_Wrist)
            ##########################################################################################

            ##########################################################################################
            hand_setting.SetHandJoinType(RLPy.EHandJoinType_UseParentBone)
            # hand_setting.SetHandJoinType(RLPy.EHandJoinType_UseChildBone)
            ##########################################################################################

            hand_setting.SetRightHandDataSource(RLPy.EHandDataSource_RightHand)
            hand_setting.SetLeftHandDataSource(RLPy.EHandDataSource_RightHand)

            ##########################################################################################
            hand_setting.SetActivePart(RLPy.EBodyActivePart_Finger_R | RLPy.EBodyActivePart_Finger_L)
            # hand_setting.SetActivePart(RLPy.EBodyActivePart_Hand_R | RLPy.EBodyActivePart_Finger_R |
            #                           RLPy.EBodyActivePart_Hand_L | RLPy.EBodyActivePart_Finger_L)
            ##########################################################################################

            if self.join_mode == JoinMode.Left:
                hand_setting.SetRightHandJoin(RLPy.EHandJoin_Invalid)
            elif self.join_mode == JoinMode.Right:
                hand_setting.SetLeftHandJoin(RLPy.EHandJoin_Invalid)

    def process_data(self, start_time):
        global keys
        global hand_device
        global mocap_manager
        global device_data
        global avatar
        global key_weights

        if hand_device.IsTPoseReady(avatar) is False:
            t_pose = BoneData.get_t_pose()
            device_data = copy.deepcopy(t_pose)
            hand_device.SetTPoseData(avatar, t_pose)
        if self.blend_mode == BlendMode.InverseSquareDistance:
            process_data_7keys()
        elif self.blend_mode == BlendMode.NearestTwoKeys:
            process_data_2keys()
        hand_device.ProcessData(0, device_data, start_time)

        return key_weights

    def calculate_weights(self, square_dist):
        global key_weights

        if self.blend_mode == BlendMode.InverseSquareDistance:
            set_weights_7keys(square_dist)
        elif self.blend_mode == BlendMode.NearestTwoKeys:
            set_weights_2keys(square_dist)

        return key_weights

    def mirror_hand_data(self, key_data):
        local_data = world_to_local(key_data)
        for i in range(0, NUM_OF_HAND_BONE):
            local_data[i*7] = -local_data[i*7]
            local_data[i*7+3] = -local_data[i*7+3]
            local_data[i*7+6] = -local_data[i*7+6]
        return local_to_world(local_data)

def process_data_7keys():
    global keys
    global device_data
    global local_data
    global slerped_local
    global slerped_local_11
    global slerped_local_12
    global slerped_local_13
    global slerped_local_21
    global slerped_local_22
    global key_weights

    channel_offset = CHANNELS * HAND_BONE_INDEX_OFFSET
    num_of_hand_bone_channels = CHANNELS * NUM_OF_HAND_BONE

    for i in range(NUM_OF_KEYS):
        if key_weights[i] == 1.0:
            for j in range(num_of_hand_bone_channels):
                device_data[channel_offset+j] = keys[i][j]
            return

    # 1. convert world to local
    # already initialize in HandRigger.run()

    # 2.interpolate 7 keys
    # first pass
    w11 = key_weights[0]+key_weights[1]
    w1 = key_weights[0]/w11
    w2 = key_weights[1]/w11
    interpolate_2keys(slerped_local_11, local_data[0], local_data[1], w1, w2)

    w12 = key_weights[2]+key_weights[3]
    w1 = key_weights[2]/w12
    w2 = key_weights[3]/w12
    interpolate_2keys(slerped_local_12, local_data[2], local_data[3], w1, w2)

    w13 = key_weights[4]+key_weights[5]
    w1 = key_weights[4]/w13
    w2 = key_weights[5]/w13
    interpolate_2keys(slerped_local_13, local_data[4], local_data[5], w1, w2)

    # seconde pass
    w21 = w11 + w12
    w1 = w11/w21
    w2 = w12/w21
    interpolate_2keys(slerped_local_21, slerped_local_11, slerped_local_12, w1, w2)

    w22 = w13 + key_weights[6]
    w1 = w13/w22
    w2 = key_weights[6]/w22
    interpolate_2keys(slerped_local_22, slerped_local_13, local_data[6], w1, w2)

    # third pass (final pass)
    w31 = w21 + w22
    w1 = w21/w31
    w2 = w22/w31
    interpolate_2keys(slerped_local, slerped_local_21, slerped_local_22, w1, w2)

    # 3. convert local to world
    device_data_local_to_world()


def process_data_2keys():
    global keys
    global device_data
    global local_data
    global slerped_local
    global key_weights
    global key_1_index
    global key_2_index
    global w1
    global w2

    channel_offset = CHANNELS * HAND_BONE_INDEX_OFFSET
    num_of_hand_bone_channels = CHANNELS * NUM_OF_HAND_BONE

    for i in range(NUM_OF_KEYS):
        if key_weights[i] == 1.0:  # set gesture to key[i] and return
            for j in range(num_of_hand_bone_channels):
                device_data[channel_offset+j] = keys[i][j]
            return

    # 1. convert world to local
    #local_data_1 = world_to_local(keys[key_1_index])
    #local_data_2 = world_to_local(keys[key_2_index])
    local_data_1 = local_data[key_1_index]
    local_data_2 = local_data[key_2_index]

    # 2. slerp between two keys
    interpolate_2keys(slerped_local, local_data_1, local_data_2, w1, w2)

    # 3. convert local to world
    device_data_local_to_world()


def set_weights_7keys(square_dist):
    global key_weights

    for i in range(NUM_OF_KEYS):
        if square_dist[i] < KEY_DIST_THRESHOLD:  # set gesture to key[i] and return
            key_weights[i] = 1.0
            for j in range(NUM_OF_KEYS):
                if j != i:
                    key_weights[j] = 0.0
            return

    for i in range(NUM_OF_KEYS):
        square_dist[i] = 1/square_dist[i]
    sum = 0
    for i in range(NUM_OF_KEYS):
        sum = sum + square_dist[i]
    for i in range(NUM_OF_KEYS):
        square_dist[i] = square_dist[i]/sum

    key_weights = copy.deepcopy(square_dist)


def set_weights_2keys(square_dist):
    global key_weights
    global key_1_index
    global key_2_index
    global w1
    global w2

    for i in range(NUM_OF_KEYS):
        if square_dist[i] < KEY_DIST_THRESHOLD:  # set gesture to key[i] and return
            key_weights[i] = 1.0
            for j in range(NUM_OF_KEYS):
                if j != i:
                    key_weights[j] = 0.0
            return

    weights = []
    for i in range(NUM_OF_KEYS):
        weights.append([i, square_dist[i]])
    sorted_weights = sorted(weights, key=lambda w: w[1])

    key_1_index = sorted_weights[0][0]
    key_2_index = sorted_weights[1][0]
    key_1_dist = math.sqrt(square_dist[key_1_index])
    key_2_dist = math.sqrt(square_dist[key_2_index])
    dist_sum = key_1_dist + key_2_dist
    w1 = key_2_dist/dist_sum if dist_sum > 0 else key_2_dist
    w2 = key_1_dist/dist_sum if dist_sum > 0 else key_1_dist

    for i in range(NUM_OF_KEYS):
        if i == key_1_index:
            key_weights[i] = w1
        elif i == key_2_index:
            key_weights[i] = w2
        else:
            key_weights[i] = 0.0


def world_to_local(world_data):  # float [NUM_OF_HAND_BONE * CHANNELS]
    global parent_idx

    local_data = []
    local_data.clear()

    # forearm 不計算 local, 只做 euler -> quaternion
    local_data.append(world_data[0])
    local_data.append(world_data[1])
    local_data.append(world_data[2])
    q = e_to_q([world_data[3], world_data[4], world_data[5]])
    local_data.append(q.x)
    local_data.append(q.y)
    local_data.append(q.z)
    local_data.append(q.w)

    for i in range(1, NUM_OF_HAND_BONE):
        i0 = i*6

        # get parent data
        pi = parent_idx[i]  # parent index
        pi0 = pi*6
        parent_p = [world_data[pi0], world_data[pi0+1], world_data[pi0+2]]
        parent_q = e_to_q([world_data[pi0+3], world_data[pi0+4], world_data[pi0+5]])

        # convert to local position
        p = [world_data[i0], world_data[i0+1], world_data[i0+2]]
        p[0] = p[0] - parent_p[0]
        p[1] = p[1] - parent_p[1]
        p[2] = p[2] - parent_p[2]
        local_p = QuaternionQ(p[0], p[1], p[2], 1)

        ###########################################################
        local_p = q_product(q_inverse(parent_q), local_p)
        local_p = q_product(local_p, parent_q)
        #local_p = q_product(parent_q, local_p)
        #local_p = q_product(local_p, q_inverse(parent_q))
        ###########################################################

        # convert to local rotation
        local_q = e_to_q([world_data[i0+3], world_data[i0+4], world_data[i0+5]])

        ###########################################################
        local_q = q_product(q_inverse(parent_q), local_q)
        #local_q = q_product(local_q, q_inverse(parent_q))
        ###########################################################

        # set local data
        local_data.append(local_p.x)
        local_data.append(local_p.y)
        local_data.append(local_p.z)
        local_data.append(local_q.x)
        local_data.append(local_q.y)
        local_data.append(local_q.z)
        local_data.append(local_q.w)

    return local_data


def local_to_world(local_data):
    global parent_idx

    world_data = [None]*NUM_OF_HAND_BONE*6

    world_data[0] = local_data[0]
    world_data[1] = local_data[1]
    world_data[2] = local_data[2]
    q = QuaternionQ(local_data[3], local_data[4], local_data[5], local_data[6])
    euler = q_to_e(q)
    world_data[3] = euler[0]
    world_data[4] = euler[1]
    world_data[5] = euler[2]
    
    world_quaternion = []
    world_quaternion.append(q)

    for i in range(1, NUM_OF_HAND_BONE):
        ldi = i*7  # local-data index
        wdi = i*6  # world-data index
    
        # get parent data
        pi = parent_idx[i]  # parent index
        pldi = pi*7  # parent local-data index
        pwdi = pi*6  # parent world-data index

        parent_world_p = [world_data[pwdi], world_data[pwdi+1], world_data[pwdi+2]]
        parent_world_q = world_quaternion[pi]

        # convert pos to world
        world_p = QuaternionQ(local_data[ldi], local_data[ldi+1], local_data[ldi+2], 1)
        world_p = q_product(parent_world_q, world_p)
        world_p = q_product(world_p, q_inverse(parent_world_q))

        world_data[wdi] = world_p.x + parent_world_p[0]
        world_data[wdi+1] = world_p.y + parent_world_p[1]
        world_data[wdi+2] = world_p.z + parent_world_p[2]

        # convert rot to world
        world_q = QuaternionQ(local_data[ldi+3], local_data[ldi+4], local_data[ldi+5], local_data[ldi+6])

        world_q = q_product(parent_world_q, world_q)

        world_quaternion.append(world_q)
        euler = q_to_e(world_q)
        world_data[wdi+3] = euler[0]
        world_data[wdi+4] = euler[1]
        world_data[wdi+5] = euler[2]

    return world_data


def device_data_local_to_world():
    global device_data
    global slerped_local

    channel_offset = CHANNELS * HAND_BONE_INDEX_OFFSET

    # forearm
    device_data[channel_offset+0] = slerped_local[0]
    device_data[channel_offset+1] = slerped_local[1]
    device_data[channel_offset+2] = slerped_local[2]
    q = QuaternionQ(slerped_local[3], slerped_local[4], slerped_local[5], slerped_local[6])
    euler = q_to_e(q)
    device_data[channel_offset+3] = euler[0]
    device_data[channel_offset+4] = euler[1]
    device_data[channel_offset+5] = euler[2]

    world_quaternion = []
    world_quaternion.append(q)

    for i in range(1, NUM_OF_HAND_BONE):
        ldi = i*7  # local-data index
        wdi = i*6  # world-data index

        # get parent data
        pi = parent_idx[i]  # parent index
        pldi = pi*7  # parent local-data index
        pwdi = pi*6  # parent world-data index

        parent_world_p = [device_data[channel_offset+pwdi], device_data[channel_offset+pwdi+1], device_data[channel_offset+pwdi+2]]
        parent_world_q = world_quaternion[pi]

        # convert pos to world
        world_p = QuaternionQ(slerped_local[ldi], slerped_local[ldi+1], slerped_local[ldi+2], 1)

        ###########################################################
        world_p = q_product(parent_world_q, world_p)
        world_p = q_product(world_p, q_inverse(parent_world_q))
        #world_p = q_product(q_inverse(parent_world_q), world_p)
        #world_p = q_product(world_p, parent_world_q)
        ###########################################################

        device_data[channel_offset+wdi] = world_p.x + parent_world_p[0]
        device_data[channel_offset+wdi+1] = world_p.y + parent_world_p[1]
        device_data[channel_offset+wdi+2] = world_p.z + parent_world_p[2]

        # convert rot to world
        world_q = QuaternionQ(slerped_local[ldi+3], slerped_local[ldi+4], slerped_local[ldi+5], slerped_local[ldi+6])

        ###########################################################
        world_q = q_product(parent_world_q, world_q)
        #world_q = q_product(world_q,parent_world_q)
        ###########################################################

        world_quaternion.append(world_q)
        euler = q_to_e(world_q)
        device_data[channel_offset+wdi+3] = euler[0]
        device_data[channel_offset+wdi+4] = euler[1]
        device_data[channel_offset+wdi+5] = euler[2]


def interpolate_2keys(slerped_local, local_data_1, local_data_2, w1, w2):
    # forearm
    slerped_local[0] = w1*local_data_1[0] + w2*local_data_2[0]
    slerped_local[1] = w1*local_data_1[1] + w2*local_data_2[1]
    slerped_local[2] = w1*local_data_1[2] + w2*local_data_2[2]
    q1 = QuaternionQ(local_data_1[3], local_data_1[4], local_data_1[5], local_data_1[6])
    q2 = QuaternionQ(local_data_2[3], local_data_2[4], local_data_2[5], local_data_2[6])
    result_q = slerp(q1, q2, w2)
    slerped_local[3] = result_q.x
    slerped_local[4] = result_q.y
    slerped_local[5] = result_q.z
    slerped_local[6] = result_q.w

    for i in range(1, NUM_OF_HAND_BONE):
        i0 = i*7
        slerped_local[i0] = w1*local_data_1[i0] + w2*local_data_2[i0]
        slerped_local[i0+1] = w1*local_data_1[i0+1] + w2*local_data_2[i0+1]
        slerped_local[i0+2] = w1*local_data_1[i0+2] + w2*local_data_2[i0+2]
        q1 = QuaternionQ(local_data_1[i0+3], local_data_1[i0+4], local_data_1[i0+5], local_data_1[i0+6])
        q2 = QuaternionQ(local_data_2[i0+3], local_data_2[i0+4], local_data_2[i0+5], local_data_2[i0+6])

        result_q = slerp(q1, q2, w2)

        slerped_local[i0+3] = result_q.x
        slerped_local[i0+4] = result_q.y
        slerped_local[i0+5] = result_q.z
        slerped_local[i0+6] = result_q.w


######################################################################
#    utility functions
######################################################################
def q_product(q1, q2):
    q = QuaternionQ(0, 0, 0, 1)
    q.w = q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z
    q.x = q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y
    q.y = q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x
    q.z = q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w
    return q


def q_conjugate(q):
    p = QuaternionQ(0, 0, 0, 1)
    p.w = q.w
    p.x = -q.x
    p.y = -q.y
    p.z = -q.z
    return p


def q_normalize(q):
    f_norm = q_norm(q)
    q.x = q.x / f_norm
    q.y = q.y / f_norm
    q.z = q.z / f_norm
    q.w = q.w / f_norm
    return q


def q_norm(q):
    return (q.w * q.w) + (q.x * q.x) + (q.y * q.y) + (q.z * q.z)


def q_inverse(q):
    p = q_conjugate(q)
    norm = q_norm(q)
    p.w = p.w/norm
    p.x = p.x/norm
    p.y = p.y/norm
    p.z = p.z/norm
    return p


def e_to_q(e):
    parent_m = RLPy.RMatrix3()
    matrix3_result = parent_m.FromEulerAngle(RLPy.EEulerOrder_XYZ, e[0]*RLPy.RMath.CONST_DEG_TO_RAD, e[1]*RLPy.RMath.CONST_DEG_TO_RAD, e[2]*RLPy.RMath.CONST_DEG_TO_RAD)
    parent_q = RLPy.RQuaternion()
    parent_q.FromRotationMatrix(matrix3_result[0])
    return parent_q


def q_to_e(q):
    abc = RLPy.RQuaternion(RLPy.RVector4(q.x, q.y, q.z, q.w))
    matrix3 = abc.ToRotationMatrix()
    temp_x = 0
    temp_y = 0
    temp_z = 0
    ret = matrix3.ToEulerAngle(RLPy.EEulerOrder_XYZ, temp_x, temp_y, temp_z)
    ret[0] = ret[0]*RLPy.RMath.CONST_RAD_TO_DEG
    ret[1] = ret[1]*RLPy.RMath.CONST_RAD_TO_DEG
    ret[2] = ret[2]*RLPy.RMath.CONST_RAD_TO_DEG
    return ret


def q_dot(q1, q2):
    return (q1.x*q2.x) + (q1.y*q2.y) + (q1.z*q2.z) + (q1.w*q2.w)


def slerp(p, q, w):  # quaternion: p, quaternion: q, weight: w
    #p = q_normalize(p)
    #q = q_normalize(q)

    f_cos = q_dot(p, q)
    f_epsilon = 1.0

    if f_cos < 0.0:
        f_cos = -f_cos
        f_epsilon = -1.0

    f_cos = clamp(f_cos, -1.0, 1.0)
    f_angle = math.acos(f_cos)
    if math.fabs(f_angle) < 1.192092896e-7:
        return p

    f_sin = math.sin(f_angle)
    f_inv_sin = 1.0/f_sin
    coeff_0 = math.sin((1.0-w)*f_angle) * f_inv_sin
    coeff_1 = f_epsilon * math.sin(w*f_angle) * f_inv_sin

    r = QuaternionQ(0, 0, 0, 1)
    r.x = coeff_0*p.x + coeff_1*q.x
    r.y = coeff_0*p.y + coeff_1*q.y
    r.z = coeff_0*p.z + coeff_1*q.z
    r.w = coeff_0*p.w + coeff_1*q.w
    r = q_normalize(r)
    return r


def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value

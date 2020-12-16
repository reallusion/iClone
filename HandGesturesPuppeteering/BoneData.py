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

hips = ["hips", "", "Hips"]
right_up_leg = ["rightupleg", "hips", "RightUpLeg"]
right_leg = ["rightleg", "rightupleg", "RightLeg"]
right_foot = ["rightfoot", "rightleg", "RightFoot"]
left_up_leg = ["leftupleg", "hips", "LeftUpLeg"]
left_leg = ["leftleg", "leftupleg", "LeftLeg"]
left_foot = ["leftfoot", "leftleg", "LeftFoot"]

spine = ["spine", "hips", "Spine"]
spine_1 = ["spine1", "spine", "Spine1"]
spine_2 = ["spine2", "spine1", "Spine2"]
neck = ["neck", "spine2", "Neck"]
head = ["head", "neck", "Head"]

right_shoulder = ["rightshoulder", "spine2", "RightShoulder"]
right_arm = ["rightarm", "rightshoulder", "RightArm"]
right_forearm = ["rightforearm", "rightarm", "RightForeArm"]
right_hand = ["righthand", "rightforearm", "RightHand"]

right_hand_thumb_1 = ["righthandthumb1", "righthand", "RightHandThumb1"]
right_hand_thumb_2 = ["righthandthumb2", "righthandthumb1", "RightHandThumb2"]
right_hand_thumb_3 = ["righthandthumb3", "righthandthumb2", "RightHandThumb3"]
right_hand_index_1 = ["righthandindex1", "righthand", "RightHandIndex1"]
right_hand_index_2 = ["righthandindex2", "righthandindex1", "RightHandIndex2"]
right_hand_index_3 = ["righthandindex3", "righthandindex2", "RightHandIndex3"]
right_hand_middle_1 = ["righthandmiddle1", "righthand", "RightHandMiddle1"]
right_hand_middle_2 = ["righthandmiddle2", "righthandmiddle1", "RightHandMiddle2"]
right_hand_middle_3 = ["righthandmiddle3", "righthandmiddle2", "RightHandMiddle3"]
right_hand_ring_1 = ["righthandring1", "righthand", "RightHandRing1"]
right_hand_ring_2 = ["righthandring2", "righthandring1", "RightHandRing2"]
right_hand_ring_3 = ["righthandring3", "righthandring2", "RightHandRing3"]
right_hand_pinky_1 = ["righthandpinky1", "righthand", "RightHandPinky1"]
right_hand_pinky_2 = ["righthandpinky2", "righthandpinky1", "RightHandPinky2"]
right_hand_pinky_3 = ["righthandpinky3", "righthandpinky2", "RightHandPinky3"]

left_shoulder = ["leftshoulder", "spine2", "LeftShoulder"]
left_arm = ["leftarm", "leftshoulder", "LeftArm"]
left_forearm = ["leftforearm", "leftarm", "LeftForeArm"]
left_hand = ["lefthand", "leftforearm", "LeftHand"]

left_hand_thumb_1 = ["lefthandthumb1", "lefthand", "LeftHandThumb1"]
left_hand_thumb_2 = ["lefthandthumb2", "lefthandthumb1", "LeftHandThumb2"]
left_hand_thumb_3 = ["lefthandthumb3", "lefthandthumb2", "LeftHandThumb3"]
left_hand_index_1 = ["lefthandindex1", "lefthand", "LeftHandIndex1"]
left_hand_index_2 = ["lefthandindex2", "lefthandindex1", "LeftHandIndex2"]
left_hand_index_3 = ["lefthandindex3", "lefthandindex2", "LeftHandIndex3"]
left_hand_middle_1 = ["lefthandmiddle1", "lefthand", "LeftHandMiddle1"]
left_hand_middle_2 = ["lefthandmiddle2", "lefthandmiddle1", "LeftHandMiddle2"]
left_hand_middle_3 = ["lefthandmiddle3", "lefthandmiddle2", "LeftHandMiddle3"]
left_hand_ring_1 = ["lefthandring1", "lefthand", "LeftHandRing1"]
left_hand_ring_2 = ["lefthandring2", "lefthandring1", "LeftHandRing2"]
left_hand_ring_3 = ["lefthandring3", "lefthandring2", "LeftHandRing3"]
left_hand_pinky_1 = ["lefthandpinky1", "lefthand", "LeftHandPinky1"]
left_hand_pinky_2 = ["lefthandpinky2", "lefthandpinky1", "LeftHandPinky2"]
left_hand_pinky_3 = ["lefthandpinky3", "lefthandpinky2", "LeftHandPinky3"]

hik_bone_list = [hips, right_up_leg, right_leg, right_foot, left_up_leg, left_leg, left_foot,
                 spine, spine_1, spine_2, neck, head,
                 right_shoulder, right_arm, right_forearm, right_hand,
                 right_hand_thumb_1,  right_hand_thumb_2,  right_hand_thumb_3,
                 right_hand_index_1,  right_hand_index_2,  right_hand_index_3,
                 right_hand_middle_1, right_hand_middle_2, right_hand_middle_3,
                 right_hand_ring_1,   right_hand_ring_2,   right_hand_ring_3,
                 right_hand_pinky_1,  right_hand_pinky_2,  right_hand_pinky_3,
                 left_shoulder, left_arm, left_forearm, left_hand,
                 left_hand_thumb_1,   left_hand_thumb_2,   left_hand_thumb_3,
                 left_hand_index_1,   left_hand_index_2,   left_hand_index_3,
                 left_hand_middle_1,  left_hand_middle_2,  left_hand_middle_3,
                 left_hand_ring_1,    left_hand_ring_2,    left_hand_ring_3,
                 left_hand_pinky_1,   left_hand_pinky_2,   left_hand_pinky_3]

tpose = [
    # hips      [0]
    0.000002,    1.428000,  94.134850,  89.999992,  -0.000010,     0.000050,                #0
    -8.975920,   3.236325,  89.688179,  -85.930466, 2.130018,     -179.695023,
    -7.370730,   0.203098,  46.964619,  -94.558495, 0.201744,     -179.641296,
    -7.241435,   3.615793,  4.171875,   -89.999886, 0.000044,     179.999481,
    8.976390,    3.236127,  89.688194,  -85.936821, -2.143035,     179.868622,
    7.370685,    0.202775,  46.964073,  -94.566475, -0.207063,     179.571716,
    7.241597,    3.621599,  4.172412,   -90.000053, -0.000018,     179.999466,

    # spine     [7]
    -0.000004,      1.222880,    102.115517,    90.055573,      -0.012245,      -0.021568,  #7
    -0.006609,      1.212970,    110.916939,    93.229034,      -0.051617,      0.133714,
    -0.013967,      0.672969,    120.488174,    85.007523,      -0.042919,      -0.021008,
    -0.030942,      2.741219,    144.163864,    100.007614,     -0.042939,      -0.020896,
    -0.039489,      0.888006,    154.665848,    90.007622,      -0.042685,      -0.021169,
    
    # right_shoulder    [12]
    -2.650147,      3.617706,   142.665100,     17.343395,      -77.938927,     65.909554,  #12
    -16.489246,     5.343336,   143.535507,     0.000283,       -89.481766,     90.708153,
    -41.778629,     5.030622,   143.535477,     90.093842,      -90.000000,     0.000000,   #right forearm  14
    -65.548546,     4.991719,   143.535431,     90.000031,      -90.000000,     0.000000,   #right hand     15
    
    # right fingers
    -67.681900,     2.026569,   142.607071,     -132.789703,    -86.924606,     -105.359779, #16
    -70.881493,     0.042078,   142.458740,     -117.038414,    -85.799629,     -118.572815, #
    -72.973358,     -1.386297,  142.293121,     -128.200302,    -87.162415,     -105.675476, #
    -73.723518,     2.903520,   144.237885,     89.999733,      -90.000000,     0.000000,    #19
    -76.632919,     2.903530,   144.237946,     89.999680,      -90.000000,     0.000000,    #
    -78.851402,     2.903533,   144.237930,     89.999619,      -90.000000,     0.000000,    #
    -73.782135,     4.588821,   144.614563,     89.999733,      -90.000000,     0.000000,    #22
    -77.117043,     4.588847,   144.614258,     89.999733,      -90.000000,     0.000000,    #
    -79.790627,     4.588840,   144.614365,     89.999733,      -90.000000,     0.000000,    #
    -73.451027,     6.148606,   144.327759,     89.999733,      -90.000000,     0.000000,    #25
    -76.517784,     6.148627,   144.327759,     89.999733,      -90.000000,     0.000000,    #
    -79.224548,     6.148638,   144.327759,     89.999733,      -90.000000,     0.000000,    #
    -72.466316,     7.726289,   144.065430,     89.999710,      -90.000000,     0.000000,    #28
    -74.959297,     7.726304,   144.066635,     89.999481,      -90.000000,     0.000000,    #
    -77.075249,     7.726308,   144.066559,     89.999481,      -90.000000,     0.000000,    #30

    # left_shoulder 
    2.648760,       3.615843,    142.664673,    17.663168,      78.032944,      -65.628563,
    16.488592,      5.332074,    143.543777,    -0.000520,      89.705803,      -90.837082,
    41.777058,      4.962777,    143.543793,    90.237167,      90.000000,      0.000000,    #33
    65.546692,      4.864380,    143.543793,    90.000008,      90.000000,      0.000000,    #34

    # left fingers
    67.675560,      1.894048,    142.619843,    -134.998489,    86.958397,      103.021172,  #35
    70.870865,      -0.097905,   142.478500,    -118.504623,    85.860069,      116.977722,  #
    72.959747,      -1.531137,   142.317444,    -130.592682,    87.196709,      103.153023,  #
    73.715630,      2.756808,    144.263519,    89.999680,      90.000000,      0.000000,    #
    76.625046,      2.756813,    144.263550,    89.999359,      90.000000,      0.000000,    #
    78.843529,      2.756832,    144.263565,    89.999290,      90.000000,      0.000000,    #
    73.777397,      4.442260,    144.640228,    89.999680,      90.000000,      0.000000,    #
    77.112259,      4.442276,    144.640015,    89.999680,      90.000000,      0.000000,    #
    79.785873,      4.442264,    144.640091,    89.999680,      90.000000,      0.000000,    #
    73.450546,      6.002759,    144.352631,    89.999680,      90.000000,      0.000000,    #
    76.517303,      6.002785,    144.352631,    89.999680,      90.000000,      0.000000,    #
    79.224045,      6.002799,    144.352646,    89.999680,      90.000000,      0.000000,    #
    72.469963,      7.582942,    144.088181,    89.999680,      90.000000,      0.000000,    #
    74.962944,      7.582955,    144.089432,    89.999695,      90.000000,      0.000000,    #
    77.078911,      7.582951,    144.089386,    89.999718,      90.000000,      0.000000]    # [49]

def get_bone_list():
    global hik_bone_list
    return hik_bone_list

def get_t_pose():
    global tpose
    return tpose

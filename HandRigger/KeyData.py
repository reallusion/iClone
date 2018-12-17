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

NUM_OF_KEYS = 7

key_name = [
    'paper',        #[0]
    'fist',         #[1]
    'good',         #[2]
    'index_finger', #[3]
    'fuck',         #[4]
    'ring_finger',  #[5]
    'pinkie',       #[6]
    'rocker',       #[7]
    'ok',           #[8]
    'gun',          #[9]
    'victory'       #[10]
    ]

key_data = {
    # paper, five_finger, t-pose
    key_name[0] : [               #bone        [index in body] -> [index in hand]
        -74, 160, 0, 0, 0, 0,     #right_hand             [16] -> [0]
        -77, 161, 3, 0, 30, 0,    #right_hand_thumb_1     [17]    [1]
        -81, 161, 3, 0, 0, 0,
        -83, 161, 3, 0, 0, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index    [20]    [4]
        -83, 161, 3, 0, 0, 0,
        -87, 161, 3, 0, 0, 0,
        -89, 161, 3, 0, 0, 0,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle   [24]    [8]
        -83, 161, 1, 0, 0, 0,
        -88, 161, 1, 0, 0, 0,
        -90, 161, 1, 0, 0, 0,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring     [28]    [12]
        -83, 161, -0, 0, 0, 0,
        -86, 161, -0, 0, 0, 0,
        -89, 161, -0, 0, 0, 0,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky    [32]    [16]
        -82, 161, -2, 0, 0, 0,
        -85, 161, -2, 0, 0, 0,
        -87, 161, -2, 0, 0, 0],   #                       [58]    [19]
    # fist, rock
    key_name[1] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 10, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, -50, 0,
        -83, 161, 3, 0, -50, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 80,
        -87, 161, 3, 0, 0, 80,
        -89, 161, 3, 0, 0, 80,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 80,
        -88, 161, 1, 0, 0, 80,
        -90, 161, 1, 0, 0, 80,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,
        -86, 161, -0, 0, 0, 80,
        -89, 161, -0, 0, 0, 80,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 80,
        -85, 161, -2, 0, 0, 80,
        -87, 161, -2, 0, 0, 80,],
    # good, thumb
    key_name[2] : [ 
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 30, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, 0, 0,     
        -83, 161, 3, 0, 0, 0,     
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 80,    
        -87, 161, 3, 0, 0, 80,    
        -89, 161, 3, 0, 0, 80,    
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 80,    
        -88, 161, 1, 0, 0, 80,    
        -90, 161, 1, 0, 0, 80,    
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,   
        -86, 161, -0, 0, 0, 80,   
        -89, 161, -0, 0, 0, 80,   
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 80,
        -85, 161, -2, 0, 0, 80,
        -87, 161, -2, 0, 0, 80,],
    #index_finger
    key_name[3] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 10, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, -50, 0,
        -83, 161, 3, 0, -50, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 0,
        -87, 161, 3, 0, 0, 0,
        -89, 161, 3, 0, 0, 0,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 80,
        -88, 161, 1, 0, 0, 80,
        -90, 161, 1, 0, 0, 80,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,
        -86, 161, -0, 0, 0, 80,
        -89, 161, -0, 0, 0, 80,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 80,
        -85, 161, -2, 0, 0, 80,
        -87, 161, -2, 0, 0, 80,],
    # fuck, middle finger
    key_name[4] : [ 
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 10, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, -50, 0,
        -83, 161, 3, 0, -50, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 80,
        -87, 161, 3, 0, 0, 80,
        -89, 161, 3, 0, 0, 80,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 0,
        -88, 161, 1, 0, 0, 0,
        -90, 161, 1, 0, 0, 0,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,
        -86, 161, -0, 0, 0, 80,
        -89, 161, -0, 0, 0, 80,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 80,
        -85, 161, -2, 0, 0, 80,
        -87, 161, -2, 0, 0, 80,],
    # ring_finger
    key_name[5] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 10, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, -50, 0,
        -83, 161, 3, 0, -50, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 80,
        -87, 161, 3, 0, 0, 80,
        -89, 161, 3, 0, 0, 80,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 80,
        -88, 161, 1, 0, 0, 80,
        -90, 161, 1, 0, 0, 80,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 0,
        -86, 161, -0, 0, 0, 0,
        -89, 161, -0, 0, 0, 0,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 80,
        -85, 161, -2, 0, 0, 80,
        -87, 161, -2, 0, 0, 80,],
    # pinkie, little finger
    key_name[6] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 10, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, -50, 0,
        -83, 161, 3, 0, -50, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 80,
        -87, 161, 3, 0, 0, 80,
        -89, 161, 3, 0, 0, 80,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 80,
        -88, 161, 1, 0, 0, 80,
        -90, 161, 1, 0, 0, 80,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,
        -86, 161, -0, 0, 0, 80,
        -89, 161, -0, 0, 0, 80,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 0,
        -85, 161, -2, 0, 0, 0,
        -87, 161, -2, 0, 0, 0,],
    # rocker
    key_name[7] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 30, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, 0, 0,
        -83, 161, 3, 0, 0, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 0,
        -87, 161, 3, 0, 0, 0,
        -89, 161, 3, 0, 0, 0,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 80,
        -88, 161, 1, 0, 0, 80,
        -90, 161, 1, 0, 0, 80,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,
        -86, 161, -0, 0, 0, 80,
        -89, 161, -0, 0, 0, 80,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 0,
        -85, 161, -2, 0, 0, 0,
        -87, 161, -2, 0, 0, 0,],
    # ok
    key_name[8] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 25, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, -25, 0,
        -83, 161, 3, 0, -35, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 40,
        -87, 161, 3, 0, 0, 65,
        -89, 161, 3, 0, 0, 65,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 0,
        -88, 161, 1, 0, 0, 0,
        -90, 161, 1, 0, 0, 0,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 0,
        -86, 161, -0, 0, 0, 0,
        -89, 161, -0, 0, 0, 0,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 0,
        -85, 161, -2, 0, 0, 0,
        -87, 161, -2, 0, 0, 0,],
    # gun
    key_name[9] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 30, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, 0, 0,
        -83, 161, 3, 0, 0, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0, 0, 0,
        -87, 161, 3, 0, 0, 0,
        -89, 161, 3, 0, 0, 0,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 80,
        -88, 161, 1, 0, 0, 80,
        -90, 161, 1, 0, 0, 80,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,
        -86, 161, -0, 0, 0, 80,
        -89, 161, -0, 0, 0, 80,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 80,
        -85, 161, -2, 0, 0, 80,
        -87, 161, -2, 0, 0, 80,],
    # victory
    key_name[10] : [
        -74, 160, 0, 0, 0, 0,     #right_hand
        -77, 161, 3, 0, 10, 0,    #right_hand_thumb_1
        -81, 161, 3, 0, -50, 0,
        -83, 161, 3, 0, -50, 0,
        -78, 161, 2, 0, 0, 0,     #right_in_hand_index
        -83, 161, 3, 0,15, 0,
        -87, 161, 3, 0, 0, 0,
        -89, 161, 3, 0, 0, 0,
        -78, 161, 0, 0, 0, 0,     #right_in_hand_middle
        -83, 161, 1, 0, 0, 0,
        -88, 161, 1, 0, 0, 0,
        -90, 161, 1, 0, 0, 0,
        -78, 161, -0, 0, 0, 0,    #right_in_hand_ring
        -83, 161, -0, 0, 0, 80,
        -86, 161, -0, 0, 0, 80,
        -89, 161, -0, 0, 0, 80,
        -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky
        -82, 161, -2, 0, 0, 80,
        -85, 161, -2, 0, 0, 80,
        -87, 161, -2, 0, 0, 80,]
}

class Keys(object):
    def __init__(self):
        global key_data
        self.key_name_list = [ #7 keys
           'paper',
           'gun',
           'victory',
           'rocker',
           'index_finger',
           'fist',
           'good', 
           ]

    def set_key(self, key_index, key):
        self.key_name_list[key_index] = key
        
    def get_data(self):
        global key_data
        data = []
        for i in range(NUM_OF_KEYS):
            data.append(key_data[self.key_name_list[i]])
        return data

hips = ["hips", "", "Hips"]
right_up_leg = ["rightupleg", "hips", "RightUpLeg"]
right_leg = ["rightleg", "rightupleg", "RightLeg"]
right_foot = ["rightfoot", "rightleg", "RightFoot"]
left_up_leg = ["leftupleg", "hips", "LeftUpLeg"]
left_leg = ["leftleg", "leftupleg", "LeftLeg"]
left_foot = ["leftfoot", "leftleg", "LeftFoot"]
spine = ["spine", "hips", "Spine"]
spine_1 = ["spine1", "spine", "Spine3"]
spine_2 = ["spine2", "spine1", "Spine6"]
spine_3 = ["spine3", "spine2", "Spine9"]
neck = ["neck", "spine3", "Neck"]
head = ["head", "neck", "Head"]
right_shoulder = ["rightshoulder", "spine3", "RightShoulder"]
right_arm = ["rightarm", "rightshoulder", "RightArm"]
right_forearm = ["rightforearm", "rightarm", "RightForeArm"]
right_hand = ["righthand", "rightforearm", "RightHand"]
right_hand_thumb_1 = ["righthandthumb1", "righthand", "RightHandThumb1"]
right_hand_thumb_2 = ["righthandthumb2", "righthandthumb1", "RightHandThumb2"]
right_hand_thumb_3 = ["righthandthumb3", "righthandthumb2", "RightHandThumb3"]
right_in_hand_index = ["rightinhandindex", "righthand", "RightInHandIndex"]
right_hand_index_1 = ["righthandindex1", "rightinhandindex", "RightHandIndex1"]
right_hand_index_2 = ["righthandindex2", "righthandindex1", "RightHandIndex2"]
right_hand_index_3 = ["righthandindex3", "righthandindex2", "RightHandIndex3"]
right_in_hand_middle = ["rightinhandmiddle", "righthand", "RightInHandMiddle"]
right_hand_middle_1 = ["righthandmiddle1", "rightinhandmiddle", "RightHandMiddle1"]
right_hand_middle_2 = ["righthandmiddle2", "righthandmiddle1", "RightHandMiddle2"]
right_hand_middle_3 = ["righthandmiddle3", "righthandmiddle2", "RightHandMiddle3"]
right_in_hand_ring = ["rightinhandring", "righthand", "RightInHandRing"]
right_hand_ring_1 = ["righthandring1", "rightinhandring", "RightHandRing1"]
right_hand_ring_2 = ["righthandring2", "righthandring1", "RightHandRing2"]
right_hand_ring_3 = ["righthandring3", "righthandring2", "RightHandRing3"]
right_in_hand_pinky = ["rightinhandpinky", "righthand", "RightInHandPinky"]
right_hand_pinky_1 = ["righthandpinky1", "rightinhandpinky", "RightHandPinky1"]
right_hand_pinky_2 = ["righthandpinky2", "righthandpinky1", "RightHandPinky2"]
right_hand_pinky_3 = ["righthandpinky3", "righthandpinky2", "RightHandPinky3"]
left_shoulder = ["leftshoulder", "spine3", "LeftShoulder"]
left_arm = ["leftarm", "leftshoulder", "LeftArm"]
left_forearm = ["leftforearm", "leftarm", "LeftForeArm"]
left_hand = ["lefthand", "leftforearm", "LeftHand"]
left_hand_thumb_1 = ["lefthandthumb1", "lefthand", "LeftHandThumb1"]
left_hand_thumb_2 = ["lefthandthumb2", "lefthandthumb1", "LeftHandThumb2"]
left_hand_thumb_3 = ["lefthandthumb3", "lefthandthumb2", "LeftHandThumb3"]
left_in_hand_index = ["leftinhandindex", "lefthand", "LeftInHandIndex"]
left_hand_index_1 = ["lefthandindex1", "leftinhandindex", "LeftHandIndex1"]
left_hand_index_2 = ["lefthandindex2", "lefthandindex1", "LeftHandIndex2"]
left_hand_index_3 = ["lefthandindex3", "lefthandindex2", "LeftHandIndex3"]
left_in_hand_middle = ["leftinhandmiddle", "lefthand", "LeftInHandMiddle"]
left_hand_middle_1 = ["lefthandmiddle1", "leftinhandmiddle", "LeftHandMiddle1"]
left_hand_middle_2 = ["lefthandmiddle2", "lefthandmiddle1", "LeftHandMiddle2"]
left_hand_middle_3 = ["lefthandmiddle3", "lefthandmiddle2", "LeftHandMiddle3"]
left_in_hand_ring = ["leftinhandring", "lefthand", "LeftInHandRing"]
left_hand_ring_1 = ["lefthandring1", "leftinhandring", "LeftHandRing1"]
left_hand_ring_2 = ["lefthandring2", "lefthandring1", "LeftHandRing2"]
left_hand_ring_3 = ["lefthandring3", "lefthandring2", "LeftHandRing3"]
left_hand_pinky = ["leftinhandpinky", "lefthand", "LeftInHandPinky"]
left_hand_pinky_1 = ["lefthandpinky1", "leftinhandpinky", "LeftHandPinky1"]
left_hand_pinky_2 = ["lefthandpinky2", "lefthandpinky1", "LeftHandPinky2"]
left_hand_pinky_3 = ["lefthandpinky3", "lefthandpinky2", "LeftHandPinky3"]

hik_bone_list = [hips, right_up_leg, right_leg, right_foot, left_up_leg, left_leg, left_foot,
                 spine, spine_1, spine_2, spine_3, neck, head,
                 right_shoulder, right_arm, right_forearm, right_hand,
                 right_hand_thumb_1, right_hand_thumb_2, right_hand_thumb_3,
                 right_in_hand_index, right_hand_index_1, right_hand_index_2, right_hand_index_3,
                 right_in_hand_middle, right_hand_middle_1, right_hand_middle_2, right_hand_middle_3,
                 right_in_hand_ring, right_hand_ring_1, right_hand_ring_2, right_hand_ring_3,
                 right_in_hand_pinky, right_hand_pinky_1, right_hand_pinky_2, right_hand_pinky_3,
                 left_shoulder, left_arm, left_forearm, left_hand,
                 left_hand_thumb_1, left_hand_thumb_2, left_hand_thumb_3,
                 left_in_hand_index, left_hand_index_1, left_hand_index_2, left_hand_index_3,
                 left_in_hand_middle, left_hand_middle_1, left_hand_middle_2, left_hand_middle_3,
                 left_in_hand_ring, left_hand_ring_1, left_hand_ring_2, left_hand_ring_3,
                 left_hand_pinky, left_hand_pinky_1, left_hand_pinky_2, left_hand_pinky_3]

tpose = [
          0, 105, 0, 0, 0, 0,       #hips                   [0]
          -11, 105, 0, 0, 0, 0,
          -11, 56, 0, 0, 0, 0,
          -11, 8, 0, 0, 0, 0,
          11, 105, 0, 0, 0, 0,
          11, 56, 0, 0, 0, 0,
          11, 8, 0, 0, 0, 0.0,
          0, 118, 0, 0, 0, 0,       #spine                  [7]
          0, 129, 0, 0, 0, 0,
          0, 141, 0, 0, 0, 0,
          0, 152, 0, 0, 0, 0,
          0, 164, 0, 0, 0, 0,
          0, 173, 0, 0, 0, 0,
          -3, 160, 0, 0, 0, 0,      #right_shoulder         [13]
          -17, 160, 0, 0, 0, 0,
          -46, 160, 0, 0, 0, 0,
          -74, 160, 0, 0, 0, 0,     #right_hand             [16]

          -77, 161, 3, 0, 30, 0,    #right_hand_thumb_1     [17]
          -81, 161, 3, 0, 0, 0,
          -83, 161, 3, 0, 0, 0,
          -78, 161, 2, 0, 0, 0,     #right_in_hand_index    [20]
          -83, 161, 3, 0, 0, 0,
          -87, 161, 3, 0, 0, 0,
          -89, 161, 3, 0, 0, 0,
          -78, 161, 0, 0, 0, 0,     #right_in_hand_middle   [24]
          -83, 161, 1, 0, 0, 0,
          -88, 161, 1, 0, 0, 0,
          -90, 161, 1, 0, 0, 0,
          -78, 161, -0, 0, 0, 0,    #right_in_hand_ring     [28]
          -83, 161, -0, 0, 0, 0,
          -86, 161, -0, 0, 0, 0,
          -89, 161, -0, 0, 0, 0,
          -77, 161, -1, 0, 0, 0,    #right_in_hand_pinky    [32]
          -82, 161, -2, 0, 0, 0,
          -85, 161, -2, 0, 0, 0,
          -87, 161, -2, 0, 0, 0,

          3, 160, 0, 0, 0, 0,       #left_shoulder          [36]
          17, 160, 0, 0, 0, 0,
          46, 160, 0, 0, 0, 0,
          74, 160, 0, 0, 0, 0,      #left_hand              [39]

          77, 161, 3, 0, -30, 0,    #left_hand_thumb_1      [40]
          81, 161, 3, 0, 0, 0,
          83, 161, 3, 0, 0, 0,
          78, 161, 2, 0, 0, 0,
          83, 161, 3, 0, 0, 0,
          87, 161, 3, 0, 0, 0,
          89, 161, 3, 0, 0, 0,
          78, 161, 0, 0, 0, 0,
          83, 161, 1, 0, 0, 0,
          88, 161, 1, 0, 0, 0,
          90, 161, 1, 0, 0, 0,
          78, 161, 0, 0, 0, 0,
          83, 161, 0, 0, 0, 0,
          86, 161, 0, 0, 0, 0,
          89, 161, 0, 0, 0, 0,
          77, 161, -1, 0, 0, 0,
          82, 161, -2, 0, 0, 0,
          85, 161, -2, 0, 0, 0,
          87, 161, -2, 0, 0, 0]     #                       [58]

def get_bone_list():
    global hik_bone_list
    return hik_bone_list

def get_t_pose():
    global tpose
    return tpose
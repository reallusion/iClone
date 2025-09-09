import os
import socket
import time
from socketserver import BaseRequestHandler, TCPServer

HOST = '0.0.0.0'
PORT = 999
send_data = []
add_value = 5
max_value = 100

avatar_exp_name = []
avatar_exp_change_idx = []
avatar_exp_change_name = ['Brow_Raise', 'Mouth_Smile']

#IC7 Standard (143)
# exp_ic7_stardard = ['Brow_Raise_Inner_Left', 'Brow_Raise_Inner_Right', 'Brow_Raise_Outer_Left', 'Brow_Raise_Outer_Right', 'Brow_Drop_Left', 'Brow_Drop_Right', 'Brow_Raise_Left', 'Brow_Raise_Right', 'Eyes_Blink', 'Eye_Blink_L', 'Eye_Blink_R', 'Eye_Wide_L', 'Eye_Wide_R', 'Eye_Squint_L', 'Eye_Squint_R', 'Nose_Scrunch', 'Nose_Flanks_Raise', 'Nose_Flank_Raise_L', 'Nose_Flank_Raise_R', 'Nose_Nostrils_Flare', 'Cheek_Raise_L', 'Cheek_Raise_R', 'Cheeks_Suck', 'Cheek_Blow_L', 'Cheek_Blow_R', 'Mouth_Smile', 'Mouth_Smile_L', 'Mouth_Smile_R', 'Mouth_Frown', 'Mouth_Frown_L', 'Mouth_Frown_R', 'Mouth_Blow', 'Mouth_Pucker', 'Mouth_Pucker_Open', 'Mouth_Widen', 'Mouth_Widen_Sides', 'Mouth_Dimple_L', 'Mouth_Dimple_R', 'Mouth_Plosive', 'Mouth_Lips_Tight', 'Mouth_Lips_Tuck', 'Mouth_Lips_Open', 'Mouth_Lips_Part', 'Mouth_Bottom_Lip_Down', 'Mouth_Top_Lip_Up', 'Mouth_Top_Lip_Under', 'Mouth_Bottom_Lip_Under', 'Mouth_Snarl_Upper_L', 'Mouth_Snarl_Upper_R', 'Mouth_Snarl_Lower_L', 'Mouth_Snarl_Lower_R', 'Mouth_Bottom_Lip_Bite', 'Mouth_Down', 'Mouth_Up', 'Mouth_L', 'Mouth_R', 'Mouth_Lips_Jaw_Adjust', 'Mouth_Bottom_Lip_Trans', 'Mouth_Skewer', 'Mouth_Open', 'Head_Turn_Up', 'Head_Turn_Down', 'Head_Turn_L', 'Head_Turn_R', 'Head_Tilt_L', 'Head_Tilt_R', 'Turn_Jaw_Down', 'Turn_Jaw_L', 'Turn_Jaw_R', 'Move_Jaw_Down', 'Move_Jaw_L', 'Move_Jaw_R', 'Left_Eyeball_Look_R', 'Left_Eyeball_Look_L', 'Left_Eyeball_Look_Down', 'Left_Eyeball_Look_Up', 'Right_Eyeball_Look_R', 'Right_Eyeball_Look_L', 'Right_Eyeball_Look_Down', 'Right_Eyeball_Look_Up', 'A01_Brow_Inner_Up', 'A02_Brow_Down_Left', 'A03_Brow_Down_Right', 'A04_Brow_Outer_Up_Left', 'A05_Brow_Outer_Up_Right', 'A06_Eye_Look_Up_Left', 'A07_Eye_Look_Up_Right', 'A08_Eye_Look_Down_Left', 'A09_Eye_Look_Down_Right', 'A10_Eye_Look_Out_Left', 'A11_Eye_Look_In_Left', 'A12_Eye_Look_In_Right', 'A13_Eye_Look_Out_Right', 'A14_Eye_Blink_Left', 'A15_Eye_Blink_Right', 'A16_Eye_Squint_Left', 'A17_Eye_Squint_Right', 'A18_Eye_Wide_Left', 'A19_Eye_Wide_Right', 'A20_Cheek_Puff', 'A21_Cheek_Squint_Left', 'A22_Cheek_Squint_Right', 'A23_Nose_Sneer_Left', 'A24_Nose_Sneer_Right', 'A25_Jaw_Open', 'A26_Jaw_Forward', 'A27_Jaw_Left', 'A28_Jaw_Right', 'A29_Mouth_Funnel', 'A30_Mouth_Pucker', 'A31_Mouth_Left', 'A32_Mouth_Right', 'A33_Mouth_Roll_Upper', 'A34_Mouth_Roll_Lower', 'A35_Mouth_Shrug_Upper', 'A36_Mouth_Shrug_Lower', 'A37_Mouth_Close', 'A38_Mouth_Smile_Left', 'A39_Mouth_Smile_Right', 'A40_Mouth_Frown_Left', 'A41_Mouth_Frown_Right', 'A42_Mouth_Dimple_Left', 'A43_Mouth_Dimple_Right', 'A44_Mouth_Upper_Up_Left', 'A45_Mouth_Upper_Up_Right', 'A46_Mouth_Lower_Down_Left', 'A47_Mouth_Lower_Down_Right', 'A48_Mouth_Press_Left', 'A49_Mouth_Press_Right', 'A50_Mouth_Stretch_Left', 'A51_Mouth_Stretch_Right', 'A52_Tongue_Out', 'T01_Tongue_Up', 'T02_Tongue_Down', 'T03_Tongue_Left', 'T04_Tongue_Right', 'T05_Tongue_Roll', 'T06_Tongue_Tip_Up', 'T07_Tongue_Tip_Down', 'T08_Tongue_Width', 'T09_Tongue_Thickness', 'T10_Tongue_Bulge_Left', 'T11_Tongue_Bulge_Right']
#CC4 Extended (300)
# exp_cc4_extended = ['Brow_Raise_Inner_L', 'Brow_Raise_Inner_R', 'Brow_Raise_Outer_L', 'Brow_Raise_Outer_R', 'Brow_Drop_L', 'Brow_Drop_R', 'Brow_Compress_L', 'Brow_Compress_R', 'Eye_Blink_L', 'Eye_Blink_R', 'Nose_Sneer_L', 'Nose_Sneer_R', 'Nose_Nostril_Raise_L', 'Nose_Nostril_Raise_R', 'Nose_Nostril_Dilate_L', 'Nose_Nostril_Dilate_R', 'Nose_Crease_L', 'Nose_Crease_R', 'Nose_Nostril_Down_L', 'Nose_Nostril_Down_R', 'Nose_Nostril_In_L', 'Nose_Nostril_In_R', 'Nose_Tip_L', 'Nose_Tip_R', 'Nose_Tip_Up', 'Nose_Tip_Down', 'Cheek_Raise_L', 'Cheek_Raise_R', 'Cheek_Suck_L', 'Cheek_Suck_R', 'Cheek_Puff_L', 'Cheek_Puff_R', 'Neck_Swallow_Up', 'Neck_Swallow_Down', 'Neck_Tighten_L', 'Neck_Tighten_R', 'Head_Turn_Up', 'Head_Turn_Down', 'Head_Turn_L', 'Head_Turn_R', 'Head_Tilt_L', 'Head_Tilt_R', 'Head_L', 'Head_R', 'Head_Forward', 'Head_Backward', 'Jaw_Open', 'Jaw_Forward', 'Jaw_Backward', 'Jaw_L', 'Jaw_R', 'Jaw_Up', 'Jaw_Down', 'Eyelash_Upper_Up_L', 'Eyelash_Upper_Down_L', 'Eyelash_Upper_Up_R', 'Eyeleash_Upper_Down_R', 'Eyelash_Lower_Up_L', 'Eyelash_Lower_Down_L', 'Eyelash_Lower_Up_R', 'Eyelash_Lower_Down_R', 'Tongue_Out', 'Tongue_In', 'Tongue_Up', 'Tongue_Down', 'Tongue_Mid_Up', 'Tongue_Tip_Up', 'Tongue_Tip_Down', 'Tongue_Narrow', 'Tongue_Wide', 'Tongue_Roll', 'Tongue_L', 'Tongue_R', 'Tongue_Tip_L', 'Tongue_Tip_R', 'Tongue_Twist_L', 'Tongue_Twist_R', 'Tongue_Bulge_L', 'Tongue_Bulge_R', 'Tongue_Extend', 'Tongue_Enlarge', 'Eye_Close_L', 'Eye_Close_R', 'Eye_Squint_L', 'Eye_Squint_R', 'Eye_Wide_L', 'Eye_Wide_R', 'Eye_L_Look_L', 'Eye_R_Look_L', 'Eye_L_Look_R', 'Eye_R_Look_R', 'Eye_L_Look_Up', 'Eye_R_Look_Up', 'Eye_L_Look_Down', 'Eye_R_Look_Down', 'Eye_Pupil_Dilate', 'Eye_Pupil_Contract', 'Ear_Up_L', 'Ear_Up_R', 'Ear_Down_L', 'Ear_Down_R', 'Ear_Out_L', 'Ear_Out_R', 'Mouth_Smile_L', 'Mouth_Smile_R', 'Mouth_Smile_Sharp_L', 'Mouth_Smile_Sharp_R', 'Mouth_Frown_L', 'Mouth_Frown_R', 'Mouth_Stretch_L', 'Mouth_Stretch_R', 'Mouth_Dimple_L', 'Mouth_Dimple_R', 'Mouth_Press_L', 'Mouth_Press_R', 'Mouth_Tighten_L', 'Mouth_Tighten_R', 'Mouth_Blow_L', 'Mouth_Blow_R', 'Mouth_Pucker_Up_L', 'Mouth_Pucker_Up_R', 'Mouth_Pucker_Down_L', 'Mouth_Pucker_Down_R', 'Mouth_Funnel_Up_L', 'Mouth_Funnel_Up_R', 'Mouth_Funnel_Down_L', 'Mouth_Funnel_Down_R', 'Mouth_Roll_In_Upper_L', 'Mouth_Roll_In_Upper_R', 'Mouth_Roll_In_Lower_L', 'Mouth_Roll_In_Lower_R', 'Mouth_Roll_Out_Upper_L', 'Mouth_Roll_Out_Upper_R', 'Mouth_Roll_Out_Lower_L', 'Mouth_Roll_Out_Lower_R', 'Mouth_Push_Upper_L', 'Mouth_Push_Upper_R', 'Mouth_Push_Lower_L', 'Mouth_Push_Lower_R', 'Mouth_Pull_Upper_L', 'Mouth_Pull_Upper_R', 'Mouth_Pull_Lower_L', 'Mouth_Pull_Lower_R', 'Mouth_Up', 'Mouth_Down', 'Mouth_L', 'Mouth_R', 'Mouth_Upper_L', 'Mouth_Upper_R', 'Mouth_Lower_L', 'Mouth_Lower_R', 'Mouth_Shrug_Upper', 'Mouth_Shrug_Lower', 'Mouth_Drop_Upper', 'Mouth_Drop_Lower', 'Mouth_Up_Upper_L', 'Mouth_Up_Upper_R', 'Mouth_Down_Lower_L', 'Mouth_Down_Lower_R', 'Mouth_Chin_Up', 'Mouth_Close', 'Mouth_Contract', '0311_01', '0311_02', 'open_01', 'Explosive_01', 'dental_up_01', 'tight_O_01', 'tight_01', 'wide_01', 'Affricate_01', 'Lips_open_01', 'tongue_up_01', 'tongue_out_01', 'tongue_narrow_01', 'tongue_lower_01', 'tongue_curl_U_01', 'tongue_curl_D_01', 'tongue_raise_01', 'blendShape10.CC_Base_Body_145ShapeShape', 'blendShape10.CC_Base_Body_146ShapeShape', 'blendShape10.CC_Base_Body_147ShapeShape', 'blendShape10.CC_Base_Body_148ShapeShape', 'blendShape10.CC_Base_Body_149ShapeShape', 'blendShape10.CC_Base_Body_150ShapeShape', 'blendShape10.CC_Base_Body_151ShapeShape', 'blendShape10.CC_Base_Body_152ShapeShape', 'blendShape10.CC_Base_Body_153ShapeShape', 'blendShape10.CC_Base_Body_154ShapeShape', 'blendShape10.CC_Base_Body_155ShapeShape', 'blendShape10.CC_Base_Body_156ShapeShape', 'blendShape10.CC_Base_Body_157ShapeShape', 'blendShape10.CC_Base_Body_158ShapeShape', 'blendShape10.CC_Base_Body_159ShapeShape', 'blendShape10.CC_Base_Body_160ShapeShape', 'blendShape10.CC_Base_Body_161ShapeShape', 'blendShape10.CC_Base_Body_162ShapeShape', 'blendShape10.CC_Base_Body_163ShapeShape', 'blendShape10.CC_Base_Body_164ShapeShape', 'blendShape10.CC_Base_Body_165ShapeShape', 'blendShape10.CC_Base_Body_166ShapeShape', 'blendShape10.CC_Base_Body_167ShapeShape', 'blendShape10.CC_Base_Body_168ShapeShape', 'blendShape10.CC_Base_Body_169ShapeShape', 'blendShape10.CC_Base_Body_170ShapeShape', 'blendShape10.CC_Base_Body_171ShapeShape', 'blendShape10.CC_Base_Body_172ShapeShape', 'blendShape10.CC_Base_Body_173ShapeShape', 'blendShape10.CC_Base_Body_174ShapeShape', 'blendShape10.CC_Base_Body_175ShapeShape', 'blendShape10.CC_Base_Body_176ShapeShape', 'blendShape10.CC_Base_Body_178ShapeShape', 'blendShape10.CC_Base_Body_179ShapeShape', 'blendShape10.CC_Base_Body_180ShapeShape', 'blendShape10.CC_Base_Body_181ShapeShape', 'blendShape10.CC_Base_Body_182ShapeShape', 'blendShape10.CC_Base_Body_183ShapeShape', 'blendShape10.CC_Base_Body_184ShapeShape', 'blendShape10.CC_Base_Body_185ShapeShape', 'blendShape10.CC_Base_Body_186ShapeShape', 'blendShape10.CC_Base_Body_187ShapeShape', 'blendShape10.CC_Base_Body_188ShapeShape', 'blendShape10.CC_Base_Body_189ShapeShape', 'blendShape10.CC_Base_Body_190ShapeShape', 'blendShape10.CC_Base_Body_191ShapeShape', 'blendShape10.CC_Base_Body_192ShapeShape', 'blendShape10.CC_Base_Body_193ShapeShape', 'blendShape10.CC_Base_Body_194ShapeShape', 'blendShape10.CC_Base_Body_195ShapeShape', 'blendShape10.CC_Base_Body_196ShapeShape', 'blendShape10.CC_Base_Body_197ShapeShape', 'blendShape10.CC_Base_Body_198ShapeShape', 'blendShape10.CC_Base_Body_199ShapeShape', 'blendShape10.CC_Base_Body_200ShapeShape', 'blendShape10.CC_Base_Body_201ShapeShape', 'blendShape10.CC_Base_Body_202ShapeShape', 'blendShape10.CC_Base_Body_203ShapeShape', 'blendShape10.CC_Base_Body_204ShapeShape', 'blendShape10.CC_Base_Body_205ShapeShape', 'blendShape10.CC_Base_Body_206ShapeShape', 'blendShape10.CC_Base_Body_208ShapeShape', 'blendShape10.CC_Base_Body_209ShapeShape', 'blendShape10.CC_Base_Body_210ShapeShape', 'blendShape1.CC_Base_Body26ShapeShape', 'blendShape1.CC_Base_Body25ShapeShape', 'blendShape1.CC_Base_Body28ShapeShape', 'blendShape1.CC_Base_Body27ShapeShape', 'blendShape1.CC_Base_Body32ShapeShape', 'blendShape1.CC_Base_Body31ShapeShape', 'blendShape1.CC_Base_Body30ShapeShape', 'blendShape1.CC_Base_Body30Shape_CopyShape', 'blendShape11.CC_Base_Body_216ShapeShape', 'blendShape11.CC_Base_Body_215ShapeShape', 'blendShape11.CC_Base_Body_214ShapeShape', 'blendShape11.CC_Base_Body_213ShapeShape', 'blendShape11.CC_Base_Body_212ShapeShape', 'blendShape11.CC_Base_Body_211ShapeShape', 'blendShape11.CC_Base_Body_218ShapeShape', 'blendShape11.CC_Base_Body_217ShapeShape', 'blendShape11.CC_Base_Body_212Shape_0Shape', 'blendShape11.CC_Base_Body_211Shape_0Shape', 'blendShape11.CC_Base_Body_212Shape_1Shape', 'blendShape11.CC_Base_Body_211Shape_1Shape', 'blendShape11.CC_Base_Body_214Shape_0Shape', 'blendShape11.CC_Base_Body_213Shape_0Shape', 'blendShape11.CC_Base_Body_212Shape_2Shape', 'blendShape11.CC_Base_Body_211Shape_2Shape', 'blendShape11.CC_Base_Body_214Shape_1Shape', 'blendShape11.CC_Base_Body_213Shape_1Shape', 'blendShape11.CC_Base_Body_216Shape_0Shape', 'blendShape11.CC_Base_Body_215Shape_0Shape', 'look_up_M', 'look_down_M', 'jaw_open_test_01', 'roll_in_test_01', 'lips_open_test_01', 'eye_shape_L', 'eye_shape_R', 'eye_shape_angry_L', 'eye_shape_angry_R', 'double_eyelid_up_L', 'double_eyelid_up_R', 'up', 'down', '0317_01', 'EE_01', 'Er_01', 'IH_01', 'Ah_01', 'Oh_01', 'W_OO_01', 'S_Z_01', 'Ch_J_01', 'F_V_01', 'TH_01', 'T_L_D_N_01', 'B_M_P_01', 'K_G_H_NG_01', 'AE_01', 'R_01']
#CC4 Standard(75)
# exp_cc4_standard = ['Brow_Raise_Inner_L', 'Brow_Raise_Inner_R', 'Brow_Raise_Outer_L', 'Brow_Raise_Outer_R', 'Brow_Drop_L', 'Brow_Drop_R', 'Eye_Blink_L', 'Eye_Blink_R', 'Eye_Squint_L', 'Eye_Squint_R', 'Eye_Wide_L', 'Eye_Wide_R', 'Eye_L_Look_L', 'Eye_R_Look_L', 'Eye_L_Look_R', 'Eye_R_Look_R', 'Eye_L_Look_Up', 'Eye_R_Look_Up', 'Eye_L_Look_Down', 'Eye_R_Look_Down', 'Nose_Sneer_L', 'Nose_Sneer_R', 'Cheek_Raise_L', 'Cheek_Raise_R', 'Cheek_Puff_L', 'Cheek_Puff_R', 'Mouth_Smile_L', 'Mouth_Smile_R', 'Mouth_Frown_L', 'Mouth_Frown_R', 'Mouth_Stretch_L', 'Mouth_Stretch_R', 'Mouth_Dimple_L', 'Mouth_Dimple_R', 'Mouth_Press_L', 'Mouth_Press_R', 'Mouth_Pucker', 'Mouth_Funnel', 'Mouth_Roll_In_Upper', 'Mouth_Roll_In_Lower', 'Mouth_L', 'Mouth_R', 'Mouth_Shrug_Upper', 'Mouth_Shrug_Lower', 'Mouth_Up_Upper_L', 'Mouth_Up_Upper_R', 'Mouth_Down_Lower_L', 'Mouth_Down_Lower_R', 'Mouth_Close', 'Tongue_Out', 'Tongue_Up', 'Tongue_Down', 'Tongue_Tip_Up', 'Tongue_Tip_Down', 'Tongue_Narrow', 'Tongue_Wide', 'Tongue_Roll', 'Tongue_L', 'Tongue_R', 'Tongue_Bulge_L', 'Tongue_Bulge_R', 'Jaw_Open', 'Jaw_Forward', 'Jaw_L', 'Jaw_R', 'Head_Turn_Up', 'Head_Turn_Down', 'Head_Turn_L', 'Head_Turn_R', 'Head_Tilt_L', 'Head_Tilt_R', 'Head_L', 'Head_R', 'Head_Forward', 'Head_Backward']

class EchoHandler(BaseRequestHandler):
    def setup(self):
        self.init_exp = False

    def handle(self):
        global add_value
        global max_value
        global avatar_exp_name
        global avatar_exp_change_name
        global avatar_exp_change_idx
        global send_data

        print('Got connection from', self.client_address)
        rcv_data = self.request.recv(10240).strip()
        exp_names_str = rcv_data.decode("utf-8")
        print('Receive Expresion Names from Client: '+exp_names_str)
        avatar_exp_name = exp_names_str.split(',')
        if len(avatar_exp_name) < 1:
            return

        send_data = [0]*len(avatar_exp_name)
        avatar_exp_change_idx = []
        for i in range(len(avatar_exp_name)):
            exp_name = avatar_exp_name[i]
            for find_name in avatar_exp_change_name:
                if exp_name.find(find_name) != -1:
                    avatar_exp_change_idx.append(i)
        if len(avatar_exp_change_idx) < 1:
            return

        while True:
            # send data
            for idx in avatar_exp_change_idx:
                send_data[idx] += add_value
                if add_value > 0 and send_data[idx] > max_value:
                    send_data[idx] = max_value
                    add_value = -add_value
                elif add_value <= 0 and send_data[idx] < 0:
                    send_data[idx] = 0
                    add_value = -add_value                    

            self.request.send(bytearray(send_data))
            time.sleep(0.05)

if __name__ == '__main__':
    # iclone has three type of expression set: Tradition(IC7 Standard), CC4 Standard, CC4 Extended

    HOST = str(socket.gethostbyname(socket.gethostname()))
    print("Facail Mocap Server ip: "+HOST+":"+str(PORT))
    serv = TCPServer((HOST, PORT), EchoHandler)
    serv.serve_forever()

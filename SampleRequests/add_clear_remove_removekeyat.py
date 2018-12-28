import RLPy
prop = RLPy.RScene.FindObject( RLPy.EObjectType_Prop, "Arc_001" )
if prop != None:
    control = prop.GetControl("Transform")
    #ClearKeys
    control.ClearKeys()
    print( control.GetKeyCount() ) # 0
    
    #Add 10 identity Keys
    key = RLPy.RTransformKey()
    key.SetTransform(RLPy.RTransform.IDENTITY)
    for i in range(10):
        key.SetTime(RLPy.RTime(i*16))
        control.AddKey(key, RLPy.RGlobal.GetFps())
   
    print( control.GetKeyCount() ) # 10
    
    #RemoveKey
    control.RemoveKey(RLPy.RTime(16))
    print( control.GetKeyCount() ) # 9
    
    #RemoveKeyAt
    i = 9
    while i >= 0:
        control.RemoveKeyAt(i)
        i -= 1
    print( control.GetKeyCount() ) # 0
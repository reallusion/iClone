import RLPy
prop = RLPy.RScene.FindObject( RLPy.EObjectType_Prop, "Arc_001" )
if prop != None:
    control = prop.GetControl("Transform")
    key_count = control.GetKeyCount()
    all_keys = []
    for i in range(key_count):
        key = RLPy.RTransformKey()
        control.GetTransformKeyAt(i, key)
        all_keys.append(key)
    print(len(all_keys))
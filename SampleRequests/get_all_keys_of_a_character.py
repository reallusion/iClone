import RLPy
avatar = RLPy.RScene.FindObject( RLPy.EObjectType_Avatar, "Zane" )
if avatar != None:
    control = avatar.GetControl("Transform")
    key_count = control.GetKeyCount()
    all_keys = []
    for i in range(key_count):
        key = RLPy.RTransformKey()
        control.GetTransformKeyAt(i, key)
        all_keys.append(key)
    print(len(all_keys))
    
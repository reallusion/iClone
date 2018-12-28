import RLPy
first_msgbox_option = RLPy.EMsgButton_Yes | RLPy.EMsgButton_No | RLPy.EMsgButton_Cancel
eClickBtn = RLPy.RUi.ShowMessageBox("Your title.", "Your message.", first_msgbox_option )
if eClickBtn == RLPy.EMsgButton_Yes:
    print("click yes")
elif eClickBtn == RLPy.EMsgButton_No:
    print("click no")
elif eClickBtn == RLPy.EMsgButton_Cancel:
    print("click cancel")

scend_msgbox_option = RLPy.EMsgButton_Ok | RLPy.EMsgButton_Cancel
eClickBtn2 = RLPy.RUi.ShowMessageBox("Your title.", "Your message.", scend_msgbox_option,  True, "Your checkbox text here." )
if eClickBtn2 == RLPy.EMsgButton_Ok:
    print("click ok.")
elif eClickBtn2 == RLPy.EMsgButton_OkDontAskAgain:
    print("your checkbox is checked.")
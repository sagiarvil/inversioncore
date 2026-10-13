import re
with open("main_phase2.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace('"Bu argumanda celiski var mi?"', '"Bu argümanda çelişki var mı?"')
code = code.replace('"Bu agda gizli araci var mi?"', '"Bu ağda gizli aracı var mı?"')

with open("main_phase2.py", "w", encoding="utf-8") as f:
    f.write(code)

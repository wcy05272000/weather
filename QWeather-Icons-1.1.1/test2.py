import math
# pre = -1
# for i in range(16):
#     if pre != math.floor(i/2):
#         print(math.floor(i/2))
#         pre = math.floor(i/2)

x = -1
for i in range(16):
    if x != math.floor(i / 2):
        x = math.floor(i / 2)
        print(x)


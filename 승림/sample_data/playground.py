from collections import deque
data = deque([1, 2, [3,4]])
while True:
    try:
        a = data.popleft()
        print(a[1])
        break
    except:
        print("1111")
        
    
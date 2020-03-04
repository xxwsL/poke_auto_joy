import tty
import sys, select,termios

settings = termios.tcgetattr(sys.stdin)

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key =''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


# while 1:
#     i = getKey()
#     if(i == 'e'):
#         break
#     print(i)
from PIL import Image
import random

size = (640, 640) 
black = (0,0,0)
white = (255,255,255)

def draw(size):
    im = Image.new("RGB", size)
    ll = []
    for i in range(size[0]):
        for j in range(size[1]):
            if random.random()>0.5:
                ll.append(white)
            else:
                ll.append(black)

    im.putdata(ll)    
    im.show()
    im.save("1.png")
    
def drawColor(size):
    im = Image.new("RGB", size)
    ll = []
    for i in range(size[0]):
        for j in range(size[1]):
            ll.append((random.randint(1,255),random.randint(1, 255),random.randint(1,255)))

    im.putdata(ll)    
    im.show()
    im.save("2.png")

def drawStyle(size):
    im = Image.new("RGB", size)
    ll = []
    for i in range(size[0]):
        for j in range(size[1]):
            c = (i+j)%255
            ll.append((i%255,c,j%255))

    im.putdata(ll)    
    im.show()
    im.save("3.png")
    
if __name__ == "__main__":
    draw(size)
    drawColor(size)
    drawStyle(size)        
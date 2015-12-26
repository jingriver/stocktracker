import random # Get a random number generator.

def singleShot():
    num_doors = 100
    swith = True
    box = [0]*num_doors    
    car = random.randint(0,num_doors-1)
    box[car] = 1
    
    first_choice = random.randint(0,num_doors-1)
    reduce = range(num_doors)
    reduce.remove(first_choice)
    if first_choice!=car:
        left = car
    else:
        left = reduce[0]
    #left = reduce[random.randint(0,1)]

    if swith:
        return box[left]
    else:
        return box[first_choice]        
        
def main():
    shared = 0
    sampleSpace = 10**4
    for i in range(sampleSpace):
        shared+=singleShot()
        
    p = float(shared)/sampleSpace
    print "%f" % p

main()
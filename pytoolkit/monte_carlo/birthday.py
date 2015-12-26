import random # Get a random number generator.

NUM_SAMPLE = 30

def singleShot():    
    taken = {}
    for i in range(NUM_SAMPLE):
        sbirthday = random.randrange(1, 366, 1)
        if sbirthday in taken:
            return 1
        else:
            taken[sbirthday] = 1
    return 0
        
def main():
    shared = 0
    sampleSpace = 10**4
    for i in range(sampleSpace):
        shared+=singleShot()
        
    p = float(shared)/sampleSpace
    print "%f" % p


NTRIALS = 10000 # Enough trials to get an reasonably accurate answer.
NPEOPLE = 30 # How many people in the group?
matches = 0 # Keep track of how many trials have matching birthdays.
for trial in range(NTRIALS): # Do a bunch of trials...
    taken = {} # A place to keep track of which birthdays
    # are already taken on this trial.
    for person in range(NPEOPLE):
        day = random.randint(0, 365) # On a randomly chosen day.
        if day in taken:
            matches += 1 # A match!
            break # No need to look for more than one.
        taken[day] = 1 # Mark the day as taken.

print "The fraction of trials that have matching birthdays is", float(matches)/NTRIALS    
main()
                
        
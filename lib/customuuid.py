import random
import string

def customuid(length=7):
    # Define the characters to choose from: lowercase letters and digits
    characters = string.ascii_lowercase + string.digits
    uid = ''
    
    # Generate a random UID of specified length
    for _ in range(length):
        random_index = random.randint(0, len(characters) - 1)
        uid += characters[random_index]
    
    return uid
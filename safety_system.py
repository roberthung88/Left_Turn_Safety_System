def safety_system(dist, vfoot):

    # Time of Arrival value calculated by the distance and velocity 
    toa = dist / vfoot 

    # if car past a certain distance, ignore it
    if dist > 200:
        return True
    
    # if car too close, just wait
    if dist < 50:
        return False

    # if logic to determine if it safe to turn based on the time of arrival. Assuming 7 seconds for a safe turn.
    if toa > 7: 
       return True
    if toa <= 7:
        return False
def safety_system(dist, vfoot)

    # Time of Arrival value calculated by the distance and velocity 
    toa = dist / vfoot 

    # if car past a certain distance, ignore it
    
    # if logic to determine if it safe to turn based on the time of arrival. Assuming 7 seconds for a safe turn.
    if toa > 7: 
        print("Go. Safe to turn.")
    if toa <= 7:
        print("Stop. Not safe to turn.")
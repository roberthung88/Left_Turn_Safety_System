def data_collection(startY, endY):
    # pixel to distance conversion
    starttemp = 0
    endtemp = 0
    
    # pixel tiers accounting for road depth in ft/pixel
    tone = 15/70 
    ttwo = 5/180
    tthree = 1/300
    tfour = 1/320
    tfive = 1/340

    if startY in range(0,180):
        starttemp = (180-startY) * tone
        starttemp =  (100 * tfive)
        starttemp += (tfour*120)
        starttemp += (tthree*140)
        starttemp += (ttwo*160)
    if startY in range(180, 340):
        starttemp =  (100 * tfive)
        starttemp += (tfour*120)
        starttemp += (tthree*140)
        starttemp += (340-startY) * ttwo
    if startY in range(340, 480):
        starttemp =  (100 * tfive)
        starttemp += (tfour*120)
        starttemp +=  (480-startY) * tthree
    if startY in range(480, 600):
        starttemp =  (100 * tfive)
        starttemp += (600-startY) * tfour
    if startY in range(600, 700):
        starttemp = (700-startY) * tfive

    if endY in range(0,180):
        endtemp = (180-endY) * tone
        endtemp =  (100 * tfive)
        endtemp += (tfour*120)
        endtemp += (tthree*140)
        endtemp += (ttwo*160)
    if endY in range(180, 340):
        endtemp =  (100 * tfive)
        endtemp += (tfour*120)
        endtemp += (tthree*140)
        endtemp += (340-endY) * ttwo
    if endY in range(340, 480):
        endtemp =  (100 * tfive)
        endtemp += (tfour*120)
        endtemp +=  (480-endY) * tthree
    if endY in range(480, 600):
        endtemp =  (100 * tfive)
        endtemp += (600-endY) * tfour
    if endY in range(600, 700):
        endtemp = (700-endY) * tfive

    ypix = starttemp - endtemp
    
    # velocity of vehicle in between detections
    # fps of 20
    vfoot = ypix / (1/20) # in ft/sec
    vmiles = vfoot * 0.681818 # in mph
    
    return vfoot

def distance_detection(vehicle, endY):
    tone = 15/10 
    ttwo = 5/12
    tthree = 1/70
    tfour = 1/320
    tfive = 1/340

    if endY in range(0,180):
        yfoot = (180-endY) * tone
        yfoot =  (100 * tfive)
        yfoot += (tfour*120)
        yfoot += (tthree*140)
        yfoot += (ttwo*160)
    if endY in range(180, 340):
        yfoot =  (100 * tfive)
        yfoot += (tfour*120)
        yfoot += (tthree*140)
        yfoot += (330-endY) * ttwo
    if endY in range(340, 480):
        yfoot =  (100 * tfive)
        yfoot += (tfour*120)
        yfoot +=  (480-endY) * tthree
    if endY in range(480, 600):
        yfoot =  (100 * tfive)
        yfoot += (600-endY) * tfour
    if endY in range(600, 700):
        yfoot = (700-endY) * tfive

    return yfoot - 1
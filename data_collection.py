def data_collection(startY, endY):
    # difference in pixels between two detection passes
    ypix = (endY - startY)

    # pixel tiers accounting for road depth in ft/pixel
    #tfive = 60/264 
    #tfour = 60/400
    #tthree = 60/500
    #ttwo = 60/600
    #tone = 60/700

    tfive = 40/100 
    tfour = 40/120
    tthree = 40/140
    ttwo = 40/160
    tone = 40/180

    # tier is determined by the endY value instead of the startY value to be conservative
    #if endY in range(0,700):
     #   yfoot = ypix * tone
    #if endY in range(700, 1300):
     #   yfoot = ypix * ttwo
    #if endY in range(1300, 1800):
     #   yfoot = ypix * tthree
    #if endY in range(1800, 2200):
     #   yfoot = ypix * tfour
    #if endY in range(2200, 2464):
     #   yfoot = ypix * tfive

    if endY in range(0,180):
        yfoot = ypix * tone
    if endY in range(180, 340):
        yfoot = ypix * ttwo
    if endY in range(340, 480):
        yfoot = ypix * tthree
    if endY in range(480, 600):
        yfoot = ypix * tfour
    if endY in range(600, 700):
        yfoot = ypix * tfive

    # velocity of vehicle in between detections
    
    # assuming the time difference between detections is one second (can change)
    vfoot = yfoot / 1 # in ft/sec
    vmiles = vfoot * 0.681818 # in mph

    return vmiles
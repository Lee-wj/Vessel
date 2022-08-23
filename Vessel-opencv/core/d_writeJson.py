import json

def writePoints(contourPoints):
    filename = '../json/contourPoints.json'
    with open(filename, 'w') as file_obj:
        json.dump(contourPoints, file_obj)
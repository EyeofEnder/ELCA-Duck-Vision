import requests

def getImage(self,path="./temp.jpeg",roverName="Rover03"): # gets image from camera and saves it as temp(img_number).jpeg

        temp = open("{}.jpeg".format(path), "wb")

        img = requests.get("http://192.168.1.10:5000/api/{}/image".format(roverName))

        temp.write(img.content)

        temp.close()
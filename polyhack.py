import requests,cv2,numpy,time,imutils

class imageAnalyzer():

    def __init__(self,
                 roverName="Rover03",
                 url="http://192.168.1.10:5000/api/",
                 temp_img_path = "./temp",
                 ):

        self.url = url + roverName

        self.temp_img_path = temp_img_path

    def getImage(self,img_number): # gets image from camera and saves it as temp(img_number).jpeg

        temp = open(self.temp_img_path + str(img_number) + ".jpeg", "wb")

        img = requests.get(self.url + "/image")

        temp.write(img.content)

        temp.close()

    def analyzeHSV(self,img_number,thresholds=(numpy.array([20,100,110]),numpy.array([40,255,255]))): # min, max, creates mask from HSV thresholds

        img = cv2.imread(self.temp_img_path + str(img_number) + ".jpeg")

        orig = numpy.copy(img)

        try:

            img = cv2.GaussianBlur(img,(7,7),8)

        except:

            pass

        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        ret = cv2.inRange(hsv, thresholds[0],thresholds[1])

        return ret,orig

    def findBoundingBoxes(self,img,orig=None,area_thresh=100,aspect_thresh=[0.8,1.0],y_threshold=[0,0.6]): # finds contours from mask and determines bound boxes, vetoes by minimum box area, aspect ratio and vertical screen portion

        con = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        con = imutils.grab_contours(con)

        if orig.any():

            cv2.drawContours(orig, con, -1, (255, 255, 255),thickness=2)

        bound = []

        for c in con:

            bound.append(cv2.boundingRect(c))

        bound = list(filter(lambda x: (x[2]*x[3] >= area_thresh) and (aspect_thresh[0] <= x[3]/x[2] <= aspect_thresh[1]) and 480*y_threshold[0] <= 480-x[1] <= 480*y_threshold[1], bound))  # vetoing based on minimal bounding box area, relative position in image and aspect ratio

        for b in bound:

            cv2.rectangle(orig,b,color=(0,0,255),thickness=2)

        cv2.imwrite("vis{}.jpg".format(0),orig)

        return bound

    def approx_distance(self,duckie_boxes,dist_half_screen=5,camera_y_res=480): # bounding boxes of ducks, calibration: distance in cm from camera to center of duck for duck to take up half of camera image height assuming duck size = const.

        distances = {}

        print(duckie_boxes)

        for box in duckie_boxes:

            distances[box] = round(dist_half_screen*(1/2)*(camera_y_res/box[3]))

        distances = [ (box, round(dist_half_screen*(1/2)*(camera_y_res/box[3]) ) ) for box in duckie_boxes] # NOTE: Y coordinate origin is from the top of the image, returns list of (rect=(x_anchor,y_anchor,x_size,y_size),distance) tuple-value pairs (note,y_size goes downwards!)

        return distances

    def capture(self,temp_image=0,db_file="temp_duck_boxes.txt"): # gets image, returns bounding boxes and distances according to NOTE, creates temp images temp(n) and vis(n) with n = temp_image argument as well as distance text file

        self.getImage(temp_image)

        ret = self.analyzeHSV(temp_image)

        boxes = self.findBoundingBoxes(ret[0], ret[1])

        duck_box_file = open(db_file, "w")

        dist = analyzer.approx_distance(boxes)

        duck_box_file.write(str(dist))

        duck_box_file.close()

        return boxes, dist


analyzer = imageAnalyzer()

while True:

    boxes, dist = analyzer.capture()

    time.sleep(0.5)




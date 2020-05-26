import cv2
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import math
import sc3nb as scn
from osc import OSC
from matplotlib import style


def callback(value):
    pass


def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--filter', required=True,
                    help='Range filter. RGB or HSV')
    ap.add_argument('-s', '--source', required=True,
                    help='Source. webcam or file')
    args = vars(ap.parse_args())

    if not args['filter'].upper() in ['RGB', 'HSV']:
        ap.error("Please specify a correct filter.")

    if not args['source'].upper() in ['WEBCAM', 'FILE']:
        ap.error("Please specify a correct source.")

    return args


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)
    return values


def compute_distance(xref, yref, xpoint, ypoint):

    dist = (xpoint-xref) ** 2 + (ypoint-yref) ** 2

    return dist


def main():
    xs = []
    ys = []

    axes = plt.gca()
    axes.set_xlim(-10, 1500)
    axes.set_ylim(-10, 1500)
    #line, = axes.plot(xs, ys, 'r-')

    args = get_arguments()
    range_filter = args['filter'].upper()
    source = args['source'].upper()

    if source == 'WEBCAM':
        cap = cv2.VideoCapture(0)
        frame_rate = 1
    elif source == 'FILE':
        cap = cv2.VideoCapture('Video1.avi')
        frame_rate = 25
    else:
        cap = 'no source'
        frame_rate = None
        print(cap)

    setup_trackbars(range_filter)

    while cap.isOpened():
        if args['source']:
            ret, image = cap.read()

            if not ret:
                break

            if range_filter == 'RGB':
                frame_to_thresh = image.copy()
            else:
                frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)

        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(image, center, 3, (0, 0, 255), -1)
                cv2.putText(image, "centroid", (center[0] + 10, center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
                cv2.putText(image, "(" + str(center[0]) + "," + str(center[1]) + ")", (center[0] + 10, center[1] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

                xs.append(x)
                ys.append(y)
                #line.set_xdata(xs)
                #line.set_ydata(ys)
                #plt.draw()
                plt.scatter(xs, ys, c='r')
                plt.pause(1e-17)
                #time.sleep(0.1)

                xref, yref = (xs[0], ys[0])
                xpoint, ypoint = (xs[-1], ys[-1])

                distance = compute_distance(xref, yref, xpoint, ypoint)
                if distance >= 1:
                    freq = distance + 400
                    sc.msg("/s_new", ["s1", -1, 1, 0, "freq", freq, "dur", 0.5, "num", 1])



            # show the frame to our screen
            cv2.imshow("Original", image)

        if cv2.waitKey(frame_rate) & 0xFF is ord('q'):
            break


sc = scn.startup()
#sc.console_logging = False


if __name__ == '__main__':
    main()

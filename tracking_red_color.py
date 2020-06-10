import cv2
import argparse
import numpy as np
import time
import math
import sc3nb as scn
from osc import OSC
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('tkagg')


def get_arguments():

    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--source', required=True,
                    help='Source. webcam or file')
    args = vars(ap.parse_args())

    if not args['source'].upper() in ['WEBCAM', 'FILE']:
        ap.error("Please specify a correct source.")

    return args


def compute_distance(xref, yref, x, y):
    dist = (x-xref) ** 2 + (y-yref) ** 2

    return dist


def main():
    xs = []
    ys = []
    axes = plt.gca()
    args = get_arguments()
    source = args['source'].upper()
    plt.get_current_fig_manager().window.wm_geometry("+2000+500")

    if source == 'WEBCAM':
        cap = cv2.VideoCapture(1)
        axes.set_xlim(0, 1200)
        axes.set_ylim(1000, 100)
        thr_radius = 50
    elif source == 'FILE':
        cap = cv2.VideoCapture('Video1.avi')
        axes.set_xlim(550, 750)
        axes.set_ylim(350, 500)
        thr_radius = 15
    else:
        cap = 'no source'
        xs = ys = None
        thr_radius = None
        print(cap)

    counter = 0
    t_0 = 0.0

    while cap.isOpened():
        t_1 = int(round(time.time() * 1000))
        print('delta time: ' + str(t_1 - t_0) + ' ms \n' + '     frame # ' + str(counter))
        t_0 = t_1

        if args['source']:
            ret, image = cap.read()

            if not ret:
                break

            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        h1_min, h2_min, h1_max, h2_max, s_min, s_max, v_min, v_max = (0, 170, 10, 180, 70, 255, 50, 255)

        #thresh_low = cv2.inRange(frame_to_thresh, (h1_min, s_min, v_min), (h1_max, s_max, v_max))
        thresh = cv2.inRange(frame_to_thresh, (h2_min, s_min, v_min), (h2_max, s_max, v_max))
        #thresh = thresh_low | thresh_high

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

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
                cv2.putText(image, "centroid", (center[0] + 10, center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255),
                            1)
                cv2.putText(image, "(" + str(center[0]) + "," + str(center[1]) + ")", (center[0] + 10, center[1] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

                xs.append(x)
                ys.append(y)

                xref, yref = (xs[0], ys[0])

                circle = plt.Circle((xref, yref), thr_radius, color='g', fill=False)
                axes.add_artist(circle)

                if counter % 25 == 0:
                    plt.draw()
                    plt.scatter(x, y, c='r', s=1)
                    plt.scatter(xs[0], ys[0], c='b', s=15)
                    plt.pause(1e-17)
                    # time.sleep(0.1)

                distance = math.sqrt(compute_distance(xref, yref, x, y))
                if distance >= thr_radius:
                    print('         distance: ' + str(int(distance)))

                    # Sonification
                    freq = distance*10 + 200
                    amp = distance/1000
                    amp = np.clip(amp, 0.1, 0.9)
                    sc.msg("/s_new", ["s1", -1, 1, 0, "freq", freq, "amp", amp, "dur", 0.5, "num", 1])

            # show the frame to our screen
            cv2.imshow("Original", image)
            cv2.moveWindow("Original", 0, 0)

        if cv2.waitKey(1) | 0xFF is ord('q'):
            break


sc = scn.startup()
sc.console_logging = False


if __name__ == '__main__':
    main()

import cv2
from time import sleep
import time
import subprocess as sp
from utils.yolo_classes import get_cls_dict
from utils.visualization import BBoxVisualization
from utils.yolo_with_plugins import TrtYOLO
import pycuda.autoinit

cap = cv2.VideoCapture('rtmp://localhost/live/stream_input')
cls_dict = get_cls_dict(80)
h = w = 288
model = 'yolov4-tiny-288'
trt_yolo = TrtYOLO(model, (h, w))
vis = BBoxVisualization(cls_dict)
rtmp_server_output = 'rtmp://localhost/live/stream_output'
command = ['ffmpeg',
               #'-re',
               '-i', '-',
               #'-c:v', 'libx264',
               #'-preset','superfast',
               '-maxrate', '3000k',
               '-bufsize', '6000k',
               #'-pix_fmt', 'yuv420p',
               #'-g', '50',
               #'-c:a', 'aac',
               #'-b:a', '160k',
               #'-ac', '2',
               #'-ar', '44100',
               #'-b:a', '160k',
               '-f', 'flv', 
                rtmp_server_output]
#process = sp.Popen(command, stdin=sp.PIPE, stderr=sp.DEVNULL)
process = sp.Popen(command, stdin=sp.PIPE, shell=False)
font = cv2.FONT_HERSHEY_PLAIN
fps = 0.0
tic = time.time()

def closedCapCallback():
    global cap

    print("no connection in the stream, reconnecting")
    cap = cv2.VideoCapture('rtmp://localhost/live/stream_input')
    sleep(1)

while True:
    if not cap.isOpened():
        #_, frame = None
        print('error while subprocess not running')
        closedCapCallback()
    else:
        _,frame = cap.read()
        if not frame is None:
            boxes, confs, clss = trt_yolo.detect(frame, 0.3)
            frame = vis.draw_bboxes(frame, boxes, confs, clss)
            cv2.putText(frame, "FPS: " + str(round(fps, 2)), (10, 50), font, 3, (255, 50, 0), 3)
            toc = time.time()
            curr_fps = 1.0 / (toc - tic)

            fps = curr_fps if fps == 0.0 else (fps * 0.95 + curr_fps * 0.05)
            tic = toc

            computing_time = (1/fps) * 1000
            cv2.putText(frame, str(round(computing_time, 2)) + " ms", (10, 90), font, 3, (255, 50, 0), 3)

            ret_toRTSP, frame_toRTSP = cv2.imencode('.png', frame)
            process.stdin.write(frame_toRTSP.tobytes())
            #process.stdin.write(frame.tostring())
            #cv2.imshow("cap",frame)
            if cv2.waitKey(1)==27:
                break

        else:
            print('error while subprocess is running')
            closedCapCallback()

cap.release()
cv2.destroyAllWindows()

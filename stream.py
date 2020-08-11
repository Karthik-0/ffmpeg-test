import os
import shlex
import sys
from subprocess import Popen, PIPE
import threading
import logging
import re

import boto3


from main import Process
from new2 import S3File
from utils import upload_dir

upload_directory = "big_video_multi_op"

params = {'Bucket': "media.testpress.in", "Key": "demo/testing/%v/"}

s3 = boto3.resource("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                    region_name="ap-southeast-1")

s3_object = s3.Object(bucket_name="media.testpress.in",
                      key="institute/sandbox/videos/232ae54d31614f3f95c46b2dce2c2975.mp4")
# s3_object = s3.Object(bucket_name="media.testpress.in",
#                       key="institute/institute/demo/bbb_sunflower_1080p_60fps_normal.mp4")

s3_file = S3File(s3_object)

# command = "ffmpeg -hwaccel cuda -c:v h264_cuvid -i - -zerolatency -preset medium -b:a 128k -map 0:0 -map 0:1 -map 0:0 -map 0:1 -map 0:0 -map 0:1 -s:v:0 " \
#           "640x360 -c:v:0 h264_nvenc -b:v:0 400k -s:v:1 960x540 -c:v:1 h264_nvenc -b:v:1 600k -s:v:2 1280x720 " \
#           "-b:v:2 1500k -c:v:2 h264_nvenc -var_stream_map 'v:0,a:0 v:1,a:1 v:2,a:2'  -master_pl_name big_video_multi_op/master.m3u8  -f hls " \
#           "-hls_time 10 -hls_list_size 0 -hls_flags temp_file  big_video_multi_op/segement%v/video.m3u8"

command = "ffmpeg -i - -c:a aac -ar 48000 -b:a 128k " \
          "-c:v h264 -s 1280x720 -b:v 1500k -preset veryfast  -f hls -hls_list_size 0 -hls_time 6 -hls_segment_filename 'big_video_multi_op/720p/video%d.ts' big_video_multi_op/720p/video.m3u8 "

command1 = "ffmpeg -i - -c:a aac -ar 48000 -b:a 128k " \
          "-c:v h264 -s 960x540 -b:v 600k -preset veryfast  -f hls -hls_list_size 0 -hls_time 6 -hls_segment_filename 'big_video_multi_op/540p/video%d.ts' big_video_multi_op/540p/video.m3u8 "

command2 = "ffmpeg -i - -c:a aac -ar 48000 -b:a 128k " \
           "-c:v h264 -s 640x360 -b:v 500k -preset veryfast  -f hls -hls_list_size 0 -hls_time 6 -hls_segment_filename 'big_video_multi_op/360p/video%d.ts' big_video_multi_op/360p/video.m3u8 "

def input_stream():
    # Working method ; Do not edit this
    p = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE)
    curr = 0
    while curr < s3_file.size:
        p.stdin.write(s3_file.read(100000))
        curr += 100000

    p.stdin.close()
    p.wait()


def upload_videos(line, exclude_m3u8=False):
    exclude_files = []
    if exclude_m3u8:
        exclude_files = ["video.m3u8"]

    regex_pattern = re.compile("(Opening .* for writing)")
    if regex_pattern.search(line):
        print("Upload Directory", upload_directory)
        upload_dir(upload_directory, exclude_files=exclude_files)


def monitor(ffmpeg, duration, time_, process):
    upload_videos(ffmpeg, exclude_m3u8=True)
    # print(ffmpeg)
    per = round(time_ / duration * 100)
    sys.stdout.write("\rTranscoding...(%s%%) [%s%s]" % (per, '#' * per, '-' * (100 - per)))
    sys.stdout.flush()


def process_poc(command):
    process = ProcessNew(command, monitor)
    process.run()


class ProcessNew(Process):
    def _thread_mon(self):
        thread = threading.Thread(target=self._monitor)
        thread.start()
        curr = 0

        while curr < s3_file.size:
            self.process.stdin.buffer.write(s3_file.read(32000000))
            curr += 32000000
        self.process.stdin.close()
        thread.join()

        if thread.is_alive():
            self.process.terminate()
            thread.join()
            error = 'Timeout! exceeded the timeout of seconds.'
            logging.error(error)
            raise RuntimeError(error)


if __name__ == "__main__":
    from new import AWS_SECRET_ACCESS_KEY
    # input_stream()
    a = input("Enter number : ")
    if str(a) == '720p':
        upload_directory = "big_video_multi_op/720p"
        process_poc(command)
    elif str(a) == "540p":
        upload_directory = "big_video_multi_op/540p"
        process_poc(command1)
    else:
        upload_directory = "big_video_multi_op/360p"
        process_poc(command2)
    upload_dir(upload_directory)
#  https://s3-ap-southeast-1.amazonaws.com/media.testpress.in/institute/sandbox/videos/232ae54d31614f3f95c46b2dce2c2975.mp4

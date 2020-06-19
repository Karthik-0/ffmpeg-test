import os
import shlex
import sys
from subprocess import Popen, PIPE
import threading
import logging
import re
from botocore.exceptions import ClientError

import boto3

from main import Process
from new2 import S3File
from utils import upload_dir

params = {'Bucket': "media.testpress.in", "Key": "demo/testing/%v/"}

s3 = boto3.resource("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                    region_name="ap-southeast-1")

s3_object = s3.Object(bucket_name="media.testpress.in",
                      key="institute/sandbox/videos/232ae54d31614f3f95c46b2dce2c2975.mp4")
# s3_object = s3.Object(bucket_name="media.testpress.in",
                    #   key="institute/institute/demo/1c61861f5875407fa2e3c1531ef6a602.mp4")

s3_file = S3File(s3_object)

command = "ffmpeg -i - -c:a aac -ar 48000 -b:a 128k  -map 0:0 -map 0:1 -map 0:0 -map 0:1 -map 0:0 -map 0:1 -s:v:0 " \
          "640x360 -c:v:0 libx265 -b:v:0 400k  -s:v:1 960x540 -c:v:1 libx265 -b:v:1 600k -s:v:1 1280x720 -c:v:2 " \
          "libx265 -b:v:1 1500k -var_stream_map 'v:0,a:0 v:1,a:1 v:2,a:2'  -master_pl_name video/master.m3u8  -f hls " \
          "-hls_time 6 -hls_list_size 0 -hls_flags temp_file  video/segement%v/video.m3u8"



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
        upload_dir("video", exclude_files=exclude_files)


def monitor(ffmpeg, duration, time_, process):
    # You can update a field in your database or log it to a file
    # You can also create a socket connection and show a progress bar to users
    # logging.info(ffmpeg) or print(ffmpeg)

    # if "something happened":
    #     process.terminate()
    upload_videos(ffmpeg, exclude_m3u8=True)
    per = round(time_ / duration * 100)
    sys.stdout.write("\rTranscoding...(%s%%) [%s%s]" % (per, '#' * per, '-' * (100 - per)))
    sys.stdout.flush()


def process_poc():
    process = ProcessNew(command, monitor)
    process.run()


class ProcessNew(Process):
    def _thread_mon(self):
        thread = threading.Thread(target=self._monitor)
        thread.start()
        curr = 0

        while curr < s3_file.size:
            self.process.stdin.buffer.write(s3_file.read(100000))
            curr += 100000
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
    print("Start Transcoding : ", AWS_SECRET_ACCESS_KEY)
    # input_stream()
    process_poc()
    upload_dir("video")

#  https://s3-ap-southeast-1.amazonaws.com/media.testpress.in/institute/sandbox/videos/232ae54d31614f3f95c46b2dce2c2975.mp4

# import ffmpeg_streaming
import os
import sys
# from ffmpeg_streaming import Formats, Bitrate, Representation, Size
# from ffmpeg_streaming import S3, CloudManager

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
REGION_NAME = "ap-southeast-1"


# def monitor(ffmpeg, duration, time_, process):
#     # You can update a field in your database or log it to a file
#     # You can also create a socket connection and show a progress bar to users
#     # logging.info(ffmpeg) or print(ffmpeg)
#
#     # if "something happened":
#     #     process.terminate()
#
#     per = round(time_ / duration * 100)
#     sys.stdout.write("\rTranscoding...(%s%%) [%s%s]" % (per, '#' * per, '-' * (100 - per)))
#     sys.stdout.flush()
#
#
# if __name__ == "__main__":
#     print("Running")
#     video = ffmpeg_streaming.input('/Users/karthik/Downloads/input.mp4')
#     hls = video.hls(Formats.h264())
#     hls.auto_generate_representations()
#     s3 = S3(
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#         region_name=REGION_NAME,
#         # bucket_name="media.testpress.in",
#         # folder="institute/demo/ffmpeg-streaming"
#     )
#
#     save_to_s3 = CloudManager().add(s3, bucket_name="media.testpress.in", folder="institute/demo/ffmpeg-streaming")
#
#     hls.output(clouds=save_to_s3, monitor=monitor)

import io
import boto3
import os


class S3File(io.RawIOBase):
    def __init__(self, s3_object):
        self.s3_object = s3_object
        self.position = 0

    def __repr__(self):
        return "<%s s3_object=%r>" % (type(self).__name__, self.s3_object)

    @property
    def size(self):
        return self.s3_object.content_length

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.position = offset
        elif whence == io.SEEK_CUR:
            self.position += offset
        elif whence == io.SEEK_END:
            self.position = self.size + offset
        else:
            raise ValueError("invalid whence (%r, should be %d, %d, %d)" % (
                whence, io.SEEK_SET, io.SEEK_CUR, io.SEEK_END
            ))

        return self.position

    def seekable(self):
        return True

    def read(self, size=-1):
        if size == -1:
            # Read to the end of the file
            range_header = "bytes=%d-" % self.position
            self.seek(offset=0, whence=io.SEEK_END)
        else:
            new_position = self.position + size

            # If we're going to read beyond the end of the object, return
            # the entire object.
            if new_position >= self.size:
                return self.read()

            range_header = "bytes=%d-%d" % (self.position, new_position - 1)
            self.seek(offset=size, whence=io.SEEK_CUR)

        return self.s3_object.get(Range=range_header)["Body"].read()

    def readable(self):
        return True



if __name__ == "__main__":
    import zipfile

    import boto3

    # s3 = boto3.resource("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    #         aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    #         region_name="ap-southeast-1")
    # s3_object = s3.Object(bucket_name="media.testpress.in", key="institute/institute/demo/courses/1c61861f5875407fa2e3c1531ef6a602.mp4")
    #
    # s3_file = S3File(s3_object)
    # with open("a3.mp4", "wb") as f:
    #     f.write(s3_file.read(100000000))
    # with open("a4.mp4", "wb") as f:
    #     f.write(s3_file.read(100000000))

    import subprocess
    import shlex

    import os
    from smart_open import open

    session = boto3.Session(aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name="ap-southeast-1")

    command = "ffmpeg -y -i - -c:a aac -ar 48000 -b:a 128k  -map 0:0 -map 0:1 -map " \
              "0:0 -map 0:1 -map 0:0 -map 0:1  -s:v:0 640x360 -c:v:0 libx265 -b:v:0 400k  -s:v:1 960x540 -c:v:1 " \
              "libx265 -b:v:1 600k -s:v:2 1280x720 -c:v:2 libx265 -b:v:2 1500k -var_stream_map 'v:0,a:0 v:1,a:1 v:2," \
              "a:2'  -master_pl_name master1.m3u8 -f hls -hls_time 6 -hls_list_size 0 -hls_flags append_list  -hls_segment_filename " \
              "'va%v/video_p1_%03d.ts'  va%v/video.m3u8"

    url = "s3://media.testpress.in/institute/institute/demo/courses/1c61861f5875407fa2e3c1531ef6a602.mp4"
    process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for line in open(url, 'rb', transport_params={'session': session}):
        process.communicate(line)

import re
import sys
import shlex
import subprocess
import threading
import logging

from ffmpeg_streaming import Format

def transcode_video():
    command = "ffmpeg -y -i /Users/karthik/Downloads/input.mp4 -c:a aac -ar 48000 -b:a 128k  -map 0:0 -map 0:1 -map " \
              "0:0 -map 0:1 -map 0:0 -map 0:1  -s:v:0 640x360 -c:v:0 libx265 -b:v:0 400k  -s:v:1 960x540 -c:v:1 " \
              "libx265 -b:v:1 600k -s:v:2 1280x720 -c:v:2 libx265 -b:v:2 1500k -var_stream_map 'v:0,a:0 v:1,a:1 v:2," \
              "a:2'  -master_pl_name master1.m3u8 -f hls -hls_time 6 -hls_list_size 0 -hls_flags append_list  -hls_segment_filename " \
              "'va%v/video_p1_%03d.ts'  va%v/video.m3u8"
    return command


def transcode_encrypted_video():
    command = "ffmpeg -y -i /Users/karthik/Downloads/input.mp4 -c:a aac -ar 48000 -b:a 128k  -map 0:0 -map 0:1 -map " \
              "0:0 -map 0:1 -map 0:0 -map 0:1  -s:v:0 640x360 -c:v:0 libx265 -b:v:0 400k  -s:v:1 960x540 -c:v:1 " \
              "libx265 -b:v:1 600k -s:v:2 1280x720 -c:v:2 libx265 -b:v:2 1500k -var_stream_map 'v:0,a:0 v:1,a:1 v:2," \
              "a:2'  -master_pl_name master.m3u8 -f hls -hls_time 6 -hls_list_size 0  -hls_segment_filename " \
              "'v%v/video%03d.ts' -hls_key_info_file enc.keyinfo  v%v/video.m3u8"
    return command


def _p_open(commands, **options):
    logging.info("ffmpeg running command: {}".format(commands))
    print("Options : ", options)
    return subprocess.Popen(shlex.split(commands), **options)


def convert_to_sec(time):
    h, m, s = time.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def get_time(key, string, default):
    time = re.search('(?<=' + key + ')\w+:\w+:\w+', string)
    return convert_to_sec(time.group(0)) if time else default


class Process(object):
    out = None
    err = None

    def __init__(self, commands: str, monitor: callable = None, **options):
        default_proc_opts = {
            'stdin': None,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
            'universal_newlines': False
        }
        default_proc_opts.update(options)
        options.update(default_proc_opts)
        options.update({
            'stdin': subprocess.PIPE,
            'universal_newlines': True
        })
        self.process = _p_open(commands, **options)
        self.monitor = monitor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process.kill()

    def _monitor(self):
        duration = 1
        time = 0
        log = []

        while True:
            line = self.process.stdout.readline().strip()
            if line == '' and self.process.poll() is not None:
                break

            if line != '':
                log += [line]

            if callable(self.monitor):
                if type(line) == str:
                    duration = get_time('Duration: ', line, duration)
                    time = get_time('time=', line, time)
                    self.monitor(line, duration, time, self.process)

        Process.out = log

    def _thread_mon(self):
        thread = threading.Thread(target=self._monitor)
        thread.start()

        thread.join()
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            error = 'Timeout! exceeded the timeout of seconds.'
            logging.error(error)
            raise RuntimeError(error)

    def run(self):
        self._thread_mon()

        if self.process.poll():
            error = str(Process.err) if Process.err else str(Process.out)
            logging.error('ffmpeg failed to execute command: {}'.format(error))
            raise RuntimeError('ffmpeg failed to execute command: ', error)
        logging.info("ffmpeg executed command successfully")

        return Process.out, Process.err


def monitor(ffmpeg, duration, time_, process):
    # You can update a field in your database or log it to a file
    # You can also create a socket connection and show a progress bar to users
    # logging.info(ffmpeg) or print(ffmpeg)

    # if "something happened":
    #     process.terminate()

    per = round(time_ / duration * 100)
    sys.stdout.write("\rTranscoding...(%s%%) [%s%s]" % (per, '#' * per, '-' * (100 - per)))
    sys.stdout.flush()


if __name__ == "__main__":
    process = Process(transcode_video(), monitor)
    process.run()

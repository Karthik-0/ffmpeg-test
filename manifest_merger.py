from m3u8_generator import PlaylistGenerator

if __name__ == "__main__":
    master_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n"
    media_details = [{
        "bandwidth": 600000,
        "resolution": "960x540",
        "name": "540p/video.m3u8"
    },
        {
            "bandwidth": 1500000,
            "resolution": "1280x720",
            "name": "720p/video.m3u8"
        }
    ]
    for media_detail in media_details:
        master_playlist += f"#EXT-X-STREAM-INF:BANDWIDTH={media_detail['bandwidth']},RESOLUTION={media_detail['resolution']}\n{media_detail['name']}.m3u8\n\n"

    print(master_playlist)

    master_m3u8 = open("big_video_multi_op/master.m3ui8", "wt")
    master_m3u8.write(master_playlist)
    master_m3u8.close()

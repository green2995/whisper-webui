import subprocess
import math
import tempfile
import os

def to_timestamp(seconds: float):
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)

    hour = int(hours)
    min = int(minutes - hours * 60)
    sec = int(seconds - minutes * 60)

    return f'{str(hour).rjust(2, "0")}:{str(min).rjust(2, "0")}:{str(sec).rjust(2, "0")}'


class SliceAudioFailureException(Exception):
    "slice audio failed"


def slice_audio(audio_filepath: str, start: float, end: float) -> str:
    root, ext = os.path.splitext(audio_filepath)
    output_path = f"{tempfile.mkdtemp()}/{root}_{start}_{end}{ext}"

    try:
        subprocess.run(
            f'ffmpeg -y -i {audio_filepath} -ss {to_timestamp(start)} -to {to_timestamp(end)} -c:a copy {output_path}',
            shell=True
        )

        return output_path
    except:
        raise SliceAudioFailureException

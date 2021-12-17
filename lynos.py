from typing import Optional
import soco
import dataclasses as dc
from PIL import Image
import requests


@dc.dataclass
class TrackInfo:
    title: str
    artist: str
    album: str
    album_art: Image
    position: str  # This is actually timedelta with format of xx:yy:zz
    # Other info are thrown away


def pick_speaker_with_name(name: str):
    for speaker in soco.discover():
        if speaker.player_name == name:
            return speaker
    raise RuntimeError(f"Cannot find speaker (zone) with name {name}")


def get_track_info(speaker: soco.SoCo) -> Optional[TrackInfo]:
    result = speaker.get_current_track_info()
    print(result)
    if result and result["title"]:
        return TrackInfo(
            title=result["title"],
            artist=result["artist"],
            album=result["album"],
            album_art=Image.open(requests.get(result["album_art"], stream=True).raw),
        )
    return None


if __name__ == "__main__":
    speaker = pick_speaker_with_name("Book Room")
    track_info = get_track_info(speaker)
    if track_info:
        track_info.album_art.show()
    else:
        print("No track is being played")

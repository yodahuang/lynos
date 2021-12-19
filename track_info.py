import dataclasses as dc
import functools
from typing import Optional

import requests
import soco
import toml
from lyricsgenius import Genius
from PIL import Image


@dc.dataclass
class TrackInfo:
    title: str
    artist: str
    album: str
    album_art: Image
    position: str  # This is actually timedelta with format of xx:yy:zz
    # Other info are thrown away

    @functools.cached_property
    def cleaned_title(self) -> str:
        """Make sure there's no something like (Remastered 2009) in the title"""
        return self.title.split("(")[0].strip()

    @functools.cached_property
    def lyrics(self) -> str:
        token = toml.load("api_secrets.toml")["genius"]["client_access_token"]
        genius = Genius(token)
        song = genius.search_song(self.cleaned_title, self.artist)
        return song.lyrics


def pick_speaker_with_name(name: str):
    for speaker in soco.discover():
        if speaker.player_name == name:
            return speaker
    raise RuntimeError(f"Cannot find speaker (zone) with name {name}")


@functools.singledispatch
def get_track_info(speaker):
    raise NotImplementedError(f"Type {type(speaker)} is not supported")


@get_track_info.register
def _(speaker: soco.SoCo) -> Optional[TrackInfo]:
    result = speaker.get_current_track_info()
    if result and result["title"]:
        return TrackInfo(
            title=result["title"],
            artist=result["artist"],
            album=result["album"],
            album_art=Image.open(requests.get(result["album_art"], stream=True).raw),
            position=result["position"],
        )
    return None


@get_track_info.register
def _(speaker: str) -> Optional[TrackInfo]:
    speaker = pick_speaker_with_name(speaker)
    return get_track_info(speaker)


if __name__ == "__main__":
    speaker = pick_speaker_with_name("Book Room")
    track_info = get_track_info(speaker)
    if track_info:
        track_info.album_art.show()
        print(track_info.lyrics)
    else:
        print("No track is being played")

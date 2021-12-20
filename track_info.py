from __future__ import annotations

import dataclasses as dc
import functools
import os
from typing import Optional, Union

import requests
import soco
import toml
from lyricsgenius import Genius
from PIL import Image


class NoSuchZoneError(Exception):
    def __init__(self, zone: str):
        self.zone = zone


class NoSongBeingPlayedError(Exception):
    def __init__(self, zone: str):
        self.zone = zone


@dc.dataclass
class RawTrackInfo:
    """A dataclass that represents the raw data from the SoCo API."""

    title: str
    artist: str
    album: str
    album_art: str
    position: str
    playlist_position: str
    duration: str
    uri: str
    metadata: str


@dc.dataclass
class TrackInfo:
    """Processed version of RawTrackInfo."""

    title: str
    cleaned_title: str
    artist: str
    album: str
    album_art: Image
    # Other info are thrown away
    lyrics: str

    @staticmethod
    def from_raw(raw: RawTrackInfo) -> TrackInfo:
        # Clean title
        cleaned_title = raw.title.split("(")[0].strip()

        # Grab lyrics
        token = os.getenv(
            "GENIUS_ACCESS_TOKEN",
            toml.load("api_secrets.toml")["genius"]["client_access_token"],
        )
        genius = Genius(token, retries=3)
        song = genius.search_song(cleaned_title, raw.artist)
        lyrics = song.lyrics

        # Grab album art
        album_art = Image.open(requests.get(raw.album_art, stream=True).raw)

        return TrackInfo(
            title=raw.title,
            cleaned_title=cleaned_title,
            artist=raw.artist,
            album=raw.album,
            album_art=album_art,
            lyrics=lyrics,
        )


def pick_speaker_with_name(name: str):
    for speaker in soco.discover():
        if speaker.player_name == name:
            return speaker
    raise NoSuchZoneError(name)


@functools.singledispatch
def get_raw_track_info(speaker):
    raise NotImplementedError(f"Type {type(speaker)} is not supported")


@get_raw_track_info.register
def _(speaker: soco.SoCo) -> Optional[TrackInfo]:
    result = speaker.get_current_track_info()
    if not result or not result.get("title"):
        raise NoSongBeingPlayedError(speaker.player_name)
    return RawTrackInfo(**result)


@get_raw_track_info.register
def _(speaker: str) -> Optional[TrackInfo]:
    speaker = pick_speaker_with_name(speaker)
    return get_raw_track_info(speaker)


def get_track_info(speaker: Union[soco.SoCo, str]) -> Optional[TrackInfo]:
    return TrackInfo.from_raw(get_raw_track_info(speaker))


# Just for debugging purposes.
if __name__ == "__main__":
    speaker = pick_speaker_with_name("Book Room")
    track_info = get_track_info(speaker)
    if track_info:
        track_info.album_art.show()
        print(track_info.lyrics)
    else:
        print("No track is being played")

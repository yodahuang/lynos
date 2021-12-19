"""Have to use REST instead of GraphQL / GRPC as Starlark (more specifically, Starlib) only supports REST."""

from __future__ import annotations
from fastapi import FastAPI, Request
from track_info import (
    RawTrackInfo,
    TrackInfo,
    get_track_info,
    get_raw_track_info,
    NoSongBeingPlayedError,
    NoSuchZoneError,
)
from io import BytesIO
import base64
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class SimpleTrackInfoResponse(BaseModel):
    title: str
    artist: str

    @staticmethod
    def from_track_info(track_info: RawTrackInfo) -> SimpleTrackInfoResponse:
        return SimpleTrackInfoResponse(title=track_info.title, artist=track_info.artist)


class RichTrackInfoResponse(BaseModel):
    title: str
    artist: str
    album: str
    album_art: str  # Image as base64 string
    lyrics: str

    @staticmethod
    def from_track_info(track_info: TrackInfo) -> RichTrackInfoResponse:
        buffered = BytesIO()
        track_info.album_art.save(buffered, format="PNG")
        album_art = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return RichTrackInfoResponse(
            title=track_info.title,
            artist=track_info.artist,
            album=track_info.album,
            album_art=album_art,
            lyrics=track_info.lyrics,
        )


@app.exception_handler(NoSongBeingPlayedError)
async def no_song_being_played_exception_handler(
    request: Request, exc: NoSongBeingPlayedError
):
    return JSONResponse(
        status_code=418,
        content={"message": f"The player at {exc.zone} is not playing anything."},
    )


@app.exception_handler(NoSuchZoneError)
async def no_such_zone_exception_handler(request: Request, exc: NoSuchZoneError):
    return JSONResponse(
        status_code=418,
        content={"message": f"No player named {exc.zone}."},
    )


@app.get("/")
async def root():
    return "I am a teapot"


@app.get("/simple_track_info/{speaker}", response_model=SimpleTrackInfoResponse)
async def simple_track_info(speaker: str):
    """A quick way to get title and artist of the current track."""
    return SimpleTrackInfoResponse.from_track_info(get_raw_track_info(speaker))


@app.get("/rich_track_info/{speaker}", response_model=RichTrackInfoResponse)
async def rich_track_info(speaker: str) -> RichTrackInfoResponse:
    """A more detailed way to get all the things of the current track."""
    return RichTrackInfoResponse.from_track_info(get_track_info(speaker))

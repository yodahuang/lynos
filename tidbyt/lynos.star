load("render.star", "render")
load("http.star", "http")
load("encoding/base64.star", "base64")
load("cache.star", "cache")

ZONE_NAME = "Book Room"
SERVER_URI = "http://192.168.4.153:4242"

def get_simple_track_info():
    rep = http.get("{}/simple_track_info/{}".format(SERVER_URI, ZONE_NAME))
    if rep.status_code != 200:
        fail("Failed to get track info %d", rep.status_code)
    return rep.json()    


def main():
    track_info = get_simple_track_info()

    return render.Root(
        child = render.Box(
            render.Row(
                expanded=True,
                main_align="space_evenly",
                cross_align="center",
                children = [
                    render.Text(track_info["title"]),
                ],
            ),
        ),
    )
WING = "M4 -6 C 22 -22 52 -50 96 -70 C 78 -46 68 -26 64 -2 C 46 -8 24 -6 6 6 Z"
TAIL = "M6 14 C 26 10 50 18 70 38 C 48 32 26 32 6 30 Z"
BODY = "M0 -44 C 8 -18 9 14 0 56 C -9 14 -8 -18 0 -44 Z"

CRIMSON = "#ff1f4b"
CRIMSON_DEEP = "#b0002a"
VIOLET = "#8a00ff"
INK = "#0b0610"
PAPER = "#e9e1f2"
MUTED = "#9a8cae"


def sigil(x, y, scale=1.0, fill="url(#geass)", extra=""):
    return (
        f'<g transform="translate({x} {y}) scale({scale})" fill="{fill}" {extra}>'
        f'<path d="{WING}"/><path d="{WING}" transform="scale(-1 1)"/>'
        f'<path d="{TAIL}"/><path d="{TAIL}" transform="scale(-1 1)"/><path d="{BODY}"/></g>'
    )


def gradient_defs():
    return (
        '<linearGradient id="geass" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{CRIMSON}"/><stop offset="1" stop-color="{CRIMSON_DEEP}"/>'
        "</linearGradient>"
        '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

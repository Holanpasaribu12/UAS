"""Real Bandung tourist-place coordinates and geographic distances."""

import itertools
import math


TITIK_AWAL = "Gedung Sate"

TEMPAT_WISATA = {
    "Gedung Sate": (-6.9025, 107.6187),
    "Museum Geologi": (-6.9006, 107.6213),
    "Braga": (-6.9175, 107.6095),
    "Alun-Alun Bandung": (-6.9217, 107.6071),
    "Trans Studio Bandung": (-6.9250, 107.6369),
    "Saung Angklung Udjo": (-6.9000, 107.6550),
}


def jarak_haversine(koordinat_a, koordinat_b):
    """Return great-circle distance in kilometers between two coordinates."""
    lintang_a, bujur_a = map(math.radians, koordinat_a)
    lintang_b, bujur_b = map(math.radians, koordinat_b)
    delta_lintang = lintang_b - lintang_a
    delta_bujur = bujur_b - bujur_a
    nilai = (
        math.sin(delta_lintang / 2) ** 2
        + math.cos(lintang_a)
        * math.cos(lintang_b)
        * math.sin(delta_bujur / 2) ** 2
    )
    return 2 * 6_371 * math.asin(math.sqrt(nilai))


def buat_matriks_jarak(tempat):
    """Build pairwise straight-line distances in kilometers."""
    jarak = {}
    for nama_a, nama_b in itertools.combinations(tempat, 2):
        jarak[(nama_a, nama_b)] = jarak_haversine(
            TEMPAT_WISATA[nama_a],
            TEMPAT_WISATA[nama_b],
        )
    return jarak


def url_openstreetmap(nama_tempat):
    """Return an OpenStreetMap link centered on the selected real place."""
    lintang, bujur = TEMPAT_WISATA[nama_tempat]
    return (
        f"https://www.openstreetmap.org/?mlat={lintang}&mlon={bujur}"
        f"#map=17/{lintang}/{bujur}"
    )

"""Measure / derive texture data from the shared asset library (system python3 with PIL + numpy + scipy).

    python3 tools/maps.py jupiter    the Jupiter map's mean linear luminance and Great Red Spot position
                                     (the constants at the top of blender/lib/jupiter.py)
    python3 tools/maps.py io         our site cut out of the USGS Io colour mosaic, reprojected to the film's local
                                     frame (X west, Y south, 1 km/px, site at the centre) →
                                     blender/textures/src/io_site_1km.png, + a palette of the site's colours
    python3 tools/maps.py far        a stand-in for 05's far ground (user 2026-10-03): the site's own mosaic is smeared
                                     poleward of ~60°, so a well-imaged northern region (FAR_CENTRE) is reprojected
                                     the same way, 2048 km across → blender/textures/src/io_far_1km.png, + its mean
                                     linear colour (the constant in blender/lib/globe.py)

Blender never reads the 100–200 MB source files pixel by pixel: it loads the map as a texture and uses these numbers.
"""
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
FILM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.expanduser('~/dev/workspace/claude/videos/_assets/textures')
JUP = os.path.join(ASSETS, 'jupiter/jupiter_map_css_plus_juno_bj.png')
IO = os.path.join(ASSETS, 'io/Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_1km.tif')
sys.path.insert(0, os.path.join(FILM, 'tools'))
import physics as P


def lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def jupiter():
    im = Image.open(JUP).convert('RGB')
    W, H = im.size
    small = np.asarray(im.resize((W // 8, H // 8), Image.BOX)).astype(np.float64) / 255
    lum = float((lin(small) * [0.2126, 0.7152, 0.0722]).sum(-1).mean())
    red = small[..., 0] - 0.5 * (small[..., 1] + small[..., 2])
    h = small.shape[0]
    band = ndimage.uniform_filter(red[int(h * 0.55):int(h * 0.68)], 9)
    y, x = np.unravel_index(band.argmax(), band.shape)
    u, v = x / small.shape[1], 1 - (y + int(h * 0.55)) / h
    print(f'{os.path.basename(JUP)}: {W}×{H}; mean linear luminance {lum:.4f}; GRS at u {u:.4f}, v {v:.4f} '
          f'(lat {180 * v - 90:.1f}°)')


def _georef(im):
    """(lon0, lat0, dlon, dlat) of pixel (0, 0)'s corner and the pixel size in degrees, from the GeoTIFF tags."""
    tags = im.tag_v2
    scale, tie = tags.get(33550), tags.get(33922)
    W, H = im.size
    if scale and tie:
        R = P.R_IO * 1000.0
        sx, sy = scale[0], scale[1]
        x0, y0 = tie[3], tie[4]
        if abs(sx) > 1.0:                                    # metres (equirectangular on the sphere)
            k = 180.0 / (math.pi * R)
            return x0 * k, y0 * k, sx * k, -sy * k                # rows run south
        return x0, y0, sx, -sy
    return -180.0, 90.0, 360.0 / W, -180.0 / H              # assume a global −180..180 grid


def io(size=1024, km_px=1.0):
    im = Image.open(IO)
    print(f'{os.path.basename(IO)}: {im.size} {im.mode}')
    lon0, lat0, dlon, dlat = _georef(im)
    print(f'georef: corner lon {lon0:.3f} lat {lat0:.3f}, pixel {dlon:.5f}° × {dlat:.5f}°')
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255
    prev = os.path.expanduser('~/dev/workspace/claude/videos/_assets/previews/io-usgs-colour-mosaic.jpg')
    if not os.path.exists(prev):
        Image.fromarray((a[::8, ::8] * 255).astype(np.uint8)).save(prev, quality=85)
    # the site: SITE_THETA from the sub-Jupiter point (lon 0) toward the north pole
    lat_s = math.radians(P.SITE_THETA)                        # latitude = SITE_THETA (on the lon-0 meridian)
    s = np.array([math.cos(lat_s), 0.0, math.sin(lat_s)])     # Io frame: x → lon 0, z → north
    north = np.array([-math.sin(lat_s), 0.0, math.cos(lat_s)])
    east = np.array([0.0, 1.0, 0.0])
    R = P.R_IO
    half = size * km_px / 2
    xs = (np.arange(size) + 0.5) * km_px - half                # west (km), left → right
    ys = half - (np.arange(size) + 0.5) * km_px                # south (km), image top = far south (toward Jupiter)
    X, Y = np.meshgrid(xs, ys)
    rho = np.hypot(X, Y) + 1e-9
    phi = rho / R
    d = (-X[..., None] * east - Y[..., None] * north) / rho[..., None]
    p = np.cos(phi)[..., None] * s + np.sin(phi)[..., None] * d
    lat = np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1)))
    lon = np.degrees(np.arctan2(p[..., 1], p[..., 0]))            # east longitude
    col = (lon - lon0) / dlon
    if dlon > 0:
        col = np.mod(col, a.shape[1])
    row = (lat - lat0) / dlat
    out = np.stack([ndimage.map_coordinates(a[..., c], [row - 0.5, col - 0.5], order=1, mode='nearest')
                    for c in range(3)], -1)
    os.makedirs(os.path.join(FILM, 'blender/textures/src'), exist_ok=True)
    dst = os.path.join(FILM, 'blender/textures/src/io_site_1km.png')
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(dst)
    print(f'site map → {os.path.relpath(dst, FILM)} ({size} km across, {km_px} km/px, X west, Y south up)')
    c = out[size // 2 - 200:size // 2 + 200, size // 2 - 200:size // 2 + 200].reshape(-1, 3)
    L = lin(c.astype(np.float64))
    print(f'site ±200 km: mean sRGB {c.mean(0).round(3)}, mean linear {L.mean(0).round(3)}')
    # palette: 6 clusters (k-means, a few rounds) of the site's colours, linear, by share
    rng = np.random.default_rng(0)
    pts = L[rng.choice(len(L), 20000, replace=False)]
    cen = pts[rng.choice(len(pts), 6, replace=False)]
    for _ in range(25):
        k = np.argmin(((pts[:, None] - cen[None]) ** 2).sum(-1), 1)
        cen = np.array([pts[k == j].mean(0) if (k == j).any() else cen[j] for j in range(6)])
    share = np.bincount(k, minlength=6) / len(k)
    for j in np.argsort(-share):
        print(f'  {share[j] * 100:5.1f} %  linear {tuple(cen[j].round(3))}')


FAR_CENTRE = (48.0, 0.25)       # latitude, and position across the mosaic (0..1 from its west edge): brown plains,
                                 # dark paterae, white SO2 patches, Galileo coverage (picked on the preview)


def far(size=2048, km_px=1.0):
    im = Image.open(IO)
    lon0, lat0, dlon, dlat = _georef(im)
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255
    lat_c, u = FAR_CENTRE
    lon_c = lon0 + u * a.shape[1] * dlon
    la, lo = math.radians(lat_c), math.radians(lon_c)
    s = np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
    north = np.array([-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)])
    east = np.array([-math.sin(lo), math.cos(lo), 0.0])
    R = P.R_IO
    half = size * km_px / 2
    xs = (np.arange(size) + 0.5) * km_px - half
    ys = half - (np.arange(size) + 0.5) * km_px
    X, Y = np.meshgrid(xs, ys)
    rho = np.hypot(X, Y) + 1e-9
    phi = rho / R
    d = (-X[..., None] * east - Y[..., None] * north) / rho[..., None]
    p = np.cos(phi)[..., None] * s + np.sin(phi)[..., None] * d
    lat = np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1)))
    lon = np.degrees(np.arctan2(p[..., 1], p[..., 0]))
    col = np.mod((lon - lon0) / dlon, a.shape[1])
    row = (lat - lat0) / dlat
    out = np.stack([ndimage.map_coordinates(a[..., c], [row - 0.5, col - 0.5], order=1, mode='nearest')
                    for c in range(3)], -1)
    dst = os.path.join(FILM, 'blender/textures/src/io_far_1km.png')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(dst)
    L = lin(out.reshape(-1, 3).astype(np.float64))
    print(f'far stand-in: centre {lat_c:.1f}° N, lon {lon_c:.1f}° → {os.path.relpath(dst, FILM)} ({size} km, {km_px} km/px)')
    print(f'mean linear {tuple(L.mean(0).round(4))}')


if __name__ == '__main__':
    {'jupiter': jupiter, 'io': io, 'far': far}[sys.argv[1]]()

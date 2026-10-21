"""Build a 2.5D Mage mesh (GLB) from the Memoji sticker and its estimated depth map.

Front surface = depth map + silhouette inflation; back surface = flattened mirror, so the
model is closed and reads as a solid figure when it turns up to ~30 degrees.

    python tools/build_mage_glb.py sticker.png depth.npy assets/models/mage.glb

The depth map comes from Depth Anything V2 Small (transformers 'depth-estimation' pipeline)
run on the sticker composited over white, resized back to the sticker's size.
"""
import io
import json
import struct
import sys

import numpy as np
from PIL import Image

SRC, DEPTH, OUT = sys.argv[1:4]
STEP = 3                      # pixels per grid cell
CROP = (76, 62, 436, 450)     # same crop as the 2D image

img = Image.open(SRC).convert('RGBA').crop(CROP)
W, H = img.size
alpha = np.array(img)[:, :, 3].astype(np.float32) / 255
depth = np.load(DEPTH)[CROP[1]:CROP[3], CROP[0]:CROP[2]]

gw, gh = W // STEP + 1, H // STEP + 1
ys = np.minimum(np.arange(gh) * STEP, H - 1)
xs = np.minimum(np.arange(gw) * STEP, W - 1)
a = alpha[np.ix_(ys, xs)]
inside = a > 0.5
# Geometry covers the silhouette plus one cell, so the texture's alpha (not the grid) draws the edge.
geo = inside.copy()
geo[1:, :] |= inside[:-1, :]; geo[:-1, :] |= inside[1:, :]; geo[:, 1:] |= inside[:, :-1]; geo[:, :-1] |= inside[:, 1:]

# Chamfer distance to the silhouette edge (two passes), in grid cells.
INF = 1e9
dist = np.where(inside, INF, 0.0)
for y in range(gh):
    for x in range(gw):
        if dist[y, x]:
            d = dist[y, x]
            if y: d = min(d, dist[y - 1, x] + 1, dist[y - 1, x - 1] + 1.414 if x else INF, dist[y - 1, x + 1] + 1.414 if x + 1 < gw else INF)
            if x: d = min(d, dist[y, x - 1] + 1)
            dist[y, x] = d
for y in range(gh - 1, -1, -1):
    for x in range(gw - 1, -1, -1):
        if dist[y, x]:
            d = dist[y, x]
            if y + 1 < gh: d = min(d, dist[y + 1, x] + 1, dist[y + 1, x + 1] + 1.414 if x + 1 < gw else INF, dist[y + 1, x - 1] + 1.414 if x else INF)
            if x + 1 < gw: d = min(d, dist[y, x + 1] + 1)
            dist[y, x] = d
dist[dist >= INF] = 0
inflate = np.sqrt(np.clip(dist, 0, None))
inflate /= inflate.max()

d = depth[np.ix_(ys, xs)]
lo, hi = np.percentile(d[inside], [2, 98])
dn = np.clip((d - lo) / (hi - lo), 0, 1)

scale = 1.0 / max(W, H)                       # model units: tallest side = 1
# Fade the depth term to zero over the last few cells before the outline, so there's no cliff
# for the texture to smear down when the model turns.
edge = np.clip(dist / 5.0, 0, 1); edge = edge * edge * (3 - 2 * edge)
z_front = (0.10 * dn * edge + 0.11 * inflate) * inside
z_back = -0.045 * inflate * inside

# Vertices: front grid then back grid (only cells we use).
idx = -np.ones((gh, gw), dtype=np.int64)
pos, uv, faces_f = [], [], []
for y in range(gh):
    for x in range(gw):
        if geo[y, x]:
            idx[y, x] = len(pos)
            pos.append(((xs[x] - W / 2) * scale, (H - ys[y]) * scale, z_front[y, x]))
            uv.append((xs[x] / W, ys[y] / H))
nf = len(pos)
back = [(p[0], p[1], 0.0) for p in pos]
for y in range(gh):
    for x in range(gw):
        if geo[y, x]:
            back[idx[y, x]] = (pos[idx[y, x]][0], pos[idx[y, x]][1], z_back[y, x])
pos = pos + back
uv = uv + uv

tris = []
for y in range(gh - 1):
    for x in range(gw - 1):
        a0, a1, b0, b1 = idx[y, x], idx[y, x + 1], idx[y + 1, x], idx[y + 1, x + 1]
        for t in ((a0, b0, a1), (a1, b0, b1)):
            if min(t) >= 0:
                tris.append(t)                                  # front, counter-clockwise toward +z
                tris.append((t[0] + nf, t[2] + nf, t[1] + nf))  # back, reversed winding
P = np.array(pos, dtype=np.float32)
T = np.array(uv, dtype=np.float32)
I = np.array(tris, dtype=np.uint32)

# Smooth vertex normals.
N = np.zeros_like(P)
fn = np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]])
for k in range(3):
    np.add.at(N, I[:, k], fn)
N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9

# Texture: the cropped Memoji with its alpha channel (alphaMode MASK trims the edge).
tex = img.copy()
buf = io.BytesIO(); tex.save(buf, 'PNG', optimize=True); png = buf.getvalue()

def pad(b, c=b'\x00'):
    return b + c * ((4 - len(b) % 4) % 4)

idx_dtype, comp = (np.uint16, 5123) if len(P) < 65536 else (np.uint32, 5125)
blobs = [P.tobytes(), N.astype(np.float32).tobytes(), T.tobytes(), I.astype(idx_dtype).tobytes(), png]
views, binary = [], b''
for i, bb in enumerate(blobs):
    views.append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(bb)} | ({'target': 34962} if i < 3 else {'target': 34963} if i == 3 else {}))
    binary += pad(bb)
gltf = {
    'asset': {'version': '2.0', 'generator': 'mage build_glb.py'},
    'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0, 'name': 'Mage'}],
    'meshes': [{'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2}, 'indices': 3, 'material': 0}]}],
    'materials': [{'name': 'memoji', 'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}, 'metallicFactor': 0.0, 'roughnessFactor': 0.55},
                   'alphaMode': 'MASK', 'alphaCutoff': 0.5, 'doubleSided': False}],
    'textures': [{'source': 0, 'sampler': 0}], 'samplers': [{'magFilter': 9729, 'minFilter': 9987}],
    'images': [{'bufferView': 4, 'mimeType': 'image/png'}],
    'accessors': [
        {'bufferView': 0, 'componentType': 5126, 'count': len(P), 'type': 'VEC3', 'min': P.min(0).tolist(), 'max': P.max(0).tolist()},
        {'bufferView': 1, 'componentType': 5126, 'count': len(P), 'type': 'VEC3'},
        {'bufferView': 2, 'componentType': 5126, 'count': len(P), 'type': 'VEC2'},
        {'bufferView': 3, 'componentType': comp, 'count': I.size, 'type': 'SCALAR'},
    ],
    'bufferViews': views,
    'buffers': [{'byteLength': len(binary)}],
}
js = pad(json.dumps(gltf, separators=(',', ':')).encode(), b' ')
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binary)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(binary), 0x004E4942) + binary
open(OUT, 'wb').write(glb)
print(f'{len(P)} vertices, {len(I)} triangles, {len(glb) / 1024:.0f} KB')

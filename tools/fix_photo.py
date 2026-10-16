import cv2, numpy as np, sys
src, out, prev = sys.argv[1], sys.argv[2], sys.argv[3]
im = cv2.imread(src); H, W = im.shape[:2]
f = im.astype(np.float32)
V = f.max(axis=2)

def rotate(img, ang, size=None):
    h, w = img.shape[:2]
    if size is None:  # rotate into a canvas big enough
        c, s = abs(np.cos(np.radians(ang))), abs(np.sin(np.radians(ang)))
        nw, nh = int(w * c + h * s) + 2, int(w * s + h * c) + 2
    else:
        nw, nh = size
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1)
    M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), M

def streak_layer(V, ang):
    # rotate so the streak direction becomes horizontal
    R, M = rotate(V, ang)
    vert = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 121))
    G = R - cv2.morphologyEx(R, cv2.MORPH_OPEN, vert)          # thin bright structures (streaks + text)
    horiz = cv2.getStructuringElement(cv2.MORPH_RECT, (281, 1))
    Sx = cv2.morphologyEx(G, cv2.MORPH_OPEN, horiz)             # keep only long ones along the streak
    Sx = cv2.GaussianBlur(Sx, (0, 0), 6)
    Mi = cv2.invertAffineTransform(M)
    return cv2.warpAffine(Sx, Mi, (W, H), flags=cv2.INTER_LINEAR)

# streak directions measured with Hough: about -27 deg and -17 deg (rising to the right)
S = np.maximum(streak_layer(V, -27), streak_layer(V, -17))
# protect people / floor: fade the correction out below the banner header
yy = np.linspace(0, 1, H)[:, None]
fade = np.clip((0.62 - yy) / 0.12, 0, 1)
S = S * fade
corr = np.clip(f - 1.15 * S[..., None], 0, 255)

# level (clockwise 0.9 deg, measured on the LED pillars) and crop the border
ang = -0.9
M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1)
J = cv2.warpAffine(corr.astype(np.uint8), M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
c = int(np.ceil(np.tan(np.radians(abs(ang))) * max(W, H))) + 2
J = J[c:H - c, c:W - c]
cv2.imwrite(out, J, [cv2.IMWRITE_JPEG_QUALITY, 93])
a = cv2.resize(im, (600, 800)); b = cv2.resize(J, (600, 800))
cv2.imwrite(prev, np.hstack([a, b]))
print('saved', J.shape, 'max streak', S.max())

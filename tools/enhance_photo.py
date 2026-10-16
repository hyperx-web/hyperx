import cv2, numpy as np, sys
src, out, prev = sys.argv[1], sys.argv[2], sys.argv[3]
orig = cv2.imread(src)
im = cv2.fastNlMeansDenoisingColored(orig, None, 2, 2, 7, 21)       # light: only messenger JPEG noise
f = im.astype(np.float32)

# veil removal with ONE black/white point for all channels (keeps white balance)
Y = f.mean(axis=2)
lo, hi = np.percentile(Y, 0.8), np.percentile(Y, 99.8)
f = np.clip((f - lo) / (hi - lo) * 255, 0, 255)

# global S-curve on luminance (smooth, no blotches) – adds the contrast the haze took away
lab = cv2.cvtColor(f.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
x = lab[:, :, 0] / 255.0
k = 0.35
s = x + k * x * (1 - x) * (2 * x - 1) * 2          # gentle S around mid-grey
lab[:, :, 0] = np.clip((s ** 1.04) * 255, 0, 255)
# slight chroma boost (a,b channels around 128)
lab[:, :, 1:] = np.clip((lab[:, :, 1:] - 128) * 1.08 + 128, 0, 255)
im = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

# upscale x1.5 + edge-aware sharpening (unsharp on L, small radius)
h, w = im.shape[:2]
im = cv2.resize(im, (int(w * 1.5), int(h * 1.5)), interpolation=cv2.INTER_LANCZOS4)
lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
L = lab[:, :, 0]
detail = L - cv2.GaussianBlur(L, (0, 0), 1.2)
edge = cv2.GaussianBlur(np.abs(cv2.Laplacian(L, cv2.CV_32F)), (0, 0), 2)
wgt = np.clip(edge / 12.0, 0, 1)                  # sharpen edges, leave flat areas smooth
lab[:, :, 0] = np.clip(L + 1.0 * wgt * detail, 0, 255)
im = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
cv2.imwrite(out, im, [cv2.IMWRITE_JPEG_QUALITY, 94])

a = cv2.resize(orig, (600, 800)); b = cv2.resize(im, (600, 800))
cv2.imwrite(prev, np.hstack([a, b]))
y0, x0 = int(im.shape[0] * 0.33), int(im.shape[1] * 0.12)
cv2.imwrite(prev.replace('.jpg', '_crop.jpg'), im[y0:y0 + 500, x0:x0 + 1100])
print('saved', im.shape)

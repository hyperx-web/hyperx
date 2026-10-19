function frames_to_mp4(frameDir, outFile, fps)
% Turn a folder of PNG frames (0000.png, 0001.png, ...) into an H.264 MP4 (PowerPoint-compatible).
% Transparent pixels are flattened onto white; sizes are rounded to even numbers for H.264.
%   matlab -batch "addpath('tools'); frames_to_mp4('rec/sat-beams','sat-beams.mp4',20)"
if nargin < 3, fps = 20; end
f = dir(fullfile(frameDir, '*.png'));
[~, idx] = sort({f.name}); f = f(idx);
v = VideoWriter(outFile, 'MPEG-4');
v.FrameRate = fps; v.Quality = 95;
open(v);
for k = 1:numel(f)
    [img, ~, a] = imread(fullfile(frameDir, f(k).name));
    img = double(img) / 255;
    if size(img, 3) == 1, img = repmat(img, 1, 1, 3); end
    if ~isempty(a)
        a = double(a) / 255;
        img = img .* a + (1 - a);          % composite over white
    end
    h = size(img, 1) - mod(size(img, 1), 2); w = size(img, 2) - mod(size(img, 2), 2);
    writeVideo(v, uint8(round(255 * img(1:h, 1:w, :))));
end
close(v);
fprintf('%s: %d frames\n', outFile, numel(f));
end

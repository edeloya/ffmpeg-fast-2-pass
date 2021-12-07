# ffmpeg-fast-2-pass
I wrote this script trying to speed up my rendering workflow by 1 encode.

I used to do an initial CRF encode for sampling and then a 2-pass with those results, meaning I encoded the total media runtime 3 times.

Here we just do sampling using the X topmost minutes with highest bitrate, cutting down full renders to 2x (+X min) runtime encoding.

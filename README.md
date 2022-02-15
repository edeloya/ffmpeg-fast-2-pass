# ffmpeg-fast-2-pass
I wrote this script trying to speed up my rendering workflow by 1 encode.

I used to do an initial CRF encode for sampling and then a 2-pass with those results, meaning I encoded the total media runtime 3 times.

Here we do sampling by remuxing (copying) the original video into ~1 second slices on keyframes to get an appropriate ceiling for the otherwise blind 2-pass target bitrate.

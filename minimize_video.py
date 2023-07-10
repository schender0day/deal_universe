import os
from moviepy.editor import VideoFileClip


def compress_video(video_path, output_path, target_size):
    # Parameter video_path is the path to the input video
    # Parameter output_path is the path to save the compressed video
    # Parameter target_size is the target size in MB

    clip = VideoFileClip(video_path)

    # Reduce the audio bitrate to minimize the size of the output video
    audio_bitrate = "32k"

    # Calculate the target bitrate in kbps based on target size
    target_bitrate = (target_size * 1024 * 8) / clip.duration

    # Write the output file
    clip.write_videofile(output_path, audio_bitrate=audio_bitrate, bitrate=str(target_bitrate) + "k")


def main():
    directory_path = '/path/to/your/directory'  # replace with your directory
    target_size = 32  # size in MB

    for filename in os.listdir(directory_path):
        if filename.endswith(".mp4"):
            video_path = os.path.join(directory_path, filename)
            file_size_MB = os.path.getsize(video_path) / (1024 * 1024)

            if file_size_MB > target_size:
                output_path = os.path.join(directory_path, "compressed_" + filename)
                compress_video(video_path, output_path, target_size)

                print(f'Compressed file {filename} and saved to {output_path}')
            else:
                print(f'Skipped file {filename} as it is smaller than target size')


if __name__ == '__main__':
    main()

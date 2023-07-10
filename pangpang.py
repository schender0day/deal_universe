import boto3
import time
from contextlib import closing
from pydub import AudioSegment
from pydub.playback import play

# Initialize polly client
polly_client = boto3.client('polly', "us-east-1")

while True:
    # Text to be converted to speech
    response = polly_client.synthesize_speech(VoiceId='Zhiyu',
                OutputFormat='mp3',
                Text = '胖胖吃一口饭, 喝一口死木西'
                       '')

    # Save the audio to a file
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = "OutputFilePath.mp3"
            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as ioe:
                print(ioe)
                sys.exit(-1)

    # Play the audio file
    song = AudioSegment.from_mp3(output)
    play(song)

    # Delay for 30 seconds
    time.sleep(30)

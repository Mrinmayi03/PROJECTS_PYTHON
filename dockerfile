#base python environment
FROM python:3.11

WORKDIR /app/project/Milestone5

#for opencv and whisper
RUN apt-get update && apt-get install -y python3-opencv
RUN apt-get update && apt-get install -y ffmpeg

#copy and install requirments
COPY requirements.txt .
RUN pip install -r requirements.txt

#copy python script
COPY milestone5.py .

#to save file and get input
RUN mkdir "ground_truth" "translated_video" "translated_audio_file_french" "translated_subtitle_file"

#set default command to run when container starts
CMD [ "python", "milestone5.py" ]

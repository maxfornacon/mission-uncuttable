import os
import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from moviepy.editor import VideoFileClip
from model.data import VisualiserVideo
from model.data import BoardVideo
from model.data import Audio


class VideoSplitter:
    """
    This class handles the video and audio splitting
    """

    def __init__(self, folder_path, folder_name, video_data):
        """
        Constructor of the class
        @param folder_path: the path to the project folder
        @param folder_name: the name of the project folder
        @param video_data: the path of the video file
        """

        self.folder_path = folder_path
        self.folder_name = folder_name
        self.video_data = video_data
        self.files = []
        self.audio_files = []

    def large_video_cut(self, fps):
        """
        a method to get the part of the speaker from the "main video" and save it in the project folder
        and create a object of this
        """
        folder = Path(self.folder_path, self.folder_name)

        cap = cv2.VideoCapture(self.video_data)

        large_video_name = 'large_video.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(os.path.join(folder,str(large_video_name)), fourcc , fps, (938, 530))

        if(cap.isOpened() == False):
            print("Error opening video stream or file")

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                frame = frame[275:805, 17:955]
                out.write(frame)

            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        new_large_video_path = Path(folder, large_video_name)
        self.files.append(new_large_video_path)
        return BoardVideo(new_large_video_path)

    def small_video_cut(self, fps):
        """
        a method to get the part of the foil/visualiser from the "main video" and save it in the project folder
        and create a object of this
        """
        folder = Path(self.folder_path, self.folder_name)

        cap = cv2.VideoCapture(self.video_data)

        small_video_name = 'small_video.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(os.path.join(folder,str(small_video_name)), fourcc , fps, (700, 530))

        if(cap.isOpened() == False):
            print("Error opening video stream or file")

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                frame = frame[275:805, 1080:1780]
                out.write(frame)

            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        new_small_video_path = Path(folder, small_video_name)
        self.files.append(new_small_video_path)
        return VisualiserVideo(new_small_video_path)

    def audio_from_video_cut(self):
        """
        a method to get the audio from a video and save it in the project folder
        and create a object of this
        """

        folder = Path(self.folder_path, self.folder_name)

        audio_from_video = 'audio.mp3'
        video = VideoFileClip(self.video_data)
        audio = video.audio
        audio.write_audiofile(os.path.join(folder, audio_from_video))
        extracted_audio = Path(folder, audio_from_video)
        self.audio_files.append(extracted_audio)
        return Audio(extracted_audio)

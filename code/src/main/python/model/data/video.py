from .media_file import MediaFile

class Video(MediaFile):
    """
    This class contains the video
    """

    def __init__(self, file_path): 
        self.__file_path = file_path

    def get(self):
        return self.__file_path
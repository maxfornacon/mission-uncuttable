from .media_file import MediaFile

class Audio(MediaFile):
    """
    This class contains the audiotrack of the video
    """

    def __init__(self, file_path):
        self.__file_path = str(file_path)

    def get(self):
        return self.__file_path

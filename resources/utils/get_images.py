import os


from .get_app_dir import getAppDirectory


def getImages(filename):
    return os.path.join(getAppDirectory(), "resources", "Images", filename)
# def getImages(filename: str):
#     filename = filename.replace(".", "_").split("/")[1]
#     return getImage(filename)
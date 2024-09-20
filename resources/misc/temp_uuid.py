import os
import uuid


from ..utils.get_app_dir import getAppDirectory

app_dir = getAppDirectory()


def generateUniqueUID() -> str:
    """
    Generates a new UUID each call
    """
    return str(uuid.uuid4())


def isUUID(value):
    # Check if the value is a string
    if isinstance(value, str):
        try:
            # Attempt to create a UUID object from the string
            val = uuid.UUID(value)
            # Check if the UUID version is 4
            return val.version == 4
        except ValueError:
            return False
    return False


def createNewUUID() -> None:
    """
    Gets the new UUID and save it into the "UUID" file
    """

    if not os.path.exists(os.path.join(app_dir, "UUID")):
        with open(os.path.join(app_dir, "UUID"), "w") as uuid:
            uuid.write(generateUniqueUID())
            uuid.close()
    else:
        with open(os.path.join(app_dir, "UUID"), "r+") as uuid:
            if not isUUID(uuid.read()):
                uuid.seek(0)
                uuid.truncate()
                uuid.write(generateUniqueUID())


def getUUID() -> str:
    """
    Gets the content of the file "UUID"
    """
    with open(os.path.join(app_dir, "UUID"), "r") as uuid:
        uuid_content = uuid.read()
        return uuid_content

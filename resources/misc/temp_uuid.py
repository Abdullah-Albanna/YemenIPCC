import uuid


from utils.get_app_dir import getAppDirectory

uuid_path = getAppDirectory() / "UUID"


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
    uuid_path.write_text(generateUniqueUID()) if not uuid_path.exists() else ""

    with open(uuid_path, "r+") as uuid:
        if not isUUID(uuid.read()):
            uuid.seek(0)
            uuid.truncate()
            uuid.write(generateUniqueUID())


def getUUID() -> str:
    """
    Gets the content of the file "UUID"
    """
    return uuid_path.read_text()

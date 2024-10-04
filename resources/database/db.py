import json
from tinydb import JSONStorage, TinyDB, where


from utils.get_app_dir import getExecutablePath


class IndentedJSONStorage(JSONStorage):
    def write(self, data):
        # Writes the data to the file in a pretty-printed format with indentation
        with open(self._handle.name, "w") as f:
            json.dump(data, f, indent=4)

    def read(self):
        try:
            # Reads the data from the file
            with open(self._handle.name, "r") as f:
                return json.load(f)
        except (IOError, ValueError):
            # Return an empty dictionary if the file doesn't exist or contains invalid JSON
            return {}


app_dir = getExecutablePath()

# if app_dir.parts[-1].isdigit():
#     app_dir =Path.cwd()

db_file_path = app_dir / "settings.json"

db = TinyDB(db_file_path, storage=IndentedJSONStorage)


class DataBase:
    @staticmethod
    def add(keys: list, values: list, table="default") -> None:
        table = db.table(table)

        for key, value in zip(keys, values):
            if not table.search(where(key).exists()):
                table.insert({key: value})

            elif table.search(where(key) == value):
                continue

            else:
                table.update({key: value}, where(key).exists())

    @staticmethod
    def get(keys: list, defaults: list, table="default") -> list:
        table = db.table(table)

        values = []

        for key, default in zip(keys, defaults):
            result = table.get(where(key).exists())

            if result and key in result:
                values.append(result[key])
            else:
                values.append(default)

        return list(values)

    @staticmethod
    def delete(keys: list, table="default"):
        table = db.table(table)

        for key in keys:
            if not table.get(where(key).exists()):
                continue

            table.remove(where(key).exists())

    @staticmethod
    def addOnce(keys: list, values: list, table="default"):
        table = db.table(table)

        for key, value in zip(keys, values):
            if table.get(where(key).exists()):
                continue

            table.insert({key: value})

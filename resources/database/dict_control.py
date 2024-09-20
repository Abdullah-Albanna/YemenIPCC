class DictControl:
    __main_dict = {}

    def shouldRun(self, identifier):
        if identifier not in self.__main_dict:
            self.__main_dict[identifier] = True
            return True
        else:
            if not self.__main_dict[identifier]:
                self.__main_dict[identifier] = True
                return True

        return False

    def runTwice(self, identifier):
        if identifier not in self.__main_dict:
            self.__main_dict[identifier] = 1
            return True
        else:
            if self.__main_dict[identifier] == 1:
                self.__main_dict[identifier] = 2
                return True
            else:
                return False

    def runAgain(self, identifier):
        self.__main_dict[identifier] = False

    def noRunAgain(self, identifier):
        self.__main_dict[identifier] = True

    def get(self, identifier, num=None):
        if identifier in self.__main_dict:
            return self.__main_dict[identifier]
        else:
            if num:
                return 0
            return None

    def write(self, identifier, content):
        self.__main_dict[identifier] = content

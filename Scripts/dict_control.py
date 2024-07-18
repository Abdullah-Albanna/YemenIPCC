
class DictControl:
    main_dict = {}

    def shouldRun(self, identifier):
        if identifier not in self.main_dict:
            self.main_dict[identifier] = True
            return True
        else:
            if not self.main_dict[identifier]:
                self.main_dict[identifier] = True
                return True
            else:
                return False
            
    def runTwice(self, identifier):
        if identifier not in self.main_dict:
            self.main_dict[identifier] = 1
            return True
        else:
            if self.main_dict[identifier] == 1:
                self.main_dict[identifier] = 2
                return True
            else:
                return False
        
    def runAgain(self, identifier):
        self.main_dict[identifier] = False
    
    def noRunAgain(self, identifier):
        self.main_dict[identifier] = True
    
    def get(self, identifier, num=None):
        if identifier in self.main_dict:
            return self.main_dict[identifier]
        else:
            if num:
                return 0
            return None
    
    def write(self, identifier, content):
        self.main_dict[identifier] = content
import json

class Botjson:
    def __init__(self):
        self.Value = {}

    def Load(self):
        try:
            with open("Bot.json", "r") as f:
                self.Value = json.load(f)
        except FileNotFoundError:
            pass

    def Save(self):
        with open("Bot.json", "w") as f:
            dumped = json.dumps(self.Value, indent=4)  # Hier wird das Argument 'indent' verwendet
            f.write(dumped)
class PermissionSystem:
    def __init__(self):
        self.name = "PermissionSystem:1.0"
        self.version = "1.0"
        self.permissionArray = {}
        self.PermissionLength = 0
    def checkperms(self, UserID, PermissionNumber):
        PermList = []
        PermListCount = 0
        for i in self.permissionArray[UserID]:
            PermList.append(i)
            PermlistCount += 1
        ZerosToAdd = PermListCount - self.PermissionLength
        for i in range(ZerosToAdd):
            PermList.append(0)
        PermissionString = ""
        for i in PermList:
            PermissionString += i
        self.permissionArray[UserID] = PermissionString
        if PermList[PermissionNumber] == 1:
            return True
        else:
            return False
        

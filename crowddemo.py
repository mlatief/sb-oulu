import random
# import SmartBody
from SmartBody import SBScript, SBEventHandler, SrVec


def vec2str(vec):
    ''' Converts SrVec to string '''
    x = vec.getData(0)
    y = vec.getData(1)
    z = vec.getData(2)
    if -0.0001 < x < 0.0001:
        x = 0
    if -0.0001 < y < 0.0001:
        y = 0
    if -0.0001 < z < 0.0001:
        z = 0
    return "" + str(x) + " " + str(y) + ""


class CrowdDemo(SBScript):
    def __init__(self, scene):
        print(">>> Initializing CrowdDemo script...")
        # Paths for characters
        self.bradCur = 0
        self.bradReached = True
        self.scene = scene
        self.bml = self.scene.getBmlProcessor()

        SBScript.__init__(self)

    def update(self, time):
        # global bradReached, bradCur
        # Once utah completes path, do again

        print(">>> Call to CrowdDemo script update...")
        bradPath = [SrVec(-8, -8, 0), SrVec(8, 8, 0), SrVec(8, -8, 0), SrVec(-8, 8, 0)]
        pathAmt = len(bradPath)

        bradList = []
        for name in self.scene.getCharacterNames():
            if 'ChrBrad' in name:
                bradList.append(self.scene.getCharacter(name))

        if self.bradReached:
            print(">>> Updating Brads positions...")
            for brad in bradList:
                # print "Moving Brad " + brad.getName()
                # Move character
                # print  '<locomotion speed="' +  str(random.uniform(1.20, 5.0)) + '" target="' +\
                                            # vec2str(bradPath[bradCur]) + '"/>'
                self.bml.execBML(brad.getName(), '<locomotion speed="' +
                                 str(random.uniform(1.20, 5.0)) +
                                 '" target="' +
                                 vec2str(bradPath[self.bradCur]) + '"/>')

            self.bradCur = self.bradCur + 1
            # If reaches max path, reset
            if self.bradCur >= pathAmt:
                self.bradCur = 0
            self.bradReached = False
            print(">>> Sent locomotion BML to 20 Brads, watch them freaking out!")



# Locomotion handler to check if characters have arrived
class LocomotionHandler(SBEventHandler):
    def __init__(self, cd):
        print(">>> Initializing LocomotionHandler...")
        self.crowdDemo = cd
        self.reachCount = 0
        print(">>> CrowdDemo object: cd.bradCur=" + str(cd.bradCur))
        SBEventHandler.__init__(self)

    def executeAction(self, ev):
        # global bradReached, reachCount
        print(">>> LocomotionHandler.executeAction")
        params = ev.getParameters()
        if 'success' in params:
            if 'ChrBrad' in params:
                self.reachCount = self.reachCount + 1
                if self.reachCount >= 6:
                    # self.crowdDemo.bradReached = True
                    self.reachCount = 0


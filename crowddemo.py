import random
import SmartBody
from SmartBody import SBScript, SBEventHandler, SrVec

def vec2str(vec):
    ''' Converts SrVec to string '''
    x = vec.getData(0)
    y = vec.getData(1)
    z = vec.getData(2)
    if -0.0001 < x < 0.0001: x = 0
    if -0.0001 < y < 0.0001: y = 0
    if -0.0001 < z < 0.0001: z = 0
    return "" + str(x) + " " + str(y) + ""

class CrowdDemo(SBScript):
    def __init__(self, scene):
        # Paths for characters
        self.bradPath = [SrVec(-8, -8, 0), SrVec(8, 8, 0), SrVec(8, -8, 0), SrVec(-8, 8, 0)]
        self.bradCur = 0
        self.pathAmt = len(self.bradPath)
        self.bradReached = True
        self.scene = scene
    
        self.bradList = []
        for name in scene.getCharacterNames():
            if 'ChrBrad' in name:
                self.bradList.append(scene.getCharacter(name))
    
        SBScript.__init__ (self)


    def update(self, time):
        #global bradReached, bradCur
        # Once utah completes path, do again
        print "CrowdDemo Update .."
        if self.bradReached:
            for brad in self.bradList:
                #print "Moving Brad " + brad.getName()
                # Move character
                #print  '<locomotion speed="' +  str(random.uniform(1.20, 5.0)) + '" target="' +\
                                            #vec2str(bradPath[bradCur]) + '"/>'
                self.bml.execBML(brad.getName(), '<locomotion speed="' +  str(random.uniform(1.20, 5.0)) + '" target="' +\
                                            vec2str(self.bradPath[self.bradCur]) + '"/>')
            self.bradCur = self.bradCur + 1
            # If reaches max path, reset
            if self.bradCur >= self.pathAmt:
                self.bradCur = 0
            self.bradReached = False



# Locomotion handler to check if characters have arrived
class LocomotionHandler(SBEventHandler):
    def __init__(self, cd):
        self.crowdDemo = cd
        self.reachCount = 0
        SBEventHandler.__init__(self)

    def executeAction(self, ev):
        #global bradReached, reachCount
        params = ev.getParameters()
        if 'success' in params:
            if 'ChrBrad' in params:
                self.reachCount = self.reachCount + 1
                if self.reachCount >= 6:
                    self.crowdDemo.bradReached = True  
                    self.reachCount = 0
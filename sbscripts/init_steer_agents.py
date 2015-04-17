print "Init Steer Agent"
def setupSteerAgent(scene, charName, prefix):
	steerManager = scene.getSteerManager()
	steerManager.removeSteerAgent(charName)
	steerAgent = steerManager.createSteerAgent(charName)
	steerAgent.setSteerStateNamePrefix(prefix)
	steerAgent.setSteerType("example")
	sbCharacter = scene.getCharacter(charName)
	



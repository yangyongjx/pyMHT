import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
import matplotlib.pyplot as plt
import numpy as np
import pulp
import tomht
from tomht.classDefinitions import Position
import tomht.radarSimulator as sim
import tomht.helpFunctions as hpf
from tomht.stateSpace.pv import*

def runSimulation():
	seed = 5446
	nTargets = 4
	p0 = Position(1,1)
	radarRange = 10.0 #meters
	maxSpeed = 2 #meters/second
	initialTargets = sim.generateInitialTargets(seed,nTargets,p0, radarRange, maxSpeed)
	initialTargets[3].state[3] 		*= -1
	initialTargets[3].state[2:4] 	*= 0.3
	initialTargets[1].state[2:4] 	*= 1.5
	initialTargets[1].state[2] 		*= -1.5
	initialTargets[1].state[2:4] 	*= 1.05
	print("Initial targets:")
	print(*initialTargets, sep='\n', end = "\n\n")

	nScans = 6
	timeStep = 1.0
	lambda_phi 	= 2e-4					#Expected number of false measurements per unit 
										# volume of the measurement space per scan
	lambda_nu 	= 0.0001				#Expected number of new targets per unit volume 
										# of the measurement space per scan
	P_d 		= 0.8					#Probability of detection
	sigma 		= 3						#Need to be changed to conficence
	N 		 	= 5						#Number of  timesteps to tail (N-scan)
	# solver  	= pulp.CPLEX_CMD(None, 0,1,0,[],0.05)
	# solver  	= pulp.GLPK_CMD(None, 0,1,0,[])
	# solver  	= pulp.PULP_CBC_CMD()
	# solver  	= pulp.SYMPHONY()		#Not implementet in PuLP yet
	# solver  	= pulp.GUROBI_CMD(None, 0,1,0,[])
	# solver  	= pulp.XPRESS()			#Need licence

	simList = sim.simulateTargets(seed, initialTargets, nScans, timeStep, Phi(timeStep), Q(timeStep), Gamma)

	print("Sim list:")
	print(*simList, sep = "\n", end = "\n\n")

	scanList = sim.simulateScans(seed, simList, C, R, False, lambda_phi,radarRange, p0)
	#solvers: CPLEX, GLPK, CBC, GUROBI
	tracker = tomht.Tracker(Phi, C, Gamma, P_d, P0, R, Q, lambda_phi, lambda_nu, sigma, N, "GLPK", logTime = True)

	# print("Scan list:")
	# print(*scanList, sep = "\n", end = "\n\n")

	for initialTarget in initialTargets:
	 	tracker.initiateTarget(initialTarget)
	 	# target.plotInitial(len(self.__targetList__)-1)

	for scanIndex, measurementList in enumerate(scanList):
		# print("#"*150)
		tracker.addMeasurementList(measurementList)
	print("#"*150)


	# hpf.printTargetList(tracker.__targetList__)
	association = hpf.backtrackMeasurementsIndices(tracker.__trackNodes__)
	print("Association",*association, sep = "\n")

	fig1 = plt.figure(num=1, figsize = (9,9), dpi=100)
	# hpf.plotRadarOutline(p0, radarRange)
	# hpf.plotVelocityArrowFromNode(tracker.__trackNodes__,2)
	# hpf.plotValidationRegionFromNodes(tracker.__trackNodes__,sigma, 1)
	# hpf.plotValidationRegionFromForest(tracker.__targetList__, sigma, 1)
	# hpf.plotMeasurementsFromForest(tracker.__targetList__, real = True, dummy = True)
	# hpf.plotMeasurementsFromList(tracker.__scanHistory__)
	# hpf.plotMeasurementsFromNodes(trackNodes)
	hpf.plotHypothesesTrack(tracker.__targetList__)
	hpf.plotActiveTrack(tracker.__trackNodes__)
	# plt.axis("equal")
	plt.xlim((p0.x-radarRange*1.05, p0.x + radarRange*1.05))
	plt.ylim((p0.y-radarRange*1.05, p0.y + radarRange*1.05))
	plt.show()

if __name__ == '__main__':
	runSimulation()
	print("Done :)")

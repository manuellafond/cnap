import random
import sys

from node import Node
from cnvprofiler import CNVProfiler

mode = "cnvdist"

prune_zeros_of_first_sequence = False

simulation_params = "10,5,5,0.5,4,2"

cnv1 = ""
cnv2 = ""

cnvfile = ""
outfile = ""

for arg in sys.argv[1:]:
	if arg.startswith("--mode="):
		mode = arg.split("=")[1]
	elif arg.startswith("--prunezeros"):
		prune_zeros_of_first_sequence = True
	elif arg.startswith("--simparams="):
		simulation_params = arg.split("=")[1]
	elif arg.startswith("--cnv1="):
		cnv1 = arg.split("=")[1]
	elif arg.startswith("--cnv2="):
		cnv2 = arg.split("=")[1]
	elif arg.startswith("--cnvfile="):
		cnvfile = arg.split("=")[1]
	elif arg.startswith("--outfile="):
		outfile = arg.split("=")[1]

		
if mode == "simulate_tree":
	sim_p = simulation_params.split(",")
	profile_length = int(sim_p[0])
	nb_leaves = int(sim_p[1])
	max_events_on_branch = int(sim_p[2])
	prob_deletion = float(sim_p[3])

	root_profile_startvals = int(sim_p[4])
	root_profile_max_delta = int(sim_p[5])

	root_profile = [4] * profile_length
	for i in range(profile_length):
		delta = random.randint(-root_profile_max_delta, root_profile_max_delta)
		root_profile[i] = max(1, root_profile[i] + delta)

	tree = Node.get_random_binary_tree(nb_leaves)

	nodes = tree.get_preorder_nodes()


	for n in nodes:
		if n == tree:
			n.params["cnvprofile"] = root_profile
			n.label = '-'.join([str(i) for i in root_profile])
		else:
		
			curprofile = list(n.parent.params["cnvprofile"])
			#generate random events on the branch from parent to n
			nb_events = random.randint(0, max_events_on_branch)
			
			for i in range(nb_events):
				r = random.uniform(0,1)
				
				#b represents amplification or deletion
				b = 1
				if r <= prob_deletion:
					b = -1
					
				#pick random range [s,t]
				s = random.randint(0, profile_length - 1)
				t = random.randint(0, profile_length - 2)
				
				if t >= s:
					t = t + 1
				else:	#swap
					tmp = s
					s = t
					t = tmp
					
				for j in range(s, t + 1):
					if curprofile[j] > 0:
						curprofile[j] = curprofile[j] + b
		
			n.params["cnvprofile"] = curprofile
			
			if n.label != "":
				n.label += "__"
			
			n.label += '-'.join([str(i) for i in curprofile])
			
			
	outstr = ""
	
	
	outstr += "<TREE>\n"
	outstr += tree.to_newick(split_label = '__', split_label_index = 0, write_internal_labels = False) + ";"
	outstr += "\n</TREE>\n"
	
	outstr += "<TREE_FULL>\n"
	outstr += tree.to_newick() + ";"
	outstr += "\n</TREE_FULL>\n"
	
	
	

	outstr += "<CLADES>\n"
	for n in tree.get_preorder_nodes():
		outstr += ','.join([l.label.split("__")[0] for l in n.get_leaves()]) + "\n"
	outstr += "</CLADES>\n"
	
	

	outstr += "<LEAVES>\n"
	for l in tree.get_leaves():
		outstr += ">" + l.label.split("__")[0] + "\n"
		outstr += ','.join([str(i) for i in l.params["cnvprofile"]]) + "\n"
	outstr += "</LEAVES>\n"

	print(outstr)
	
elif mode == "cnvdist":
	
	
	if cnv1 == "" or cnv2 == "":
		print("Please specify two CNV profiles with --cnv1 and --cnv2")
		sys.exit()
		
	profile1 = [int(x) for x in cnv1.split(",")]
	profile2 = [int(x) for x in cnv2.split(",")]
	
	if len(profile1) != len(profile2):
		print("Error: the two profiles do not have the same length")
		sys.exit()
		
	

	cost = CNVProfiler.get_distance(profile1, profile2, prune_zeros_of_first_sequence)
	
	print(cost)

	
elif mode == "pairwise_dists" or mdoe == "pairwise_distances":
	
	if cnvfile == "":
		print("Specify a cnv file in fasta format with --cnvfile")
		sys.exit()
		
	f = open(cnvfile, 'r')
	curname = ""
	curstr = ""
	
	profilenames = []
	profiles = {}
	for line in f:
		line = line.replace("\n", "").replace("\r", "")
		
		if line.startswith(">"):
			curname = line.replace(">", "")
			profiles[curname] = ""
			profilenames.append(curname)
		else:
			if curname != "":
				profiles[curname] += line

	
	s =	len(profilenames)
	profiledistances = []
	for i in range(s):
		
		prof_i = [int(x) for x in profiles[profilenames[i]].split(",")]
		profiledistances.append([0] * s)
		for j in range(i + 1, s):
			
			prof_j = [int(x) for x in profiles[profilenames[j]].split(",")]
			dist1 = CNVProfiler.get_distance(prof_i, prof_j, True)
			dist2 = CNVProfiler.get_distance(prof_j, prof_i, True)
			profiledistances[i][j] = max(dist1, dist2)

	outstr = str(s) + "\n"
	
	for i in reversed(range(s)):
		outstr += profilenames[i].ljust(10)
		if i < s - 1:
			outstr
		for j in reversed(range(i + 1, s)):
			outstr += " " + str(profiledistances[i][j]) + " "
		if i > 0:
			outstr += "\n"

	if outfile != "":
		fo = open(outfile, 'w')
		fo.write(outstr)
		fo.close()
	else:
		print(outstr)


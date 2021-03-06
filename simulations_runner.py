import sys
import os
from os.path import join
import os,subprocess
from shutil import copyfile
import time


work_dir = "./simulations"
nb_runs = 10


run_medicc = False
run_euclid = False


for arg in sys.argv[1:]:
	if arg.startswith("--medicc"):
		run_medicc = True
	if arg.startswith("--euclidean"):
		run_euclid = True


#param string format
#prof_len,nb_leaves,max_events_on_branch,prob_deletion,root_profile_startvals,root_profile_max_delta

param_sets = []

#small
param_sets.append("10,5,5,0.5,3,2")
'''
param_sets.append("10,5,5,0.25,3,2")
param_sets.append("10,5,5,0.75,3,2")

#smallish
param_sets.append("20,10,8,0.5,4,2")
param_sets.append("20,10,8,0.25,4,2")
param_sets.append("20,10,8,0.75,4,2")


#medium
param_sets.append("30,20,10,0.5,5,3")
param_sets.append("30,20,10,0.25,5,3")
param_sets.append("30,20,10,0.75,5,3")
'''



for p in param_sets:
	for r in range(0, nb_runs):
		
		###############################################
		# simulate tree
		###############################################
		dir = join(work_dir, p.replace(",", "-"))
		if not os.path.exists(dir):
			os.makedirs(dir)
		
		outfile = join(dir, "r" + str(r))
		cmd = "python cnap.py --mode=simulate_tree > " + outfile
		print(cmd)
		os.system(cmd)

		started = False
		started_tree = False
		f = open(outfile, 'r')
		leaves_str = ""
		tree_str = ""
		for line in f:
			line = line.replace("\n", "").replace("\r", "")
			
			if line.startswith("<LEAVES>"):
				started = True
			elif line.startswith("</LEAVES>"):
				started = False
			elif line.startswith("<TREE>"):
				started_tree = True
			elif line.startswith("</TREE>"):
				started_tree = False
			elif started:
				leaves_str += (line + "\n")
			elif started_tree:
				tree_str += line
				
		f.close()
		
		tree_filename = join(dir, "r" + str(r) + "_tree.newick")
		f = open( tree_filename, 'w')
		f.write(tree_str)
		f.close()
		
		###############################################
		# get distances
		###############################################
		tmpdir = join(dir, "tmp")
		if not os.path.exists(tmpdir):
			os.makedirs(tmpdir)
		#empty tmpdir
		for the_file in os.listdir(tmpdir):
			file_path = os.path.join(tmpdir, the_file)
			if os.path.isfile(file_path):
				os.unlink(file_path)
		
		fasta_filename = join(tmpdir, 'tmp.fa')
		f = open(fasta_filename, 'w')
		f.write(leaves_str)
		f.close()
		
		cmd = "python cnap.py --mode=pairwise_dists --cnvfile=" + join(tmpdir, 'tmp.fa') + " --outfile=" + join(tmpdir, "infile")
		print(cmd)
		os.system(cmd)
		
		
		
		###############################################
		# call phylip
		###############################################
		cwd = os.getcwd()
		os.chdir(tmpdir)
		
		#taken from http://telliott99.blogspot.com/2010/03/running-phylip-as-process.html
		
		responses = '.temp.txt'
		FH = open(responses,'w')
		FH.write('L\n')
		FH.write('Y\n')
		FH.close()

		cmd = 'neighbor < ' + responses + ' >  screenout'

		proc = subprocess.Popen(cmd, shell=True)
		pid,ecode = os.waitpid(proc.pid, 0)
		print ecode
		
		os.chdir(cwd)
		
		f = open(join(os.getcwd(), tmpdir, "outtree"))
		for line in f:
			print(line)
			
		tree_phylip_filename = join(dir, "r" + str(r) + "_phylip_tree.newick"  )
		copyfile( join(tmpdir, "outtree"), tree_phylip_filename )
		
		
		###############################################
		# get quartet distance
		###############################################
		
		cmd = "qdist/qdist " + tree_filename + " " + tree_phylip_filename + " > r" + str(r) + ".qtet"
		print(cmd)
		os.system(cmd)
		
		
		###############################################
		# now run medicc on this tree
		###############################################
		if run_medicc:
			medicc_dir = join(dir, "medicc")
			if not os.path.exists(medicc_dir):
				os.makedirs(medicc_dir)
			
			#create a desc file
			descstr = "chrom1 " + fasta_filename + " " + fasta_filename
			descfilename = join(medicc_dir, "desc_r" + str(r) + ".txt")
			f = open(descfilename, 'w')
			f.write(descstr)
			f.close()
			
			medicc_outdir = join(medicc_dir, "r" + str(r) + "_out")
			cmd = "medicc.py " + descfilename + " " + medicc_outdir
			print(cmd)
			os.system(cmd)
			
			medicc_treefile = join(medicc_outdir, "tree_final.new")
			medicc_treefile_local = join(dir, "r" + str(r) + "_medicc_tree.newick")
			copyfile( medicc_treefile, medicc_treefile_local )
			
			cmd = "qdist/qdist " + tree_filename + " " + medicc_treefile_local + " > r" + str(r) + "_medicc.qtet"
			print(cmd)
			os.system(cmd)
		
		###############################################
		# run Euclidean distance with NJ
		###############################################
		if run_euclid:
			pass	#not implemented
		
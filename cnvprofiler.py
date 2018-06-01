import sys

g__debug = False

class CNVProfiler:

	@staticmethod
	def get_distance(base_profile, target_profile, prune_zeros_of_first_sequence = False):
	
		z1 = CNVProfiler.get_zero_intervals(base_profile)
	
		if len(z1) > 0 and not prune_zeros_of_first_sequence:
			print("Error: CNV profile 1 has zeros, which is forbidden.  Add the flag --prunezeros to the command line to remove the positions containing zeros in the two input profiles.")
			sys.exit()
			
		if len(z1) > 0:	#if we get here, we can prune
			base_profile, target_profile = CNVProfiler.remove_zero_intervals(base_profile, target_profile, z1)
	
	
		if g__debug:
			print("Before 0 pruning")
			print("x=" + ','.join([str(i) for i in base_profile]) + "     y=" + ','.join([str(i) for i in target_profile]))
	
	
		intervals = CNVProfiler.get_zero_intervals(target_profile)
		
		cost = CNVProfiler.get_zero_intervals_cost(base_profile, target_profile, intervals)
		
		if g__debug:
			print("zero intervals=" + ' '.join( [str(z[0]) + "," + str(z[1]) for z in intervals]  ))
			print("Cost of zero-pos=" + str(cost))
		
		x, y = CNVProfiler.remove_zero_intervals(base_profile, target_profile, intervals)
		
		
		if g__debug:
			print("---------------")
			print("After 0 pruning")
			print("x=" + ','.join([str(i) for i in x]) + "     y=" + ','.join([str(i) for i in y]))
		
		nsp, costs = CNVProfiler.get_nsp_and_costs_without_zeros(x, y)
		
		for i in range(len(x)):
			cost += costs[i]
			
		return cost


	@staticmethod
	def get_zero_intervals(profile):
		
		intervals = []
		zero_interval_start = -1
		for i in range(len(profile)):
			
			if profile[i] == 0:
				if zero_interval_start == -1:
					zero_interval_start = i
			else:
				if zero_interval_start != -1:
					intervals.append( [zero_interval_start, i - 1] )
					zero_interval_start = -1

		if zero_interval_start != -1:
			intervals.append( [zero_interval_start, len(profile) - 1] )
		return intervals
	
	@staticmethod
	def get_zero_intervals_cost(base_profile, target_profile, intervals):
		
		cost = 0
		for z in intervals:
			m = max(base_profile[z[0]:z[1] + 1])
			
			left = 0
			right = 0
			if z[0] > 0:
				left = max(0, base_profile[z[0] - 1] - target_profile[z[0] - 1])
			if z[1] < len(base_profile) - 1:
				right = max(0, base_profile[z[1] + 1] - target_profile[z[1] + 1])
			mp = max(left, right)

			cost = cost + max(0, m - mp)
		return cost
		
	@staticmethod
	def remove_zero_intervals(base_profile, target_profile, intervals):
		x = list(base_profile)
		y = list(target_profile)
		
		for z in reversed(intervals):
			del x[z[0]: z[1] + 1]
			del y[z[0]: z[1] + 1]
			
			
		return x,y
		
	#Assertion: there are no zero-positions in target_profile
	@staticmethod
	def get_nsp_and_costs_without_zeros(base_profile, target_profile):
		
		n = len(base_profile)
		
		
		
		diff = [base_profile[i] - target_profile[i] for i in range(n)]
		
		
		#first compute left nsp
		left_nsp = [-1] * n
		stack_pos = []	#contains stack of positions
		for i in range(n):
			
			
			if diff[i] >= 0:
				while len(stack_pos) > 0 and diff[stack_pos[-1]] > diff[i]:
					stack_pos.pop()
			else:
				while len(stack_pos) > 0 and diff[stack_pos[-1]] < diff[i]:
					stack_pos.pop()

			if len(stack_pos) == 0:
				left_nsp[i] = -1
			else:
				left_nsp[i] = stack_pos[-1]
				
			stack_pos.append(i)
					
		
		#then right nsp
		right_nsp = [-1] * n
		stack_pos = []	#contains stack of positions
		for i in reversed(range(n)):
			
			
			if diff[i] >= 0:
				while len(stack_pos) > 0 and diff[stack_pos[-1]] >= diff[i]:
					stack_pos.pop()
			else:
				while len(stack_pos) > 0 and diff[stack_pos[-1]] <= diff[i]:
					stack_pos.pop()

			if len(stack_pos) == 0:
				right_nsp[i] = -1
			else:
				right_nsp[i] = stack_pos[-1]

			stack_pos.append(i)
				
		nsp = [-1] * n
		costs = [0] * n
		
		for i in range(n):
			left = 0
			right = 0
			if left_nsp[i] != -1:
				left = diff[left_nsp[i]]
			if right_nsp[i] != -1:
				right = diff[right_nsp[i]]
			
			sgn = 1
			if diff[i] < 0:
				sgn = -1
			

			costleft = diff[i] * sgn - max(0, left * sgn)
			costright = diff[i] * sgn - max(0, right * sgn)
			
			if costright <= costleft:
				costs[i] = costright
				nsp[i] = right_nsp[i]
			else:
				costs[i] = costleft
				nsp[i] = left_nsp[i]
		
		if g__debug:
			print("l=" + ','.join([str(i) for i in left_nsp]))
			print("r=" + ','.join([str(i) for i in right_nsp]))
			print("n=" + ','.join([str(i) for i in nsp]))
			print("c=" + ','.join([str(i) for i in costs]))
			
			
		
		return nsp, costs
		
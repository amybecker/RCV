"""

this tool runs simple instances of rank-choice voting.
votes that exceed the threshold are transfered proportionally to 
their remaining share among votes with same first choice.

The rcv_run function takes as input a list of rankings (first choice to last) 
and percent of voters with that ranking:

[['candidate_1', 'candidate 2', ....], percent with this rank choice], 
	['candidate_2', 'candidate 1', ....], percent with this rank choice],
	...]

e.g.:
	ballot_list = [[['a1','a2','b1'], 0.5],
				[['a1','b1','a2'], .1],
				[['b1','a1'], .4]]


percentages need not sum to one and can optionally be rescaled

rankings need not be complete

"""

import math
import random

def remove_cand(cand, ballot_list):
	for ballot in ballot_list:
		new_ballot = []
		for c in ballot[0]:
			if c!= cand:
				new_ballot.append(c)
		ballot[0] = new_ballot


def replace_cand(cand_rem, cand_add, ballot_list):
	for ballot in ballot_list:
		new_ballot = []
		for c in ballot[0]:
			if c== cand_rem:
				new_ballot.append(cand_add)
			else:
				new_ballot.append(c)
		ballot[0] = new_ballot


def transfer_votes(cand, ballot_list, cutoff):
	winning_ballots = []
	winning_vote_share = 0
	for i in range(len(ballot_list)):
		if len(ballot_list[i][0]) == 0:
			continue
		if ballot_list[i][0][0] == cand:
			winning_ballots.append(i)
			winning_vote_share += ballot_list[i][1]
	for i in range(len(ballot_list)):
		if i in winning_ballots:
			ballot_list[i][1] = ballot_list[i][1] - cutoff*ballot_list[i][1]/winning_vote_share



def rcv_run(ballot_list, num_seats, rescale_bool, verbose_bool):
	#rescale
	rescale_val = 1
	if rescale_bool:
		rescale_val = 0
	for ballot in ballot_list:
		rescale_val += ballot[1]
	if rescale_val == 0:
		print("need to have positive ballot percentages")
	for ballot in ballot_list:
		ballot[1] = ballot[1]/rescale_val

	winners = []
	cutoff = 1.0/(num_seats+1)

	#identify winners
	while len(winners) < num_seats:
		# print(ballot_list)
		# print()
		max_list_len = max(len(ballot[0]) for ballot in ballot_list)
		if max_list_len == 0:
			print("******* ISSUE: threshold not passed *******")
			exit()
		cand_dict = {ballot[0][0]:0 for ballot in ballot_list if len(ballot[0]) > 0}
		for ballot in ballot_list:
			if len(ballot[0]) > 0:
				cand_dict[ballot[0][0]] += ballot[1]
		max_cand = max(cand_dict, key=cand_dict.get)
		min_cand = min(cand_dict, key=cand_dict.get)
		if cand_dict[max_cand] >= cutoff:
			winners.append(max_cand)
			transfer_votes(max_cand, ballot_list, cutoff)
			remove_cand(max_cand, ballot_list)
			if verbose_bool:
				print("candidate", max_cand, "elected")
		elif cand_dict[min_cand] < cutoff:
			remove_cand(min_cand, ballot_list)
			if verbose_bool:
				print("candidate", min_cand, "eliminated")
		else:
			print("******* ISSUE: input error *******")
			break
	return winners



############## build scenarios ###############


def polarized_generator(num_seats, i, perm_white, perm_minority):
	if i in {1,2,3}:
		if perm_minority and perm_white:
			return random.sample(minority_cands[:num_seats],num_seats) + random.sample(white_cands[:num_seats],num_seats)
		if perm_minority and not perm_white:
			return random.sample(minority_cands[:num_seats],num_seats) + white_cands[:num_seats]
		if not perm_minority and  perm_white:
			return minority_cands[:num_seats] + random.sample(white_cands[:num_seats],num_seats)
		if not perm_minority and not perm_white:
			return minority_cands[:num_seats] + white_cands[:num_seats]	
	elif i == 0:
		if perm_minority and perm_white:
			return random.sample(white_cands[:num_seats],num_seats) + random.sample(minority_cands[:num_seats],num_seats)
		if perm_minority and not perm_white:
			return white_cands[:num_seats] + random.sample(minority_cands[:num_seats],num_seats)
		if not perm_minority and  perm_white:
			return random.sample(white_cands[:num_seats],num_seats) + minority_cands[:num_seats]
		if not perm_minority and not perm_white:
			return white_cands[:num_seats] + minority_cands[:num_seats]	


def interweave(listA, listB):
	assert(len(listA) == len(listB))
	new_list = []
	for i in range(len(listA)):
		new_list.append(listA[i])
		new_list.append(listB[i])
	return new_list


def crossover_generator(num_seats, i, perm_white, perm_minority):
	if i in {1,2,3}:
		if perm_minority and perm_white:
			return interweave(random.sample(white_cands[:num_seats],num_seats), random.sample(minority_cands[:num_seats],num_seats))
		if perm_minority and not perm_white:
			return interweave(white_cands[:num_seats], random.sample(minority_cands[:num_seats],num_seats))
		if not perm_minority and  perm_white:
			return interweave(random.sample(white_cands[:num_seats],num_seats), minority_cands[:num_seats])
		if not perm_minority and not perm_white:
			return interweave(white_cands[:num_seats], minority_cands[:num_seats])
	elif i == 0:
		if perm_minority and perm_white:
			return interweave(random.sample(minority_cands[:num_seats],num_seats), random.sample(white_cands[:num_seats],num_seats))
		if perm_minority and not perm_white:
			return interweave(random.sample(minority_cands[:num_seats],num_seats), white_cands[:num_seats])
		if not perm_minority and  perm_white:
			return interweave(minority_cands[:num_seats], random.sample(white_cands[:num_seats],num_seats))
		if not perm_minority and not perm_white:
			return interweave(minority_cands[:num_seats], white_cands[:num_seats])



def scenario_generator(num_seats, votes, cvap_vec, perm_white_vec, perm_minority_vec, pct_crossover_vec):
	vote_list = []
	for i in range(len(cvap_vec)):
		# polarized votes
		for vote in range(math.ceil(votes*cvap_vec[i]*(1.0-pct_crossover_vec[i]))):
			vote_list.append([polarized_generator(num_seats, i, perm_white_vec[i], perm_minority_vec[i]),1.0])
		# crossover votes
		for vote in range(math.ceil(votes*cvap_vec[i]*(pct_crossover_vec[i]))):
			vote_list.append([crossover_generator(num_seats, i, perm_white_vec[i], perm_minority_vec[i]),1.0])
	return vote_list


candidate_dict = {'w1':0,'w2':0,'w3':0,'w4':0,'w5':0,'w6':0,'w7':0,'w8':0,'w9':0,'min1':1,'min2':1,'min3':1,'min4':1,'min5':1,'min6':1,'min7':1,'min8':1,'min9':1}

white_cands = ['w1','w2','w3','w4','w5','w6','w7','w8','w9']
minority_cands = ['min1','min2','min3','min4','min5','min6','min7','min8','min9']


def run_scenarios(cvap_vec, crossover_vec, num_votes, num_runs):

	scen1 = [[False, False, False, False],
			[False, False, False, False],
			[0,0,0,0], 'total pol., unam vote']

	scen2a = [[False, False, False, False],
			[False, True, True, True],
			[0,0,0,0], 'total pol., minority permute min_i']

	scen2b = [[True, True, True, True],
			[True, True, True, True],
			[0,0,0,0], 'total pol., all permute all']

	scen2c = [[True, False, False, False],
			[True, False, False, False],
			[0,0,0,0], 'total pol., white permute all']

	scen3 = [[False, False, False, False],
			[False, False, False, False],
			crossover_vec, 'crossover, unam vote']

	scen4a = [[False, False, False, False],
			[False, True, True, True],
			crossover_vec, 'crossover, minority permute min_i']

	scen4b = [[True, True, True, True],
			[True, True, True, True],
			crossover_vec, 'crossover, all permute all']

	scen4c = [[True, False, False, False],
			[True, False, False, False],
			crossover_vec, 'crossover, white permute all']

	scen_list = [scen1, scen2a, scen2b, scen2c, scen3, scen4a, scen4b, scen4c]

	results = {}

	for scen in scen_list:
		num_runs_performed = 1 if 'unam' in scen[3] else num_runs
		print('num runs:', num_runs_performed)
		for i in [3,5,7,9]:
			num_minority_seats = []
			for j in range(num_runs_performed):
				winners = rcv_run(scenario_generator(i, num_votes, cvap_vec, scen[0], scen[1], scen[2]), i, True, False)
				num_minority_seats.append(sum(candidate_dict[x] for x in winners))
			if 'unam' in scen[3]:
				print(scen[3], i, 'seats', 'minority_seats:', num_minority_seats)
			else:
				print(scen[3], i, 'seats', 'min:', min(num_minority_seats), 'max:', max(num_minority_seats), 'avg:', sum(num_minority_seats)/len(num_minority_seats))
		

###################### Edit Inputs Below ###################### 

#white, minority1, minority2, other
cvap_vec = [.60, .3, .15, .05]

#white, minority1, minority2, other
crossover_vec = [.2,.3,.2,.3]

num_votes = 3000
num_runs = 100

run_scenarios(cvap_vec, crossover_vec, num_votes, num_runs)
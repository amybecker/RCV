import csv
import operator
import numpy as np
import matplotlib.pyplot as plt



import math
import random

def remove_cand(cand, ballot_list):
	for ballot in ballot_list:
		new_ballot = []
		for c in ballot[0]:
			if c!= cand:
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
	remove_cand('0', ballot_list)
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
	losers = []
	cutoff = 1.0/(num_seats+1)
	
	#identify winners
	while len(winners) < num_seats and max(len(ballot[0]) for ballot in ballot_list) > 0:
		# print(ballot_list)
		# print()
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
			losers.append(min_cand)
			if verbose_bool:
				print("candidate", min_cand, "eliminated")
		else:
			print("******* ISSUE: input error *******")
			break
	return (winners, losers)



###################################################################


election_file_name = '2010 Mayor Oakland.csv'

precincts_dem = set()
precinct_totpop = {}
precinct_race_vec = {}
with open('rcv_elections.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0            
	for row in csv_reader:
		if line_count == 0:
			line_count += 1
		else:
			precincts_dem.add(row[5])
			precinct_totpop[row[1]] = int(row[2])
			precinct_race_vec[row[1]] = [int(row[3]), int(row[4]), int(row[5]), int(row[6])]
			assert(int(row[2]) >= int(row[3])+int(row[4])+int(row[5])+int(row[6]))
			line_count += 1

#dictionary of precint to race pct vec
precinct_race_vec_pct = {prec[0]:[0 if pop == 0 else pop/precinct_totpop[prec[0]] for pop in prec[1]] for prec in precinct_race_vec.items()}


#dictionary of race triple freq
rank_races = {}

#dictionary of candidate triple freq
rank_cands = {}

#set of precints
precincts = set()

#vote count by precint
precinct_turnout = {}

#dictionary mapping candidate to listed race
candidate_race = {}
candidates = set()



#dictionary mapping precinctss to vector of vote counts for freq triples
precinct_votes = {prec: {trip:0 for trip in freq_cand_triples} for prec in precincts}

total_votes = {}

with open(election_file_name) as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	for row in csv_reader:
		if line_count == 0:
			line_count += 1
		else:
			if row[5] not in precincts:
				precincts.add(row[5])
				precinct_votes[row[5]] = {}
			if (row[8], row[9], row[10]) not in precinct_votes[row[5]]:
				precinct_votes[row[5]][(row[8], row[9], row[10])] = 1
				precinct_turnout[row[5]] = 1
			else:
				precinct_votes[row[5]][(row[8], row[9], row[10])] += 1
				precinct_turnout[row[5]] += 1
			if (row[8], row[9], row[10]) not in total_votes:
				total_votes[(row[8], row[9], row[10])] = 1
			else:
				total_votes[(row[8], row[9], row[10])] += 1

			candidates.add(row[8])
			candidates.add(row[9])
			candidates.add(row[10])

			line_count += 1

total_ballot = []
for item in total_votes.items():
	total_ballot.append([item[0],item[1]])
for cand in candidates:
	total_ballot.append([[cand,'0','0'],0])

city_rank = rcv_run(total_ballot, len(candidates)-1, True, False)
city_winners = city_rank[0]
city_losers = city_rank[1]	
city_losers.reverse()
print('total pop', city_winners + city_losers)


city_votes_by_prec = []

for prec in precincts:
	prec_ballot_list = []
	for item in precinct_votes[prec].items():
		prec_ballot_list.append([list(item[0]), item[1]])
	for cand in candidates:
		prec_ballot_list.append([[cand,'0','0'],0])
	ranking = rcv_run(prec_ballot_list, len(candidates)-1, True, False)
	winners = ranking[0]
	losers = ranking[1]	
	losers.reverse()
	turnout = precinct_turnout[prec]
	city_votes_by_prec.append([winners + losers, turnout])
	# print(prec, winners + losers)


prec_weighted_city_rank = rcv_run(city_votes_by_prec, len(candidates)-1, True, False)
prec_weighted_city_winners = prec_weighted_city_rank[0]
prec_weighted_city_losers = prec_weighted_city_rank[1]	
prec_weighted_city_losers.reverse()
print('rehydrated:', prec_weighted_city_winners + prec_weighted_city_losers)


print(sum(item[1] for item in total_votes.items()))
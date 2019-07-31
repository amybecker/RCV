import csv
import operator
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import stv
import scipy.stats as stats

election_file_name = '2014_Mayor_ballot_image.csv'
output_file_name = 'small_2014_mayoral_oakland.csv'

precincts = set()
precinct_votes = {}
precinct_votes_tally = {}
cands = set()

with open(election_file_name) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            if row[5] not in precincts:
                precincts.add(row[5])
                precinct_votes[row[5]] = [[row[8], row[9], row[10]]]
                precinct_votes_tally[row[5]] = {}
            if (row[8], row[9], row[10]) not in precinct_votes_tally[row[5]]:
                precinct_votes_tally[row[5]][(row[8], row[9], row[10])] = 1
            else:
                precinct_votes[row[5]].append([row[8], row[9], row[10]])
                cands.update([row[8], row[9], row[10]])
                precinct_votes_tally[row[5]][(row[8], row[9], row[10])] += 1
            line_count += 1
csv_file.close()


def clean_cands(cand_partial):
    for i in cands:
        if i not in cand_partial:
            cand_partial.append(i)
    if '0' in cand_partial:
        cand_partial.remove('0')
    return cand_partial

prec_STV = {}
num_cands_for_cutoff = 3

for prec in precincts:
    prec_ballot_list = []
    for item in precinct_votes_tally[prec].items():
        prec_ballot_list.append([list(item[0]), item[1]])
    ranking = stv.rcv_run(prec_ballot_list, num_cands_for_cutoff, True, False)
    winners = ranking[0]
    losers = ranking[1]	
    losers.reverse()
    prec_STV[prec] = clean_cands(winners+losers)


####### distance functions

def list_to_int_list(input_list):
    new_list = []
    for i in input_list:
        new_list.append(int(i))
    return new_list

def kendall_tau(x1, x2):
    tau, p = stats.kendalltau(x1, x2)
    return (-1*tau+1)/2

def kendall_tau_5(x1, x2):
    tau, p = stats.kendalltau(x1[:5], x2[:5])
    return (-1*tau+1)/2


####### objective functions

def obj_1():
    return 1

def L1_norm(val_list):
    return sum(abs(i) for i in val_list)


def L2_norm(val_list):
    running_sum = 0
    for i in val_list:
        running_sum += abs(i)**2
    return running_sum ** (1/2)


######### borda

def borda_score(points, borda_election, stv_dict, dist_func, agg_dist_func):
    """
    function to score each precinct 
    points:  list of associated point values for 1st place thru kth place, given k candidates (p_1, ..., p_k)
    borda_election: dictionary with precincts as keys and a list of individual ballots for each vote in that precinct 
                    under the borda count system
    stv_dict: dictionary with precincts as keys and a list of individual ballots for each vote in that precinct,
                under an STV system
    dist_func: function that takes the Borda point and STV preference schedules and quantifies the dist between them
    agg_dist_func: aggregates the distance results from each precinct """
        
    borda_dict = {}
    borda_result_dict = {}
    precinct_dists = []
    for precinct in list(borda_election.keys()):
        borda_dict[precinct] = {}
        for voter in range(len(borda_election[precinct])):
            for rank in range(len(borda_election[precinct][voter])):
                cand = borda_election[precinct][voter][rank]
                if cand not in borda_dict[precinct]:
                    borda_dict[precinct][cand] = points[rank]
                else: 
                    borda_dict[precinct][cand] += points[rank]

        sorted_borda_dict = dict(sorted(borda_dict[precinct].items(), key=operator.itemgetter(1), reverse=True))
        borda_result_dict[precinct] = list(sorted_borda_dict.keys())
        precinct_dists.append(dist_func(list_to_int_list(clean_cands(borda_result_dict[precinct])), list_to_int_list(stv_dict[precinct])))
        # print(precinct, sorted_borda_dict)
        # print(borda_result_dict[precinct], stv_dict[precinct])
        # print(dist_func(list_to_int_list(clean_cands(borda_result_dict[precinct])), list_to_int_list(stv_dict[precinct])))
        # print()
    score = agg_dist_func(precinct_dists)
    return score 
    

def borda_optimization_wrapper_3cand(num_cands, points_total, election_data, prec_STV_dic, dist_func, obj_func):
    best_val = math.inf
    best_option = [-1]*num_cands
    with open(output_file_name, 'w') as writeFile:
        writer = csv.writer(writeFile)
            
        for i in range(points_total+1):
            print(i)
            for j in range(points_total-i+1):
                k = points_total-i-j
                point_scheme = [i,j,k] + [0]*(num_cands-3)
                cur_val = borda_score(point_scheme, election_data, prec_STV_dic, dist_func, obj_func)
                writer.writerow(point_scheme + [cur_val])
                if cur_val < best_val:
                    best_option = point_scheme
                    best_val = cur_val
    writeFile.close()
    return best_option


# from https://stackoverflow.com/questions/37711817/generate-all-possible-outcomes-of-k-balls-in-n-bins-sum-of-multinomial-catego?rq=1
def gen(n,k):
    if(k==1):
        return [[n]]
    if(n==0):
        return [[0]*k]
    return [ g2 for x in range(n+1) for g2 in [ u+[n-x] for u in gen(x,k-1) ] ]


def borda_optimization_wrapper_ncand(n, num_cands, points_total, election_data, prec_STV_dic, dist_func, obj_func):
    best_val = math.inf
    best_option = [-1]*num_cands
    with open(output_file_name, 'w') as writeFile:
        writer = csv.writer(writeFile)
        for vec in gen(points_total, n):
            print(vec[0])
            point_scheme = vec + [0]*(num_cands-n)
            cur_val = borda_score(point_scheme, election_data, prec_STV_dic, dist_func, obj_func)
            writer.writerow(point_scheme + [cur_val])
            if cur_val < best_val:
                best_option = point_scheme
                best_val = cur_val
    writeFile.close()
    return best_option


points_to_distribute = 20
num_cands = len(cands)
n = 4

# print('best:', borda_optimization_wrapper_3cand(num_cands, points_to_distribute, precinct_votes, prec_STV, kendall_tau, L1_norm))

print('best:', borda_optimization_wrapper_ncand(n, num_cands, points_to_distribute, precinct_votes, prec_STV, kendall_tau, L1_norm))

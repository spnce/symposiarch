beers = {}
for line in open('beers.csv', 'r'):
    fields = line.split(",")
    key = float(fields[1])
    value = fields[0]
    if key in beers:
    	tmp = beers[key]
    	tmp2 = [value] + tmp
    	beers[key] = tmp2
    else:
    	beers[key] = [value]

liquors = {}
for line in open('liquors.csv', 'r'):
    fields = line.split(",")
    key = float(fields[1])
    value = fields[0]
    if key in liquors:
    	tmp = liquors[key]
    	tmp2 = [value] + tmp
    	liquors[key] = tmp2
    else:
    	liquors[key] = [value]

wines = {}
for line in open('wines.csv', 'r'):
    fields = line.split(",")
    key = float(fields[1])
    value = fields[0]
    if key in wines:
    	tmp = wines[key]
    	tmp2 = [value] + tmp
    	wines[key] = tmp2
    else:
    	wines[key] = [value]

import sys
input_type = input("Alcohol Class (B, L, W): ")
input_var = input("Target Alcohol Percentage: ")

if input_type == "L":
	diction = liquors
elif input_type == "B":
	diction = beers
else:
	diction = wines

import random
possible_output = min(diction.items(), key=lambda x: abs(x[0] - input_var))[1]
if len(possible_output) == 1:
	print possible_output[0]
else:
	ran = random.randint(0,len(possible_output)-1)
	print possible_output[ran]
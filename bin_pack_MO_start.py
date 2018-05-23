# Bin packing code for single objective bin packing problem
#    as in ENGSCI 761 MO assignment
# Adapted by Andrea Raith from Mike O'Sullivan's bin_pack_func.py (ENGSCI 761 IP labs)

from pulp import *
from random import randint

class BinPackProb:
  def __init__(self, ITEMS, volume, types, capacity, no_types):
    self.ITEMS = ITEMS
    self.volume = dict(zip(ITEMS, volume))
    self.types = dict(zip(ITEMS, types))
    self.BINS = range(len(ITEMS)) # Create 1 bin for each item, indices start at 0
    self.capacity = capacity
    self.no_types = no_types
    self.TYPES = range(1,no_types+1) # create list of all types: {1,2,...,no_types}

def formulate(bpp):
  # formulate the optimisation problem
  prob = pulp.LpProblem("Bin packing problem",pulp.LpMinimize)

  assign_vars = LpVariable.dicts("y",
                                 [(i, j) for i in bpp.ITEMS
                                         for j in bpp.BINS],
                                 cat=LpBinary)
  use_vars    = LpVariable.dicts("x", bpp.BINS, cat=LpBinary)
  waste_vars  = LpVariable.dicts("w", bpp.BINS, 0, None)

  unique_vars = LpVariable.dicts("u",
                                 [(j, k) for j in bpp.BINS
                                         for k in bpp.TYPES],
                                 cat=LpBinary)


  weight = 0.01
  prob += lpSum(waste_vars[j] for j in bpp.BINS) + weight*lpSum( lpSum(unique_vars[j, k] for k in bpp.TYPES) - 1 for j in bpp.BINS ), "lexi"

  M = 1e3
  for j in bpp.BINS:
    for k in bpp.TYPES:
      prob += M * unique_vars[j, k] >= lpSum(assign_vars[i, j] if bpp.types[i] == k else 0 for i in bpp.ITEMS)

  # Cost = unique types - 1
  # Enforce number of unique types >= 1 so having zero items is not rewarded
  for j in bpp.BINS:
    prob += lpSum(unique_vars[j, k] for k in bpp.TYPES) >= 1
 
  for j in bpp.BINS:
    prob += lpSum(bpp.volume[i] * assign_vars[i, j] for i in bpp.ITEMS) \
            + waste_vars[j] == bpp.capacity * use_vars[j]

  for i in bpp.ITEMS:
    prob += lpSum(assign_vars[i, j] for j in bpp.BINS) == 1

  # ordering the bins
  for j in range(len(bpp.BINS)-1):
        prob += use_vars[j] - use_vars[j+1] >= 0

  # Save problem structures for later use
  prob.assign_vars = assign_vars
  prob.use_vars = use_vars
  prob.waste_vars = waste_vars
  prob.unique_vars = unique_vars
      
  return prob


def solve(prob,solver,msg_out=1):
  # solve the problem and report on solution status
  print "solving..."

  if solver == "Gurobi":
    # solve using gurobi -- may not work in computer labs
    prob.solve(pulp.GUROBI_CMD(msg = msg_out)) # msg = 1 for output, 0 for no output
  elif solver == "CBC":
    prob.solve(PULP_CBC_CMD(msg = msg_out)) # msg = 1 for output, 0 for no output
  else:
    print "unknown solver type. stop."
    return

  # solution status
  if LpStatus[prob.status] == 'Optimal':
    print "optimal solution found"
  else:
    print "no optimal solution found"
  
  return prob.status


def eval_objective(prob,bpp):
  # calculates objective value from decision variables

  for j in bpp.BINS:
    for i in bpp.ITEMS:
      if value(prob.assign_vars[i, j]) > 0:
        print prob.assign_vars[i, j]
  
  total_waste = 0
  for j in bpp.BINS:
    if not(value(prob.waste_vars[j]) is None):
      total_waste = total_waste + int(round(value(prob.waste_vars[j])))

  mixed_types = lpSum( lpSum(value(prob.unique_vars[j, k]) for k in bpp.TYPES) - 1 for j in bpp.BINS )

  return total_waste, mixed_types


          
if __name__ == '__main__':

  # 10 items
  itms = range(10)
  vols = [4, 3, 12, 3, 15, 5, 2, 2, 15, 2]
  typs = [5, 1, 1, 5, 2, 5, 5, 1, 3, 4]
  Cap = 25
  max_type = max(typs)

  
  bpp = BinPackProb(ITEMS  = itms,
                  volume = vols,
		  types = typs,
                  capacity = Cap,
                  no_types = max_type)

  prob = formulate(bpp)

  # status = solve(prob,"CBC",1) # arguments: problem, solver type (CBC), 1 for output; 0 for no output
  # Using Gurobi as solver - first add Gurobi to system path, see instructions
  status = solve(prob,"Gurobi",1) # arguments: problem, solver type (Gurobi), 1 for output; 0 for no output

  if LpStatus[status] == 'Optimal':
    print "objective value of optimal solution is: " + str(int(round(value(prob.objective))))

    wasted_space = eval_objective(prob,bpp)

    print "un-weighted objective value calculated based on decision variables is: " + str(wasted_space)


 

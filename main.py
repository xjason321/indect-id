import Player as p
import Graph as graph
import Algorithm as a
import random
import math

from flask import Flask, render_template

def run_ai(ai, player, percentSamples, percentTraced):

  numSamples = round(percentSamples * player.size)
  numTraced = round(percentTraced * numSamples)
  numberToSelect = math.ceil(0.03 * player.size)
  
  for _ in range(numSamples):
      chosen = ai.ChooseOneToSample(player)
      player.sample(chosen)
  
  print(f"Sampled {len(player.sampled)} Nodes: {player.sampled}")
  
  # After, calculate likelihoods
  sorted_indices = ai.getSortedIds()
  
  # Find spread pattern for most likely
  for Id in sorted_indices[-numTraced:]:
      ai.TraceSpreadPattern(player, Id)
  
  traced = sorted_indices[-numTraced:]
  
  print(f"Traced Spread Patterns For {sorted_indices[-numTraced:]}")
  
  # Compare likelihoods again
  sorted_indices = ai.getSortedIds()
  
  # Print 5 Top Choices (rightmost is the one it's most confident in)
  print(f"Top Choices From AI (least confident to most confident, right being most confident): \n{sorted_indices[-numberToSelect:]}")
  
  for nodeNumber in sorted_indices[-numberToSelect:]:
    player.nodes[nodeNumber].selectedByAI = "True"

  return sorted_indices, traced

app = Flask(__name__, template_folder = 'templates', static_folder='static')

@app.route('/')
def index():

  # NEAT GENOME SHIT: (THESE WILL BE GENERATED)
  # RIGHT NOW THEY ARE NUMBERS PULLED FROM MY ASS
  negativeEffectBias = 0.1
  positiveBias = 0.1
  positiveEffectBias = 0.05
  similarityWeight = 1
  percentSamples = 0.1
  percentTraced = 0.5
  
  player = p.Player(
    size = random.randint(100, 250),
    time = random.randint(2, 5),
    min = random.randint(2, 4),
    max = random.randint(3, 5),
    percent = random.uniform(0, 0.1) # initially given
  )

  ai = a.Algorithm(
    size=player.size,

    # NEAT
    negativeEffectBias=negativeEffectBias,
    positiveBias=positiveBias,
    positiveEffectBias=positiveEffectBias,
    similarityWeight=similarityWeight
  )
  
  sorted, traced = run_ai(ai, player, percentSamples, percentTraced)
  
  # Start window loop
  nodes, edges = graph.CreateGraphHTML(player, "templates/index.html")

  return render_template(
    'index.html', 
    
    nodes=nodes, 
    edges=edges, 
    
    actual_p_zero=player.p_zero, 
    sampled=str(player.sampled), 
    sorted=sorted[-20:], 
    traced=str(traced),
    
    num_nodes=len(player.nodes),
    alloted_time=player.time,
    min=player.min_connections,
    max=player.max_connections,
    num_visible=player.num_visible_to_player
  )

if __name__ == "__main__":  # Makes sure this is the main process
	app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
	)

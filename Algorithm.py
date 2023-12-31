import Player as p
import copy
import Node as nn
import math, random

class Algorithm():
    def __init__(self, size, negativeEffectBias, positiveBias, positiveEffectBias, similarityWeight):
      self.nodeLikelihoods = [1] * size
      # self.percentSamplesAlloted = 0.2
      # self.percentTracesAlloted = 0.05

      self.negativeEffectBias = negativeEffectBias

      self.positiveBias = positiveBias
      self.positiveEffectBias = positiveEffectBias

      self.similarityWeight = similarityWeight

    def InitialScan(self, nodes):
        # All negative nodes can't be patient zero, and the chances
        # of their neighbors being patient zero is less.
        for node in nodes:
            if node.state == 0:
                self.nodeLikelihoods[node.id] = 0
                for neighbor in node.connections:
                    self.nodeLikelihoods[neighbor.id] -= self.negativeEffectBias
            elif node.state == 1:
                self.nodeLikelihoods[node.id] += self.positiveBias
                for neighbor in node.connections:
                    self.nodeLikelihoods[neighbor.id] += self.positiveEffectBias

    def ChooseOneToSample(self, player):
        # Find most likely after initial scan
        self.InitialScan(player.nodes.values())

        save = []

        for node in player.sampled:
            save.append((player.nodes[node].id, self.nodeLikelihoods[node]))
            self.nodeLikelihoods[node] = -999

        mostLikely = max(self.nodeLikelihoods)

        for Id, likelihood in save:
            self.nodeLikelihoods[Id] = likelihood

        # Find most likely nodes and sample them
        likelyNodes = []
        for node in player.nodes.values():
            if self.nodeLikelihoods[node.id] == mostLikely:
                likelyNodes.append(node.id)

        return random.choice(likelyNodes) 

    def FindDifference(self, list1, list2):
        # Calculate Jaccard similarity
        intersection = len(set(list1).intersection(set(list2)))
        union = len(set(list1).union(set(list2)))
        jaccard_similarity = intersection / union

        return jaccard_similarity

    def TraceSpreadPattern(self, Player, target_node):
        new_player = copy.deepcopy(Player)

        # Reset infections
        for node in new_player.nodes.values():
            node.state = 0

        nn.runInfectionSimulation(4, new_player.nodes, selected_p_zero=new_player.nodes[target_node+1])

        infectionsForNewPlayer = [node.state for node in new_player.nodes.values()]
        infectionsForCurrentPlayer = [node.state for node in Player.nodes.values()]

        difference = math.fabs(self.FindDifference(infectionsForNewPlayer, infectionsForCurrentPlayer))

        self.nodeLikelihoods[int(Player.nodes[target_node+1].id) - 1] -= (difference * self.similarityWeight)

    def getSortedIds(self):
        indexed_arr = [(value, index) for index, value in enumerate(self.nodeLikelihoods)]

        # Sort the list of tuples based on values
        sorted_arr = sorted(indexed_arr, key=lambda x: x[0])

        # Extract the sorted indices
        sorted_indices = [index for _, index in sorted_arr]

        return sorted_indices


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
  for Id in sorted_indices[:numTraced]:
    ai.TraceSpreadPattern(player, Id)

  traced = sorted_indices[:numTraced]

  print(f"Traced Spread Patterns For {sorted_indices[:numTraced]}")

  # Compare likelihoods again
  sorted_indices = ai.getSortedIds()

  # Print 5 Top Choices (rightmost is the one it's most confident in)
  print(
      f"Top Choices From AI (least confident to most confident, right being most confident): \n{sorted_indices[-numberToSelect:]}"
  )

  for nodeNumber in sorted_indices[-numberToSelect:]:
    player.nodes[nodeNumber].selectedByAI = "True"

  return sorted_indices, traced

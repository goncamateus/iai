# ghostAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import random
from copy import deepcopy

import bfs
import util
from game import Actions, Agent, Directions
from pacman import GameState
from util import manhattanDistance


class GhostAgent(Agent):
    def __init__(self, index):
        self.index = index

    def getAction(self, state):
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state):
        "Returns a Counter encoding a distribution over actions from the provided state."
        util.raiseNotDefined()


COMMUNICATION = {}


class CommGhost(GhostAgent):
    "A ghost that prefers to rush Pacman, or flee when scared."

    def __init__(self, index, depth=3):
        self.index = index
        self.depth = depth

    def encode_state(self, state: GameState):
        encode = list()
        pacman_pos = state.getPacmanPosition()
        encode.append(pacman_pos)
        encode += state.getGhostPositions()
        encode.append(state.getNumFood())
        return tuple(encode)

    def get_maze_distance(self, gameState, index):
        start = gameState.getGhostPosition(index)
        goal = gameState.getPacmanPosition()
        walls = deepcopy(gameState.getWalls())
        other_pos = [gameState.getGhostPosition(i) for i in range(
            1, gameState.getNumAgents()) if i != index]
        for pos in other_pos:
            walls.data[int(pos[0])][int(pos[1])] = True
        res = bfs.search(start, goal, walls)
        return len(res)

    def get_expectimax_score(self, gameState: GameState, agentIndex, depth):

        if gameState.getGhostState(self.index).scaredTimer > 0:
            if agentIndex != 0:
                if self.get_maze_distance(gameState, agentIndex) <= 4:
                    return -100000
            else:
                if self.get_maze_distance(gameState, self.index) <= 4:
                    return -100000
        elif gameState.isLose():
            return 100000
        if depth == 0 or gameState.isWin():
            # dist to agent agentIndex
            if agentIndex != 0:
                return -self.get_maze_distance(gameState, agentIndex)
            else:
                return -self.get_maze_distance(gameState, self.index)

        if agentIndex != 0:
            return self.max_value(gameState, agentIndex, depth)[0]
        else:
            return self.exp_value(gameState, depth)

    def max_value(self, gameState, agentIndex, depth):
        global COMMUNICATION
        v = -1000000
        best_action = None
        actions = gameState.getLegalActions(agentIndex)
        for action in actions:
            successor = gameState.generateSuccessor(agentIndex, action)
            encoded = self.encode_state(successor)
            if successor.isWin():
                res = -100000
            elif successor.isLose():
                res = 100000
            else:
                if encoded in COMMUNICATION:
                    res = COMMUNICATION[encoded]
                else:
                    if agentIndex == gameState.getNumAgents() - 1:
                        res = self.get_expectimax_score(successor, 0, depth)
                    else:
                        res = self.max_value(
                            successor, agentIndex + 1, depth)[0]
            COMMUNICATION[encoded] = res
            if v < res:
                v = res
                best_action = action
        return v, best_action

    def exp_value(self, gameState: GameState, depth):
        global COMMUNICATION
        v = 0
        actions = gameState.getLegalActions(0)
        if gameState.isLose():
            return 100000
        if len(actions) == 0 or gameState.isWin():
            return -100000

        for action in actions:
            successor = gameState.generateSuccessor(0, action)
            encoded = self.encode_state(successor)
            if encoded in COMMUNICATION:
                val = COMMUNICATION[encoded]
            else:
                val = self.get_expectimax_score(successor, 1, depth - 1)
                COMMUNICATION[encoded] = val
            v += val
        return v / len(actions)

    def getDistribution(self, state):
        global COMMUNICATION
        dist = util.Counter()
        action = self.max_value(state, self.index, self.depth)[1]
        dist[action] = 1.0
        dist.normalize()
        if self.index == state.getNumAgents() - 1:
            COMMUNICATION = {}
        return dist


class RandomGhost(GhostAgent):
    "A ghost that chooses a legal action uniformly at random."

    def getDistribution(self, state):
        dist = util.Counter()
        for a in state.getLegalActions(self.index):
            dist[a] = 1.0
        dist.normalize()
        return dist


class DirectionalGhost(GhostAgent):
    "A ghost that prefers to rush Pacman, or flee when scared."

    def __init__(self, index, prob_attack=0.8, prob_scaredFlee=0.8):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution(self, state):
        # Read variables from state
        ghostState = state.getGhostState(self.index)
        legalActions = state.getLegalActions(self.index)
        pos = state.getGhostPosition(self.index)
        isScared = ghostState.scaredTimer > 0

        speed = 1
        if isScared:
            speed = 0.5

        actionVectors = [Actions.directionToVector(
            a, speed) for a in legalActions]
        newPositions = [(pos[0]+a[0], pos[1]+a[1]) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Select best actions given the state
        distancesToPacman = [manhattanDistance(
            pos, pacmanPosition) for pos in newPositions]
        if isScared:
            bestScore = max(distancesToPacman)
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min(distancesToPacman)
            bestProb = self.prob_attack
        bestActions = [action for action, distance in zip(
            legalActions, distancesToPacman) if distance == bestScore]

        # Construct distribution
        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legalActions:
            dist[a] += (1-bestProb) / len(legalActions)
        dist.normalize()
        return dist

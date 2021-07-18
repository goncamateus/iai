# multiAgents.py
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

import util
from game import Agent, AgentState, Directions, GameStateData
from pacman import GameState
from util import manhattanDistance


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()
        if 'Stop' in legalMoves:
            legalMoves.remove('Stop')

        # Choose one of the best actions
        scores = [self.evaluationFunction(
            gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(
            len(scores)) if scores[index] == bestScore]
        # Pick randomly among the best
        chosenIndex = random.choice(bestIndices)
        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)

        ghost_score = self.get_ghost_score(currentGameState)
        future_ghost_score = self.get_ghost_score(successorGameState)

        best_food = self.get_best_food(currentGameState)

        my_pos = currentGameState.getPacmanPosition()
        my_future_pos = successorGameState.getPacmanPosition()

        score = 0

        score += future_ghost_score

        if util.manhattanDistance(my_pos, best_food) < util.manhattanDistance(my_future_pos, best_food):
            score -= 10
        else:
            score += 10

        return score

    def get_ghost_score(self, gameState: GameState):
        score = 0
        closest_capsule = self.get_closest_capsule(gameState)
        closest_ghost = self.get_closest_ghost(gameState)
        my_pos = gameState.getPacmanPosition()
        dist_ghost = util.manhattanDistance(
            my_pos, closest_ghost.getPosition())
        scared_timer = closest_ghost.scaredTimer
        if dist_ghost + scared_timer < 3:
            if closest_capsule:
                dist_capsule = util.manhattanDistance(
                    my_pos, closest_capsule)
                if dist_capsule < 2:
                    score += 10
                else:
                    score = -100
            else:
                score = -100
        elif closest_capsule:
            dist_capsule = util.manhattanDistance(my_pos, closest_capsule)
            if dist_capsule < 2:
                score += 10
        return score

    def get_best_foods_from_ghost(self, gameState: GameState, ghost: AgentState):
        food_positions = gameState.getFood().asList()
        ghost_distances = [manhattanDistance(ghost.getPosition(), food)
                           for food in food_positions]
        my_pos = gameState.getPacmanPosition()
        my_distances = [manhattanDistance(my_pos, food)
                        for food in food_positions]
        best_pos = None
        best_dist = 1000
        for i, food_pos in enumerate(food_positions):
            if best_dist == 1000:
                best_pos = food_pos
                best_dist = my_distances[i]
            elif my_distances[i] < ghost_distances[i] + ghost.scaredTimer:
                if best_dist > my_distances[i]:
                    best_pos = food_pos
                    best_dist = my_distances[i]

        return best_pos

    def get_best_food(self, gameState: GameState) -> tuple:
        ghosts = gameState.getGhostStates()
        my_pos = gameState.getPacmanPosition()
        best_foods = [self.get_best_foods_from_ghost(gameState, ghost)
                      for ghost in ghosts]
        closest_bests = min(best_foods, key=lambda x: util.manhattanDistance(
            my_pos, x))
        return closest_bests

    def get_closest_capsule(self, gameState: GameState):
        capsule_positions = gameState.getCapsules()
        my_pos = gameState.getPacmanPosition()
        distances = [manhattanDistance(my_pos, capsule)
                     for capsule in capsule_positions]
        if capsule_positions:
            return capsule_positions[distances.index(min(distances))]
        return None

    def get_closest_ghost(self, gameState: GameState) -> AgentState:
        ghost_states = gameState.getGhostStates()
        my_pos = gameState.getPacmanPosition()
        distances = [manhattanDistance(
            my_pos, ghost.getPosition()) for ghost in ghost_states]
        return ghost_states[distances.index(min(distances))]


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction

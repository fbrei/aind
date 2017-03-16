"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def h_distances_between(game,player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player as inverse distance between the player and its opponent.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    ### Maximize distance to the second player
    pos1 = game.get_player_location(player)
    pos2 = game.get_player_location(game.get_opponent(player))
    
    deltax = pos1[0] - pos2[0]
    deltay = pos1[1] - pos2[1]

    return 1.0 / (abs(deltax) + abs(deltay))


def h_distance_center(game,player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player as inverse distance between the player and the center of the board.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")


    ### Minimize distance to center
    position = game.get_player_location(player)

    # The difference in the x-coordinate
    deltax = position[0] - game.width/2

    # Same for the y-coordinate
    deltay = position[1] - game.height/2

    # Avoid division by zero
    if deltax == 0 and deltay == 0:
        return float("inf")
    else:
        return 1.0 / (abs(deltax) + abs(deltay))



def h_closest_center_move(game,player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player as being able to block the closest move towards the
    center that the enemy can make.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # The center coordinates
    game_center = [game.width, game.height]

    # Get all movement options of the enemy
    legal_enemy_moves = game.get_legal_moves(game.get_opponent(player))

    # Calculate the distance of all reachable locations to the center, return the minimum
    return min( [ abs(move[0] - game_center[0]) + abs(move[1] - game_center[1]) for move in legal_enemy_moves] )


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # This function calculates the heuristic as the sum of the distance to center
    # and the number of movement options left.

    # The inverse distance to the center is always < 1, the difference between two
    # numbers of motion options is at least 1 apart. To make the inverse distance matter
    # at all, it has to be multiplied by a factor, whereas #my-moves has to be divided.
    k = 5.0


    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    
    position = game.get_player_location(player)

    deltax = position[0] - game.width/2
    deltay = position[1] - game.height/2

    if deltax == 0 and deltay == 0:
        return float("inf")
    else:
        return k * 1.0 / (abs(deltax) + abs(deltay)) + (1.0/k) * len(game.get_legal_moves(player))



class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        # If there is no legal move, forfeit
        if not legal_moves:
            return (-1,-1)
        
        # Save the first legal move, just in case of timeout
        best_heuristic, best_move = float("-inf"), legal_moves[0]

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.method == 'minimax':
                search = self.minimax
            else:
                search = self.alphabeta

            if self.iterative:
                depth = 1
                while True:
                    # Assume that deeper searches give better results
                    best_heuristic, best_move = search(game,depth)
                    depth = depth+1 
            else:
                best_heuristic, best_move = search(game, self.search_depth)



        except Timeout:
            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """

        # Always check first if we reach the timeout
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        # We reached a leaf node. This means that our agent either won or lost
        if not game.get_legal_moves(self):
            return game.utility(self), game.get_player_location(self)

        # The base case only looks one move ahead and calls the score method for the resulting situations.
        # The extra tuple is added in case the minimizing player has no more movement options, so the min-function does not receive an empty list.
        if depth == 1:
            if maximizing_player:
                return max( [ ( self.score(game.forecast_move(move),self),move ) for move in game.get_legal_moves() ] )
            else:
                return min( [ ( self.score(game.forecast_move(move),self),move ) for move in game.get_legal_moves() ] + [ (float("inf"), (-1,-1)) ] )
        else:
            if maximizing_player:
                return max( [ (self.minimax(game.forecast_move(move),depth-1,not maximizing_player)[0], move) for move in game.get_legal_moves() ] )  
            else:
                return min( [ (self.minimax(game.forecast_move(move),depth-1,not maximizing_player)[0], move) for move in game.get_legal_moves() ] + [ (float("inf"), (-1,-1)) ] )  



    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """

        # Again, check for timeout first
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        
        # Get the legal moves of the current player
        legal_moves = game.get_legal_moves()

        # Leaf node, either we won or we lost
        if not game.get_legal_moves(self):
            return game.utility(self), game.get_player_location(self)

        # The base case, only expand one step or the end of the game is reached and there is no use
        # in expanding beyond this point
        if depth == 1 or len(game.get_blank_spaces()) == 1:
            if maximizing_player:
                # The initial best move
                best_score, best_move = float("-inf"), legal_moves[0]
                for move in legal_moves:
                    # The value of this move can be calculated directly
                    score = self.score(game.forecast_move(move),self)
                    # If we have crossed a threshold, this branch becomes irrelevant
                    if score >= beta:
                        return score, move
                    else:
                        # And update the best move if we have found a better one
                        if score > best_score:
                            best_score, best_move = score, move

                return best_score, best_move

            else:
                # This time we are minimizing
                worst_score, worst_move = float("inf"), (-1,-1)
                for move in legal_moves:
                    # Again, calculate directly
                    score = self.score(game.forecast_move(move),self)
                    # Check to see if we have crossed the line. If so, there is no use in continuing
                    if score <= alpha:
                        return score, move
                    else:
                        # Update the new minimum score
                        if score < worst_score:
                            worst_score, worst_move, = score, move

                return worst_score, worst_move

        else:
            if maximizing_player:
                best_score, best_move = float("-inf"), legal_moves[0]
                for move in legal_moves:
                    # The score cannot be calculated directy, but as the return value of the subtree search
                    score = self.alphabeta(game.forecast_move(move),depth-1,alpha,beta,not maximizing_player)[0]
                    if score >= beta:
                        return score,move
                    else:
                        if score > best_score:
                            best_score, best_move = score, move
                            # The new score is higher than the old lower bound, so update it
                            alpha = score

                return best_score, best_move

            else:
                worst_score, worst_move = float("inf"), (-1,-1)
                for move in legal_moves:
                    # The score cannot be calculated directy, but as the return value of the subtree search
                    score = self.alphabeta(game.forecast_move(move),depth-1,alpha,beta,not maximizing_player)[0]
                    if score <= alpha:
                        return score,move
                    else:
                        if score < worst_score:
                            worst_score, worst_move, = score, move
                            # Update the upper bound to make sure pruning works as expected
                            beta = score

                return worst_score, worst_move

# playerdatabase.py
#
# Draft team class.
#
# Don Nguyen
# Aug, 2015
  
import os

class DraftTeams:

    # Constructor
    def __init__(self, cfg):
        
        self.cfg = cfg

        # Create empty list of teams
        self.teams = {}

    # Add a draft team
    def add_team(self, teamname):

        self.teams[teamname] = DraftTeam(self.cfg)

    # Return list of drafted players
    def drafted_players(self):

        # Initialize empty list of drafted players
        dft_players = []

        for team in self.teams:
            for player in self.teams[team].drafted:
                if player != None:
                    dft_players.append(player)

        return dft_players

    # Determine draft round number
    def round(self):

        # initialize dict of draft rounds
        next_draft_round = {}

        # Determine next draft round for each player
        for team in self.teams:

            # Loop through draft list rounds
            for i in range(0, self.cfg['num_rounds']):

                # If empty draft slot, this is the next draft round for this player 
                if self.teams[team].drafted[i] == None:
                    next_draft_round[team] = i
                    break

        # Get a player that is drafting this round
        # Note that this is a random player and not neccessarily the next drafter
        player_next_draft_round = min(next_draft_round)

        # Return the lowest draft round
        return next_draft_round[player_next_draft_round]

class DraftTeam:

    # Constructor
    def __init__(self, cfg):

        self.cfg = cfg
        
        # Create empty draft list
        self.drafted = [None]*cfg['num_rounds']

        # Create empty positions lists
        self.players = {}
        for pos in cfg['starters']:
            self.players[pos] = []

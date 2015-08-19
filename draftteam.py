# playerdatabase.py
#
# Draft team class.
#
# Don Nguyen
# Aug, 2015
  
import os
import csv
import pdb

class DraftTeams:

    # Constructor
    def __init__(self, cfg):
        
        self.cfg = cfg

        # Create empty list of teams
        self.teams = {}

    # Reset state
    def reset(self):
    
        for team in self.teams:
            
            # Empty draft list
            self.teams[team].drafted = [None]*self.cfg['num_rounds']

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
                    dft_players.append(player[0])

        return dft_players

    # Determine draft round number
    def round(self):

        # initialize next draft round to max
        next_draft_round = self.cfg['num_rounds']

        # Determine next draft round for each player
        for team in self.teams:

            # Loop through draft list rounds
            for i in range(0, self.cfg['num_rounds']):

                # Save lowest draft slot
                if self.teams[team].drafted[i] == None:
                    next_draft_round = min(i, next_draft_round)

        # Return the lowest draft round
        return next_draft_round

    # Get pick number
    def get_pick_num(self):

        # Determine round number
        n_round = self.round()

        # Determine if it is an ascending round or a descending round
        # Event rounds are ascending
        is_ascending_round = (n_round % 2) == 0

        if is_ascending_round:
            # Loop drafters to find someone that needs to draft this round
            for i in range(0, len(self.cfg['teams'])):
                drafter = self.cfg['teams'][i]
                if self.teams[drafter].drafted[n_round] == None:
                    return i
        else:
            # Loop backwards through drafters to find someone that needs to draft this round
            for i in range(0, len(self.cfg['teams'])):
                drafter = self.cfg['teams'][-(i+1)]
                if self.teams[drafter].drafted[n_round] == None:
                    return i
          
    # Get overall pick number
    def get_overall_pick_num(self):

        return self.round()*len(self.cfg['teams']) + self.get_pick_num()
    
    # Get next drafter
    def get_drafter(self):
    
        # Determine round number
        n_round = self.round()

        # Determine if it is an ascending round or a descending round
        # Event rounds are ascending
        is_ascending_round = (n_round % 2) == 0

        if is_ascending_round:
            # Loop drafters to find someone that needs to draft this round
            for drafter in self.cfg['teams']:
                if self.teams[drafter].drafted[n_round] == None:
                    return drafter
        else:
            # Loop backwards through drafters to find someone that needs to draft this round
            for drafter in reversed(self.cfg['teams']):
                if self.teams[drafter].drafted[n_round] == None:
                    return drafter
     
    def write_state(self):
        
        # Loop through each team
        for team in self.teams:
        
            # Get filename
            fname = os.path.join(self.cfg['team_dir'],team+'.csv')
            fname = os.path.abspath(fname)
        
            # Open file for writing
            f = open(fname, 'wb')
            writer = csv.writer(f)
            
            # Loop through draft picks
            for i in range(0, len(self.teams[team].drafted)):
            
                if self.teams[team].drafted[i] != None:
                    writer.writerows([[i,self.teams[team].drafted[i][0],self.teams[team].drafted[i][1]]])
        
            # Close file
            f.close
            
    def load_state(self):
    
        # Loop through each team
        for team in self.teams:
        
            # Empty draft list
            self.teams[team].drafted = [None]*self.cfg['num_rounds']
        
            # Get filename
            fname = os.path.join(self.cfg['team_dir'],team+'.csv')
            fname = os.path.abspath(fname)
        
            # Open file for reading
            f = open(fname, 'rb')
            reader = csv.reader(f)
            
            # Loop through draft picks in file
            for row in reader:
            
                # Draft player
                self.teams[team].draft_player(int(row[0]), row[1], row[2])
                
            # Close file
            f.close

class DraftTeam:

    # Constructor
    def __init__(self, cfg):

        self.cfg = cfg
        
        # Create empty draft list
        self.drafted = [None]*self.cfg['num_rounds']
        
    # Draft player
    def draft_player(self, n_round, player_name, player_pos):
    
        # Add player and position to draft list
        self.drafted[n_round] = (player_name, player_pos)
        
    # Get position counts
    def get_pos_counts(self):

        # Initialize counters for positions to 0
        pos_counts = {}
        for pos in self.cfg['starters']:
            pos_counts[pos] = 0

        # Count players in each position
        for player in self.drafted:
            if not player == None:
                pos_counts[player[1]] += 1

        # Return player counts
        return pos_counts

    # Generate position weights
    def get_pos_weights(self, n_round):

        # Get position count
        pos_counts = self.get_pos_counts()

        # Loop through position types
        pos_weights = {}
        for pos in self.cfg['starters']:

            # Check if this position is not draftable in this round
            if not pos in self.cfg['draftable'][n_round]:

                # Set weight to undraftable
                pos_weights[pos] = -1.0

            # Check if number of players at position is exceeded
            elif pos_counts[pos] > self.cfg['draft_max'][pos]:

                # Set weight to undraftable
                pos_weights[pos] = -1.0

            # Check if more players than starters ix exceeded
            elif pos_counts[pos] >= self.cfg['starters'][pos]:

                # Decrement weight if starter positions have been filled
                pos_weights[pos] = 1.0 - self.cfg['weight_decrement']*(pos_counts[pos] - self.cfg['starters'][pos] + 1)

            else:

                # Full weight
                pos_weights[pos] = 1.0

        return pos_weights

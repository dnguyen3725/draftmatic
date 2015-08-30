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
            
    def load_state(self, player_db):
    
        # Loop through each team
        for team in self.teams:
        
            # Empty draft list
            self.teams[team].drafted = [None]*self.cfg['num_rounds']
        
            # Get filename
            fname = os.path.join(self.cfg['team_dir'],team+'.csv')
            fname = os.path.abspath(fname)
        
            # Open file for reading
            if os.path.isfile(fname):
                f = open(fname, 'rb')
                reader = csv.reader(f)
            
                # Loop through draft picks in file
                for row in reader:
            
                    # Draft player
                    self.teams[team].draft_player(int(row[0]), row[1], row[2], player_db)
                
                # Close file
                f.close

class DraftTeam:

    # Constructor
    def __init__(self, cfg):

        self.cfg = cfg
        
        # Create empty draft list
        self.drafted = [None]*self.cfg['num_rounds']
        
    # Draft player
    def draft_player(self, n_round, player_name, player_pos, player_db):
    
        # Add player and position to draft list
        self.drafted[n_round] = (player_name, player_pos)  
            
        # Add ADP to list
        if not player_name in player_db.adp:
            player_db.adp[player_name] = 999
            
        # Add to position list if not already there
        if not player_name in player_db.position:
            player_db.position[player_name] = player_pos
        
        # Add to team list if not already there
        if not player_name in player_db.team:
            player_db.team[player_name] = 'Unknown'
        
        # Add to players list if not already there
        if not player_pos in player_db.players:
            player_db.players[player_pos] = []
        
        if not player_name in player_db.players[player_pos]:
            player_db.players[player_pos].append(player_name)
            
        # Add to points list if not already there
        if not player_pos in player_db.proj_points:
            player_db.proj_points[player_pos] = {}
        
        if not player_name in player_db.proj_points[player_pos]:
            player_db.proj_points[player_pos][player_name] = 0.0
            
        if not player_pos in player_db.proj_points_low:
            player_db.proj_points_low[player_pos] = {}
        
        if not player_name in player_db.proj_points_low[player_pos]:
            player_db.proj_points_low[player_pos][player_name] = 0.0
            
        if not player_pos in player_db.proj_points_high:
            player_db.proj_points_high[player_pos] = {}
        
        if not player_name in player_db.proj_points_high[player_pos]:
            player_db.proj_points_high[player_pos][player_name] = 0.0
            
    # Undraft player
    def undraft_player(self, n_round):
    
        self.drafted[n_round] = None
        
    # Get position counts
    def get_pos_counts(self):

        # Initialize counters for positions to 0
        pos_counts = {}
        for pos in self.cfg['starters']:
            
            player_list = self.get_players(pos)
            pos_counts[pos] = len(player_list)

        # Return player counts
        return pos_counts
        
    # Get player lists
    def get_players(self, pos):
        
        player_list = []
        
        for i in range(0, len(self.drafted)):
        
            if self.drafted[i] != None:
            
                if self.drafted[i][1] == pos:
                
                    player_list.append(self.drafted[i][0])
                    
        return player_list
        

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
            elif pos_counts[pos] >= self.cfg['draft_max'][pos]:

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
        
    # Get expected low range starter points
    def get_exp_points_starter_low(self, player_db, pos):
    
        # Get list of players at position
        players = self.get_players(pos)
        
        # Get dict of expected points
        fpts = {}
        for player in players:
            fpts[player] = player_db.get_fpts_low(player)
            
        # Sort by points
        fpts_sorted = sorted(fpts, key=fpts.get)
        
        # Number of starters
        n_starters = min(self.cfg['starters'][pos], len(fpts_sorted))
        
        # Sum number of points for starters
        exp_points = 0.0
        for i in range(0, n_starters):
            exp_points = exp_points + fpts[fpts_sorted[i]]
            
        return exp_points
            
    # Get expected high range starter points
    def get_exp_points_starter_high(self, player_db, pos):
    
        # Get list of players at position
        players = self.get_players(pos)
        
        # Get dict of expected points
        fpts = {}
        for player in players:
            fpts[player] = player_db.get_fpts_high(player)
            
        # Sort by points
        fpts_sorted = sorted(fpts, key=fpts.get)
        
        # Number of starters
        n_starters = min(self.cfg['starters'][pos], len(fpts_sorted))
        
        # Sum number of points for starters
        exp_points = 0.0
        for i in range(0, n_starters):
            exp_points = exp_points + fpts[fpts_sorted[i]]
            
        return exp_points
        
    # Get expected low range bench points
    def get_exp_points_bench_low(self, player_db, pos):
    
        # Get list of players at position
        players = self.get_players(pos)
        
        # Get dict of expected points
        fpts = {}
        for player in players:
            fpts[player] = player_db.get_fpts_low(player)
            
        # Sort by points in reverse
        fpts_sorted = sorted(fpts, key=fpts.get, reverse=True)
        
        # Number of starters
        n_starters = min(self.cfg['starters'][pos], len(fpts_sorted))
        
        # Number of bench players
        n_bench = max(0, len(fpts_sorted)-n_starters)
        
        # Sum number of points for starters
        exp_points = 0.0
        for i in range(0, n_bench):
            exp_points = exp_points + fpts[fpts_sorted[i]]
            
        return exp_points
            
    # Get expected high range bench points
    def get_exp_points_bench_high(self, player_db, pos):
    
        # Get list of players at position
        players = self.get_players(pos)
        
        # Get dict of expected points
        fpts = {}
        for player in players:
            fpts[player] = player_db.get_fpts_high(player)
            
        # Sort by points
        fpts_sorted = sorted(fpts, key=fpts.get, reverse=True)
        
        # Number of starters
        n_starters = min(self.cfg['starters'][pos], len(fpts_sorted))
        
        # Number of bench players
        n_bench = max(0, len(fpts_sorted)-n_starters)
        
        # Sum number of points for starters
        exp_points = 0.0
        for i in range(0, n_bench):
            exp_points = exp_points + fpts[fpts_sorted[i]]
            
        return exp_points

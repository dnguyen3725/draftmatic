# playerdatabase.py
#
# Player database class.
#
# Don Nguyen
# Aug, 2015

import os
import xlrd
import copy
import pdb

class PlayerDatabase:

    # Constructor
    def __init__(self, cfg):
	
        self.cfg = cfg

        # Import player projection data
        self.import_player_projections()
        
        # Import defensive projection data
        self.import_defensive_projections()
        
        # Import average draft position data
        self.import_adp()

    # Import player projections from xls files
    def import_player_projections(self):
        
        # Create empty team dict
        self.team = {}
        
        # Create empty position dict
        self.position = {}
        
        # Create empty players dict
        self.players = {}
        
        # Create empty projected points dict
        self.proj_points = {}
        self.proj_points_low = {}
        self.proj_points_high = {}

        for pos in ('QB','RB','WR','TE','K'):
        
            filename = self.cfg['f_proj'][pos]
                
            print('Parsing ' + pos + ' Projection Data')
                
            # Get full filename
            fname = os.path.join(self.cfg['root_dir'],filename)
            fname = os.path.abspath(fname)
            
            # Read in xls workbook
            xl_workbook = xlrd.open_workbook(fname)
                
            # Read in first sheet of workbook
            xl_sheet = xl_workbook.sheet_by_index(0)
                
            # Number of columns
            num_cols = xl_sheet.ncols
                
            # Initialize flag to search for header row
            found_header = False
                
            # Create empty list of players
            self.players[pos] = []

            # Create empty dict of projected points
            self.proj_points[pos] = {}
            self.proj_points_low[pos] = {}
            self.proj_points_high[pos] = {}
                
            # Iterate through rows of xls file
            for row_idx in range(0, xl_sheet.nrows):
                        
                # Scan through file looking for header row	
                if (not found_header) and (xl_sheet.cell(row_idx, 0).value.find('Player Name') >= 0):
                                
                    # Header row found, save header names
                    hdr = []
                    for col_idx in range(0, num_cols): 
                                        
                        hdr.append(xl_sheet.cell(row_idx, col_idx).value.encode('utf-8').strip())
                                        
                    found_header = True
                                        
                # After header row is found, process remaining player data
                elif found_header:
                        
                    # Player name
                    player_name = xl_sheet.cell(row_idx, 0).value.encode('utf-8')
					
                    # Team
                    team_name = xl_sheet.cell(row_idx, 1).value.encode('utf-8')
                    
                    # If player already exists append position to name
                    if player_name in self.position:
                        player_name = player_name + ' (' + pos + ')'
					
                    # Add team entry for player
                    self.team[player_name] = team_name
		
                    # Add entry for position lookup
                    self.position[player_name] = pos
                    
                    # Add player to position list
                    self.players[pos].append(player_name)
					
                    # Get projected points for season
                    # Avg, Low, High, Default
                    fpts = [0, 0, 0, 0]
					
                    for i in range(2,len(hdr)):
                        
                        # Split header to see if it is average, low, or high
                        hdr_split = hdr[i].split()
                        
                        # Entry is for default projected fantasy points
                        if hdr_split[0] == 'fpts':
                                
                            # Save average default projected fantasy points
                            # Average is indicated by no Low or High keyword
                            if len(hdr_split) == 1:
                                fpts[3] = xl_sheet.cell(row_idx, i).value
                                
                        else:
			       			
                            # Get projected value for category
                            projected_value = xl_sheet.cell(row_idx, i).value
                            
                            # Get points per action for category
                            points_per = self.cfg['off_pts'][hdr_split[0]]
                            
                            # Determine if this contributes towards avg, low, or high total
                            if len(hdr_split) == 1:
                                # No low or high key, this is the average
                                i_fpts = 0
                            else:
                                if (hdr_split[1] == 'Low') and (points_per >= 0):
                                    # This is a low value for a positive entry
                                    # This goes towards low projection
                                    i_fpts = 1
                                elif (hdr_split[1] == 'High') and (points_per >= 0):
                                    # This is a high value for a positive entry
                                    # This goes towards high projection
                                    i_fpts = 2
                                elif (hdr_split[1] == 'Low'):
                                    # This is a low value for a negative entry
                                    # This goes towards the high projection
                                    i_fpts = 2
                                elif (hdr_split[1] == 'High'):
                                    # This is a high value for a negative entry
                                    # This goes towards the low projection
                                    i_fpts = 1
							
                            # Accumulate projected fantasy points
                            fpts[i_fpts] = fpts[i_fpts] + projected_value*points_per
		
                    # Store projected fantasy points for this player
                    self.proj_points[pos][player_name] = fpts[0]
                    self.proj_points_low[pos][player_name] = fpts[1]
                    self.proj_points_high[pos][player_name] = fpts[2]
	
	# Import defensive projections from xls files
    def import_defensive_projections(self):

        for pos in ('DST','IDP'):
        
            filename = self.cfg['f_proj'][pos]
                
            print('Parsing ' + pos + ' Projection Data')
            
            # Create empty list of players if this is first instance of position
            if not pos in self.players:
                self.players[pos] = []
                
            # Create empty dict of projected points if this is first instance of position
            if not pos in self.proj_points:
                self.proj_points[pos] = {}
                self.proj_points_low[pos] = {}
                self.proj_points_high[pos] = {}
            
            # Get full filename
            fname = os.path.join(self.cfg['root_dir'],filename)
            fname = os.path.abspath(fname)
            
            # Read in xls workbook
            xl_workbook = xlrd.open_workbook(fname)
                
            # Read in first sheet of workbook
            xl_sheet = xl_workbook.sheet_by_index(0)
                
            # Number of columns
            num_cols = xl_sheet.ncols
                
            # Initialize flag to search for header row
            found_header = False
                
            # Iterate through rows of xls file
            for row_idx in range(0, xl_sheet.nrows):
                        
                # Scan through file looking for header row	
                if (not found_header) and (xl_sheet.cell(row_idx, 0).value.find('Rank') >= 0):
                                
                    # Header row found, save header names
                    hdr = []
                    for col_idx in range(0, num_cols): 
                                        
                        hdr.append(xl_sheet.cell(row_idx, col_idx).value.encode('utf-8').strip())
                                        
                    found_header = True
                                        
                # After header row is found, process remaining player data
                elif found_header:
                    
                    # Player name
                    first_name = xl_sheet.cell(row_idx, 2).value.encode('utf-8').strip()
                    last_name = xl_sheet.cell(row_idx, 1).value.encode('utf-8').strip()
                    player_name = first_name + ' ' + last_name
					
                    # Team
                    team_name = xl_sheet.cell(row_idx, 3).value.encode('utf-8')
					
					# If player already exists append position to name
                    if player_name in self.position:
                        player_name = player_name + ' (' + pos + ')'
					
                    # Add team entry for player
                    self.team[player_name] = team_name
		
                    # Add entry for position lookup
                    self.position[player_name] = pos
                    
                    # Add player to position list
                    self.players[pos].append(player_name)
					
                    # Get projected points for season
                    # Avg, Low, High, Default
                    fpts = [0, 0, 0, 0]
					
                    for i in range(5,len(hdr)):
                        
                        # Entry is for default projected fantasy points
                        if hdr[i] == 'Pts':
                                
                            # Save average default projected fantasy points
                            fpts[3] = xl_sheet.cell(row_idx, i).value
                                
                        else:
			       			
                            # Get projected value for category
                            projected_value = xl_sheet.cell(row_idx, i).value
                            
                            # Get points per action for category
                            points_per = self.cfg[pos+'_pts'][hdr[i]]
							
                            # Accumulate projected fantasy points
                            fpts[0] = fpts[0] + projected_value*points_per
		
		            # Save off average as high and low since there is no range data
		            fpts[1] = fpts[0]
		            fpts[2] = fpts[0]
		
                    # Store projected fantasy points for this player
                    self.proj_points[pos][player_name] = fpts[0]
                    self.proj_points_low[pos][player_name] = fpts[1]
                    self.proj_points_high[pos][player_name] = fpts[2]
		    
	
    # Import average draft positions
    def import_adp(self):
	
        print('Parsing Average Draft Position Data')
		
        # Create empty average draft position dict
        self.adp = {}
		
        # Get full filename
        fname = os.path.join(self.cfg['root_dir'],self.cfg['f_adp'])
        fname = os.path.abspath(fname)
			
        # Read in xls workbook
        xl_workbook = xlrd.open_workbook(fname)
			
        # Read in first sheet of workbook
        xl_sheet = xl_workbook.sheet_by_index(0)
			
        # Number of columns
        num_cols = xl_sheet.ncols
			
        # Initialize flag to search for header row
        found_header = False
		
        # Iterate through rows of xls file
        for row_idx in range(0, xl_sheet.nrows):
				
            # Scan through file looking for header row	
            if (not found_header) and (xl_sheet.cell(row_idx, 1).value.find('Player Name') >= 0):
				
                found_header = True
				
            # After header row is found, process remaining player data
            elif found_header:
                
                # ADP
                adp = xl_sheet.cell(row_idx, 0).value
                adp = int(adp)
					
                # Player name
                player_name = xl_sheet.cell(row_idx, 1).value.encode('utf-8')

                # Position
                player_position = xl_sheet.cell(row_idx, 2).value.encode('utf-8')
				
                # Team
                player_team = xl_sheet.cell(row_idx, 2).value.encode('utf-8')
                
                # Check if position appended version of name has been used
                appended_player_name = player_name + ' (' + player_position + ')'
                if appended_player_name in self.position:
                    # Use appended player name
                    player_name = appended_player_name

                # Add ADP to list
                self.adp[player_name] = adp

                # Add to position list if not already there
                if not player_name in self.position:
                    self.position[player_name] = player_position

                # Add to team list if not already there
                if not player_name in self.team:
                    self.team[player_name] = player_team

                # Add to players list if not already there
                if not player_position in self.players:
                    self.players[player_position] = []

                if not player_name in self.players[player_position]:
                    self.players[player_position].append(player_name)

    # Rank Players
    def rank_players(self, drafted_players, n_round, pos_weights):
	
        # Initialize available player lists to include all players
        self.avail_players = copy.deepcopy(self.players)
        self.avail_adp = copy.deepcopy(self.adp)
        self.avail_proj_points = copy.deepcopy(self.proj_points)
        self.avail_proj_points_low = copy.deepcopy(self.proj_points_low)
        self.avail_proj_points_high = copy.deepcopy(self.proj_points_high)

        # Create counters for drafted positions
        n_pos_drafted = {}
        n_pos_available = {}
        for pos in self.cfg['starters']:
            n_pos_drafted[pos] = 0
            n_pos_available[pos] = 0

        # Removed drafted players
        for player in drafted_players:
            
            n_pos_drafted[self.position[player]] += 1
            self.avail_players[self.position[player]].remove(player)
            del self.avail_proj_points[self.position[player]][player]
            del self.avail_proj_points_low[self.position[player]][player]
            del self.avail_proj_points_high[self.position[player]][player]
            del self.avail_adp[player]

        # Number of players deep to look for baseline player
        n_baseline_player = (n_round + self.cfg['baseline_depth'][n_round])*len(self.cfg['teams'])
        n_baseline_player = min(n_baseline_player, len(self.adp))
        
        # Sort available players by adp
        players_adp_sorted = sorted(self.adp, key=self.adp.get)

        # Number of available players in each position to baseline depth
        for i in range(0, n_baseline_player):
        
            player = players_adp_sorted[i]

            # Increment available position counter
            n_pos_available[self.position[player]] += 1

        # Calculate baseline depth for each position
        pos_baseline = {}
        vbd_baseline = {}
        self.vbd = {}
        for pos in self.cfg['starters']:

            self.vbd[pos] = {}
            
            # Saturate baseline at the max number of players at that position
            n_pos_available[pos] = min(n_pos_available[pos], 
                                       self.cfg['draft_max'][pos]*len(self.cfg['teams']))
            

            # Get baseline depth of each position
            pos_baseline[pos] = n_pos_available[pos] - n_pos_drafted[pos]

            # Make sure depth is at least 1 so vbd is scored for a minimum of
            # 1 person
            pos_baseline[pos] = max(pos_baseline[pos], 1)
            
            # Make sure baseline isn't longer than total available players
            pos_baseline[pos] = min(pos_baseline[pos], len(self.avail_proj_points[pos])-1)

            # Calculate VBD if projected points are available
            if pos in self.avail_proj_points:

                # Sort players in position group from highest to lowest by avg fpts
                players_fpts_sorted = sorted(self.avail_proj_points[pos], key=self.avail_proj_points[pos].get, reverse=True)

                # Get basline score
                vbd_baseline[pos] = self.proj_points[pos][players_fpts_sorted[pos_baseline[pos]]]

                # Calculate vbd for all available players in position
                for player in self.avail_proj_points[pos]:
                    
                    if player in self.avail_players[pos]:
                    
                        vbd_avg = self.avail_proj_points[pos][player] - vbd_baseline[pos]
                        vbd_low = self.avail_proj_points_low[pos][player] - vbd_baseline[pos]
                        vbd_high = self.avail_proj_points_high[pos][player] - vbd_baseline[pos]
                        self.vbd[pos][player] = (self.cfg['distribution_weight'][0]*vbd_avg +
                                                 self.cfg['distribution_weight'][1]*vbd_low +
                                                 self.cfg['distribution_weight'][2]*vbd_high)
        
        # Generate ranking scores for all players
        self.ranking_score = {}
        for pos in self.cfg['starters']:

            # Ignore positions with negative weights
            if pos_weights[pos] > 0:

                # Loop through players in position
                for player in self.vbd[pos]:

                    # Only rank players with non-negative vbd
                    # Negative VBD is meaningless since it is below the baseline
                    if self.vbd[pos][player] >= 0.0:
                        self.ranking_score[player] = self.vbd[pos][player]


        # Sort by ranking score to get rank
        self.rank = sorted(self.ranking_score, key=self.ranking_score.get, reverse=True)
       
    # Get value based draft score 
    def get_vbd(self, player):
        
        return self.vbd[self.position[player]][player]
        
    # Get average expected points per game
    def get_fpts_avg(self, player):
    
        return self.proj_points_low[self.position[player]][player]/self.cfg['num_games_per_season']
        
    # Get low expected points per game
    def get_fpts_low(self, player):
    
        return self.proj_points_low[self.position[player]][player]/self.cfg['num_games_per_season']
        
    # Get high expected points per game
    def get_fpts_high(self, player):
    
        return self.proj_points_high[self.position[player]][player]/self.cfg['num_games_per_season']

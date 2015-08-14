# playerdatabase.py
#
# Player database class.
#
# Don Nguyen
# Aug, 2015

import os
import xlrd
import ipdb

class PlayerDatabase:

    # Constructor
    def __init__(self, cfg):
	
        self.cfg = cfg

        # Import player projection data
        self.import_player_projections()
        
        # Import average draft position data
        self.import_adp()
        
        # Initialize empty teams dict
        self.teams = {}
	
        self.players['IDP'] = []

    # Import player projections from xls files
    def import_player_projections(self):
		
        f_projections = {}
        f_projections['QB'] = 'FantasyPros_Fantasy_Football_Rankings_QB.xls'
        f_projections['RB'] = 'FantasyPros_Fantasy_Football_Rankings_RB.xls'
        f_projections['WR'] = 'FantasyPros_Fantasy_Football_Rankings_WR.xls'
        f_projections['TE'] = 'FantasyPros_Fantasy_Football_Rankings_TE.xls'
        f_projections['K']  = 'FantasyPros_Fantasy_Football_Rankings_K.xls'
        
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

        for pos, filename in f_projections.items():
                
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
                            points_per = self.cfg['pts'][hdr_split[0]]
                            
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
	
    # Import average draft positions
    def import_adp(self):
	
        print('Parsing Average Draft Position Data')
	
        f_adp = 'FantasyPros_2015_Overall_ADP_Rankings.xls'
		
        # Create empty average draft position dict
        self.adp = {}
		
        # Get full filename
        fname = os.path.join(self.cfg['root_dir'],f_adp)
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
            if (not found_header) and (xl_sheet.cell(row_idx, 0).value.find('ADP') >= 0):
				
                found_header = True
				
            # After header row is found, process remaining player data
            elif found_header:
					
                # ADP
		adp = xl_sheet.cell(row_idx, 0).value
					
                # Player name
                player_name = xl_sheet.cell(row_idx, 1).value.encode('utf-8')

                # Position
                player_position = xl_sheet.cell(row_idx, 2).value.encode('utf-8')
				
                # Team
                player_team = xl_sheet.cell(row_idx, 2).value.encode('utf-8')

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
        self.avail_players = self.players
        self.avail_adp = self.adp

        # Create counters for drafted positions
        n_pos_drafted = {}
        n_pos_available = {}
        for pos in self.cfg['starters']:
            n_pos_drafted[pos] = 0
            n_pos_available[pos] = 0

        # Removed drafted players
        for player in drafted_players:
        
            n_pos_drafted[self.position[player]] += 1
            del self.avail_players[self.position[player]][player]
            del self.avail_adp[player]

        # Number of players deep to look for baseline player
        n_baseline_player = (n_round + self.cfg['baseline_depth'][n_round])*len(self.cfg['teams'])

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
        vbd = {}
        vbd_low = {}
        vbd_high = {}
        for pos in self.cfg['starters']:

            vbd[pos] = {}
            vbd_low[pos] = {}
            vbd_high[pos] = {}

            # Get baseline depth of each position
            pos_baseline[pos] = n_pos_available[pos] - n_pos_drafted[pos]

            # Make sure depth is not negative
            pos_baseline[pos] = max(pos_baseline[pos], 0)

            # Calculate VBD if projected points are available
            if pos in self.proj_points:

                # Sort players in position group from highest to lowest by avg fpts
                players_fpts_sorted = sorted(self.proj_points[pos], key=self.proj_points[pos].get, reverse=True)

                # Get basline score
                vbd_baseline[pos] = self.proj_points[pos][players_fpts_sorted[pos_baseline[pos]]]

                # Calculate vbd for all players in position
                for player in self.proj_points[pos]:

                    vbd[pos][player] = self.proj_points[pos][player] - vbd_baseline[pos]
                    vbd_low[pos][player] = self.proj_points_low[pos][player] - vbd_baseline[pos]
                    vbd_high[pos][player] = self.proj_points_high[pos][player] - vbd_baseline[pos]

                    # Saturate at 0
                    vbd[pos][player] = max(vbd[pos][player], 0.0)
                    vbd_low[pos][player] = max(vbd_low[pos][player], 0.0)
                    vbd_high[pos][player] = max(vbd_high[pos][player], 0.0)

            else:

                for player in self.players[pos]:

                    vbd[pos][player] = 0.0
                    vbd_low[pos][player] = 0.0
                    vbd_high[pos][player] = 0.0
                    
        # Generate ranking scores for all players
        self.ranking_score = {}
        for pos in self.cfg['starters']:

            # Ignore positions with negative weights
            if pos_weights[pos] > 0:

                # Loop through players in position
                for player in vbd[pos]:

                    self.ranking_score[player] = (self.cfg['distribution_weight'][0]*vbd[pos][player] +
                                                  self.cfg['distribution_weight'][1]*vbd_low[pos][player] +
                                                  self.cfg['distribution_weight'][2]*vbd_high[pos][player])


        # Sort by ranking score to get rank
        self.rank = sorted(self.ranking_score, key=self.ranking_score.get, reverse=True)

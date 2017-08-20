# playerdatabase.py
#
# Player database class.
#
# Don Nguyen
# Aug, 2015

import os
import xlrd
import csv
import copy
import pdb

class PlayerDatabase:
    
    # Constructor
    def __init__(self, cfg):
	
        self.cfg = cfg

        # Import player projection data
        #self.import_player_projections()
        self.import_player_projections_csv()
        
        # Import defensive projection data
        self.import_defensive_projections_csv()
        
        # Import average draft position data
        self.import_adp_csv()
        
        # Import expert consensus ranking data
        self.import_ecr_csv()

    # Import player projections from csv files
    def import_player_projections_csv(self):
        
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
        
        # Generate headers
        headers = {}
        headers['QB'] = ['player','team','pass_att','pass_cmp','pass_yds','pass_tds','pass_ints','rush_att','rush_yds','rush_tds','fumbles','fpts']
        headers['RB'] = ['player','team','rush_att','rush_yds','rush_tds','rec_att','rec_yds','rec_tds','fumbles','fpts']
        headers['WR'] = ['player','team','rush_att','rush_yds','rush_tds','rec_att','rec_yds','rec_tds','fumbles','fpts']
        headers['TE'] = ['player','team','rec_att','rec_yds','rec_tds','fumbles','fpts']
        headers['K'] = ['player','team','fg','fga','xpt','fpts']
        
        for pos in ('QB','RB','WR','TE','K'):
        
            filename = self.cfg['f_proj'][pos]
                
            print('Parsing ' + pos + ' Projection Data')
                
            # Get full filename
            fname = os.path.join(self.cfg['root_dir'],filename)
            fname = os.path.abspath(fname)
                
            # Initialize flag to search for header row
            found_header = False
                
            # Create empty list of players
            self.players[pos] = []

            # Create empty dict of projected points
            self.proj_points[pos] = {}
            self.proj_points_low[pos] = {}
            self.proj_points_high[pos] = {}
            
            # Open csv file
            with open(fname) as csv_file:
            
                # Create csv reader handle
                csv_data = csv.reader(csv_file, delimiter=',', dialect=csv.excel_tab)
                
                # Iterate through rows of csv file
                projections = {}
                for row in csv_data:
                        
                    # Scan through file looking for header row	
                    if row[0] == 'Player':
                                
                        # Header row found, skip line
                        continue
                                        
                    # After header row is found, process remaining player data
                    else:
                        
                        # Player name
                        player_name = row[0]
                        
                        if player_name != '':
					    
                            # Team
                            team_name = row[1]
                            
                            # The row with the player's name is the average data
                            prob = 'avg'
                        
                            # If player already exists append position to name
                            if player_name in self.position:
                                player_name = player_name + ' (' + pos + ')'                            
					        
                            # Add team entry for player
                            self.team[player_name] = team_name
		                    
                            # Add entry for position lookup
                            self.position[player_name] = pos
                            
                            # Add player to position list
                            self.players[pos].append(player_name)
                            
                            # Save player name
                            last_player_name = player_name
                            
                        else:
                        
                            # Extension of last player's data
                            player_name = last_player_name
                            
                            # Probability
                            prob = row[1]
                        
                        # Initialize point counter to 0
                        fpts = 0
					    
                        for i in range(2,len(headers[pos])):
                        
                            if headers[pos][i] != 'fpts':
                            
			                    # Get projected value for category
                                projected_value = float(row[i].replace(',',''))
                                
                                # Get points per action for category
                                points_per = self.cfg['off_pts'][headers[pos][i]]
						        
                                # Accumulate projected fantasy points
                                fpts = fpts + projected_value*points_per
		                        
                        # Store projected fantasy points for this player
                        if prob == 'avg':
                            self.proj_points[pos][player_name] = fpts
                        elif prob == 'low':
                            self.proj_points_low[pos][player_name] = fpts
                        elif prob == 'high':
                            self.proj_points_high[pos][player_name] = fpts

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
	
	# Import defensive projections from csv files
    def import_defensive_projections_csv(self):

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
            
            # Open csv file
            with open(fname) as csv_file:
        
                # Create csv reader handle
                csv_data = csv.reader(csv_file, delimiter=',', dialect=csv.excel_tab)
                
                # Initialize flag to search for header row
                found_header = False
                
                # Iterate through rows of csv file
                for row in csv_data:
                        
                    # Scan through file looking for header row	
                    if (not found_header) and (row[0] == 'Rank'):
                                
                        # Header row found, save header names
                        hdr = []
                        for col_idx in range(0, len(row)): 
                        
                            hdr.append(row[col_idx])
                                        
                        found_header = True
                                        
                    # After header row is found, process remaining player data
                    elif found_header:
                    
                        # Player name
                        first_name = row[2]
                        last_name = row[1]
                        player_name = first_name + ' ' + last_name
					
                        # Team
                        team_name = row[3]
					
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
                                fpts[3] = row[i]
                                
                            else:
			       			
                                # Get projected value for category
                                projected_value = float(row[i])
                            
                                # Get points per action for category
                                points_per = self.cfg[pos+'_pts'][hdr[i]]
							
                            #    Accumulate projected fantasy points
                                fpts[0] = fpts[0] + projected_value*points_per
		
		                # Save off average as high and low since there is no range data
		                fpts[1] = fpts[0]
		                fpts[2] = fpts[0]
		
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
    def import_adp_csv(self):
	
        print('Parsing Average Draft Position Data')
		
        # Create empty average draft position dict
        self.adp = {}
		
        # Get full filename
        fname = os.path.join(self.cfg['root_dir'],self.cfg['f_adp'])
        fname = os.path.abspath(fname)
			
		# Open csv file
        with open(fname) as csv_file:
        
            # Create csv reader handle
            csv_data = csv.reader(csv_file, delimiter=',', dialect=csv.excel_tab)
                
            # Initialize flag to search for header row
            found_header = False
                
            # Iterate through rows of csv file
            for row in csv_data:
				
                # Scan through file looking for header row	
                if (not found_header) and (row[1] == 'Player'):
				
                    found_header = True
				
                # After header row is found, process remaining player data
                elif found_header:
                
                    # ADP
                    adp = row[0]
                    adp = int(adp)
					
                    # Player name
                    player_name = row[1]

                    # Position
                    player_position = row[4]
                    if player_position[0] == 'K':
                        player_position = 'K'
                    elif player_position[0:3] == 'DST':
                        player_position = 'DST'
                    else:
                        player_position = player_position[0:2]
				
                    # Team
                    player_team = row[2]
                
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
                    
                    # Add to points list if not already there
                    if not player_position in self.proj_points:
                        self.proj_points[player_position] = {}
                
                    if not player_name in self.proj_points[player_position]:
                        self.proj_points[player_position][player_name] = 0.0
                
                    if not player_position in self.proj_points_low:
                        self.proj_points_low[player_position] = {}
                
                    if not player_name in self.proj_points_low[player_position]:
                        self.proj_points_low[player_position][player_name] = 0.0
                
                    if not player_position in self.proj_points_high:
                        self.proj_points_high[player_position] = {}
                
                    if not player_name in self.proj_points_high[player_position]:
                        self.proj_points_high[player_position][player_name] = 0.0
	
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
                if player_position[0] == 'K':
                    player_position = 'K'
                elif player_position[0:3] == 'DST':
                    player_position = 'DST'
                else:
                    player_position = player_position[0:2]
				
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
                    
                # Add to points list if not already there
                if not player_position in self.proj_points:
                    self.proj_points[player_position] = {}
                
                if not player_name in self.proj_points[player_position]:
                    self.proj_points[player_position][player_name] = 0.0
                
                if not player_position in self.proj_points_low:
                    self.proj_points_low[player_position] = {}
                
                if not player_name in self.proj_points_low[player_position]:
                    self.proj_points_low[player_position][player_name] = 0.0
                
                if not player_position in self.proj_points_high:
                    self.proj_points_high[player_position] = {}
                
                if not player_name in self.proj_points_high[player_position]:
                    self.proj_points_high[player_position][player_name] = 0.0

    # Import expert consensus rankings
    def import_ecr_csv(self):
	
        print('Parsing Expert Consensus Ranking Data')
		
        # Create empty expert consensus ranking dict
        self.ecr = {}
		
        # Get full filename
        fname = os.path.join(self.cfg['root_dir'],self.cfg['f_ecr'])
        fname = os.path.abspath(fname)
			
		# Open csv file
        with open(fname) as csv_file:
        
            # Create csv reader handle
            csv_data = csv.reader(csv_file, delimiter=',', dialect=csv.excel_tab)
                
            # Initialize flag to search for header row
            found_header = False
                
            # Iterate through rows of csv file
            for row in csv_data:
				
                # Scan through file looking for header row	
                if (not found_header) and (row[1] == 'Player'):
				
                    found_header = True
				
                # After header row is found, process remaining player data
                elif found_header:
                
                    # ECR
                    ecr = row[0]
                    ecr = int(ecr)
					
                    # Player name
                    player_name = row[1]

                    # Position
                    player_position = row[3]
                    if player_position[0] == 'K':
                        player_position = 'K'
                    elif player_position[0:3] == 'DST':
                        player_position = 'DST'
                    else:
                        player_position = player_position[0:2]
				
                    # Team
                    player_team = row[2]
                
                    # Check if position appended version of name has been used
                    appended_player_name = player_name + ' (' + player_position + ')'
                    if appended_player_name in self.position:
                        # Use appended player name
                        player_name = appended_player_name

                    # Add ECR to list
                    self.ecr[player_name] = ecr

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
                    
                    # Add to points list if not already there
                    if not player_position in self.proj_points:
                        self.proj_points[player_position] = {}
                
                    if not player_name in self.proj_points[player_position]:
                        self.proj_points[player_position][player_name] = 0.0
                
                    if not player_position in self.proj_points_low:
                        self.proj_points_low[player_position] = {}
                
                    if not player_name in self.proj_points_low[player_position]:
                        self.proj_points_low[player_position][player_name] = 0.0
                
                    if not player_position in self.proj_points_high:
                        self.proj_points_high[player_position] = {}
                
                    if not player_name in self.proj_points_high[player_position]:
                        self.proj_points_high[player_position][player_name] = 0.0

    # Import expert consensus rankings
    def import_ecr(self):
	
        print('Parsing Expert Consensus Ranking Data')
		
        # Create empty expert consensus ranking dict
        self.ecr = {}
		
        # Get full filename
        fname = os.path.join(self.cfg['root_dir'],self.cfg['f_ecr'])
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
                
                # ECR
                ecr = xl_sheet.cell(row_idx, 0).value
                ecr = int(ecr)
					
                # Player name
                player_name = xl_sheet.cell(row_idx, 1).value.encode('utf-8')

                # Position
                player_position = xl_sheet.cell(row_idx, 2).value.encode('utf-8')
                if player_position[0] == 'K':
                    player_position = 'K'
                elif player_position[0:3] == 'DST':
                    player_position = 'DST'
                else:
                    player_position = player_position[0:2]
				
                # Team
                player_team = xl_sheet.cell(row_idx, 2).value.encode('utf-8')
                
                # Check if position appended version of name has been used
                appended_player_name = player_name + ' (' + player_position + ')'
                if appended_player_name in self.position:
                    # Use appended player name
                    player_name = appended_player_name

                # Add ECR to list
                self.ecr[player_name] = ecr

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
                    
                # Add to points list if not already there
                if not player_position in self.proj_points:
                    self.proj_points[player_position] = {}
                
                if not player_name in self.proj_points[player_position]:
                    self.proj_points[player_position][player_name] = 0.0
                
                if not player_position in self.proj_points_low:
                    self.proj_points_low[player_position] = {}
                
                if not player_name in self.proj_points_low[player_position]:
                    self.proj_points_low[player_position][player_name] = 0.0
                
                if not player_position in self.proj_points_high:
                    self.proj_points_high[player_position] = {}
                
                if not player_name in self.proj_points_high[player_position]:
                    self.proj_points_high[player_position][player_name] = 0.0

    # Rank Players
    def rank_players(self, draftteams, drafted_players, n_round, pos_weights, n_pick):
        
        # Initialize available player lists to include all players
        self.avail_players = copy.deepcopy(self.players)
        self.avail_adp = copy.deepcopy(self.adp)
        self.avail_ecr = copy.deepcopy(self.ecr)
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
            del self.avail_ecr[player]

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
            
        # Force IDP expected to number of teams since there are none in the ADP
        n_pos_available['IDP'] = len(self.cfg['teams'])

        # Calculate baseline depth for each position
        pos_baseline = {}
        vbd_baseline = {}
        self.vbd = {}
        for pos in self.cfg['starters']:

            self.vbd[pos] = {}
            
            # Calculate max number of players expected to be drafted at position
            max_expected_drafted = 0
            for team in draftteams.teams:
                # Get position counts for team
                pos_counts = draftteams.teams[team].get_pos_counts()
                
                # Increment the max of the actual drafted players or the expected max
                max_expected_drafted = (max_expected_drafted + 
                    max(pos_counts[pos],self.cfg['draft_max'][pos]))
            
            # Saturate baseline at the max number of players at that position
            n_pos_available[pos] = min(n_pos_available[pos], max_expected_drafted)
            
            # Get baseline depth of each position
            pos_baseline[pos] = n_pos_available[pos] - n_pos_drafted[pos]

            # Make sure depth is at least 1 so vbd is scored for a minimum of
            # 1 person
            pos_baseline[pos] = max(pos_baseline[pos], 1)
            
            # Make sure baseline isn't longer than total available players
            pos_baseline[pos] = min(pos_baseline[pos], len(self.avail_proj_points[pos])-1)

            # Calculate VBD if projected points are available
            if pos in self.avail_proj_points:
            
                # Compute weighted expected points
                players_fpts_weighted = {}
                for player in self.avail_proj_points[pos]:
                    players_fpts_weighted[player] = (self.cfg['distribution_weight'][0]*self.avail_proj_points[pos][player] +
                                                     self.cfg['distribution_weight'][1]*self.avail_proj_points_low[pos][player] +
                                                     self.cfg['distribution_weight'][2]*self.avail_proj_points_high[pos][player])
                
                # Sort players in position group from highest to lowest by avg fpts
                players_fpts_sorted = sorted(players_fpts_weighted, key=players_fpts_weighted.get, reverse=True)
                                
                # Get basline score
                vbd_baseline[pos] = players_fpts_weighted[players_fpts_sorted[pos_baseline[pos]]]

                # Calculate vbd for all available players in position
                for player in self.avail_proj_points[pos]:
                    
                    if player in self.avail_players[pos]:
                    
                        self.vbd[pos][player] = players_fpts_weighted[player] - vbd_baseline[pos]
        
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
                        self.ranking_score[player] = self.vbd[pos][player]*pos_weights[pos]
                        
                        # Apply adp weight if available
                        if player in self.adp:
                            self.ranking_score[player] = self.ranking_score[player] + (n_pick - self.adp[player])*self.cfg['adp_bias']


        # Sort by ranking score to get rank
        self.rank = sorted(self.ranking_score, key=self.ranking_score.get, reverse=True)
               
    # Get value based draft score 
    def get_vbd(self, player):
        
        return self.vbd[self.position[player]][player]
        
    # Get rankings score
    def get_ranking_score(self, player):
    
        return self.ranking_score[player]
        
    # Get average expected points per game
    def get_fpts_avg(self, player):
    
        return self.proj_points[self.position[player]][player]/self.cfg['num_games_per_season']
        
    # Get low expected points per game
    def get_fpts_low(self, player):
    
        return self.proj_points_low[self.position[player]][player]/self.cfg['num_games_per_season']
        
    # Get high expected points per game
    def get_fpts_high(self, player):
    
        return self.proj_points_high[self.position[player]][player]/self.cfg['num_games_per_season']

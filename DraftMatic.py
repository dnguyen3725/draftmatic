# DraftMatic.py
#
# Program to help to achieve universal fantasy football dominance.
# Aug, 2015

import sys
import os
import xlrd

# Player Database Class
#######################

class PlayerDatabase:

	# Constructor
	def __init__(self, root_dir, pts):
	
		# Import player projection data
		self.import_player_projections(root_dir, pts)
		
		# Import average draft position data
		self.import_adp(root_dir)
		
		# Initialize empty teams dict
		self.teams = {}
	
	# Import player projections from xls files
	def import_player_projections(self, root_dir, pts):
		
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
		
		for pos, filename in f_projections.items():
			
			print('Parsing ' + pos + ' Projection Data')
			
			# Get full filename
			fname = os.path.join(root_dir,filename)
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
							points_per = pts[hdr_split[0]]
							
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
								if (hdr_split[1] == 'Low'):
									# This is a low value for a negative entry
									# This goes towards the high projection
									i_fpts = 2
								elif (hdr_split[1] == 'High'):
									# This is a high value for a negative entry
									# This goes towards the low projection
									i_fpts = 1
							
							# Accumulate projected fantasy points
							fpts[i_fpts] = fpts[i_fpts] + projected_value*points_per
					
					self.proj_points[player_name] = fpts
					
	# Import average draft positions
	def import_adp(self, root_dir):
	
		print('Parsing Average Draft Position Data')
	
		f_adp = 'FantasyPros_2015_Overall_ADP_Rankings.xls'
		
		# Create empty average draft position dict
		self.adp = {}
		
		# Get full filename
		fname = os.path.join(root_dir,f_adp)
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
				
				self.adp[player_name] = adp
				
	# Rank Players
	def rank_players(self):
	
		# Initialize available player lists to include all players
		self.avail_players = self.players
		self.avail_adp = self.adp
		
		# Remove drafted players
		for team in self.teams:
			for pos in self.teams[team]:
				for player in self.teams[team][pos]:
					del self.avail_players[pos][player]
					del avail_adp[player]
					
		print self.avail_players
					
	# Initialize team
	def initialize_team(self, team):
	
		# Add empty dict for team
		self.teams[team] = {}
		
		# Add empty players list for each position
		for pos in self.players:
		
			self.teams[team][pos] = []
	
# Main Function Calls
#######################		 

# Set configuration parameters
def set_config():
    
    # Directory of team lists
    root_dir = '2015_data'
    
    # Teams
    teams = []
    teams.append('JoshHathaway')
    teams.append('Don')
    teams.append('Nick')
    teams.append('Cesar')
    teams.append('Rosa')
    teams.append('Robert')
    teams.append('Mitchell')
    teams.append('Josh')
    teams.append('Joe')
    teams.append('Tony')
    teams.append('Travis')
    teams.append('Zach')
    
    # Weight deduction per excess player
    weight_decrement = 0.2
    
    # Number of starters
    starters = {}
    starters['QB'] = 1
    starters['RB'] = 2
    starters['WR'] = 3
    starters['TE'] = 1
    starters['K'] = 1
    starters['ID'] = 1
    
    # League scoring (pts/unit)
    pts = {}
    pts['pass_att'] = 0.0
    pts['pass_cmp'] = 0.0
    pts['pass_yds'] = 1.0/25.0
    pts['pass_tds'] = 4.0
    pts['pass_ints'] = -1.0
    pts['rush_att'] = 0.0
    pts['rush_yds'] = 1.0/10.0
    pts['rush_tds'] = 6.0
    pts['rec_att'] = 0.0
    pts['rec_yds'] = 1.0/10.0
    pts['rec_tds'] = 6.0
    pts['fumbles'] = -2.0
    
    # Include Kicker scoring
    if True:
        pts['fg'] = 3.0
        pts['fga'] = 0.0
        pts['xpt'] = 1.0
    else:
        pts['fg'] = 0.0
        pts['fga'] = 0.0
        pts['xpt'] = 0.0
    
    # Include Individual defensive scoring
    if True:
        pts['sacks'] = 2.0
        pts['force_fumb'] = 0.0
        pts['rec_fumb'] = 0.0
        pts['int'] = 3.0
        pts['pass_def'] = 0.0
        pts['tackles'] = 1.0
        pts['assists'] = 0.5
        pts['def_td'] = 6.0
    else:
        pts['sacks'] = 0.0
        pts['force_fumb'] = 0.0
        pts['rec_fumb'] = 0.0
        pts['int'] = 0.0
        pts['pass_def'] = 0.0
        pts['tackles'] = 0.0
        pts['assists'] = 0.0
        pts['def_td'] = 0.0
        
    # Return tuple of configuration parameters
    return (root_dir, teams, weight_decrement, starters, pts)

# Main Loop
def main():

	# Get configuration parameters
	cfg = set_config()
	root_dir = cfg[0]
	teams = cfg[1]
	weight_decrement = cfg[2]
	starters = cfg[3]
	pts = cfg[4]
	
	# Get Player Database
	player_db = PlayerDatabase(root_dir, pts)
	
	# Add teams to database
	for team in teams:
		player_db.initialize_team(team)
	
	# Startup console
	print '-'*50
	print 'Draft Time Bitches!'
	print '-'*50
	
	# Main Loop
	while True:
	
		# Rank players
		player_db.rank_players()
	
		# Prompt user for pick
		print '(''exit'' to quit)'
		console_inp = raw_input('Enter Pick: ')
		
		# Exit on command
		if console_inp.find('exit') >= 0:
			break

if __name__ == '__main__':
  main()

# DraftMatic.py
#
# Program to help to achieve universal fantasy football dominance.
#
# Don Nguyen
# Aug, 2015

import sys
import os
from playerdatabase import PlayerDatabase

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

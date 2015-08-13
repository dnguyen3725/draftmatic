# DraftMatic.py
#
# Program to help to achieve universal fantasy football dominance.
#
# Don Nguyen
# Aug, 2015

import sys
import os
from playerdatabase import PlayerDatabase
from draftteam import DraftTeams

# Set configuration parameters
def set_config():
    
    cfg = {}

    # Directory of player projection data
    cfg['root_dir'] = '2015_data'
    
    # Draft teams in order
    cfg['teams'] = []
    cfg['teams'].append('JoshHathaway')
    cfg['teams'].append('Don')
    cfg['teams'].append('Nick')
    cfg['teams'].append('Cesar')
    cfg['teams'].append('Rosa')
    cfg['teams'].append('Robert')
    cfg['teams'].append('Mitchell')
    cfg['teams'].append('Josh')
    cfg['teams'].append('Joe')
    cfg['teams'].append('Tony')
    cfg['teams'].append('Travis')
    cfg['teams'].append('Zach')
    
    # Number of draft rounds
    cfg['num_rounds'] = 16

    # Number of starters
    cfg['starters'] = {}
    cfg['starters']['QB'] = 1
    cfg['starters']['RB'] = 2
    cfg['starters']['WR'] = 3
    cfg['starters']['TE'] = 1
    cfg['starters']['K'] = 1
    cfg['starters']['IDP'] = 1
    cfg['starters']['DST'] = 1
    
    # League scoring (pts/unit)
    cfg['pts'] = {}
    cfg['pts']['pass_att'] = 0.0
    cfg['pts']['pass_cmp'] = 0.0
    cfg['pts']['pass_yds'] = 1.0/25.0
    cfg['pts']['pass_tds'] = 4.0
    cfg['pts']['pass_ints'] = -1.0
    cfg['pts']['rush_att'] = 0.0
    cfg['pts']['rush_yds'] = 1.0/10.0
    cfg['pts']['rush_tds'] = 6.0
    cfg['pts']['rec_att'] = 0.0
    cfg['pts']['rec_yds'] = 1.0/10.0
    cfg['pts']['rec_tds'] = 6.0
    cfg['pts']['fumbles'] = -2.0
    
    # Include Kicker scoring
    if True:
        cfg['pts']['fg'] = 3.0
        cfg['pts']['fga'] = 0.0
        cfg['pts']['xpt'] = 1.0
    else:
        cfg['pts']['fg'] = 0.0
        cfg['pts']['fga'] = 0.0
        cfg['pts']['xpt'] = 0.0
    
    # Include Individual defensive scoring
    if True:
        cfg['pts']['sacks'] = 2.0
        cfg['pts']['force_fumb'] = 0.0
        cfg['pts']['rec_fumb'] = 0.0
        cfg['pts']['int'] = 3.0
        cfg['pts']['pass_def'] = 0.0
        cfg['pts']['tackles'] = 1.0
        cfg['pts']['assists'] = 0.5
        cfg['pts']['def_td'] = 6.0
    else:
        cfg['pts']['sacks'] = 0.0
        cfg['pts']['force_fumb'] = 0.0
        cfg['pts']['rec_fumb'] = 0.0
        cfg['pts']['int'] = 0.0
        cfg['pts']['pass_def'] = 0.0
        cfg['pts']['tackles'] = 0.0
        cfg['pts']['assists'] = 0.0
        cfg['pts']['def_td'] = 0.0
        
    # Number of rounds to establish baseline depth
    cfg['baseline_depth'] = []
    cfg['baseline_depth'].append(8) # 1
    cfg['baseline_depth'].append(7) # 2
    cfg['baseline_depth'].append(6) # 3
    cfg['baseline_depth'].append(5) # 4
    cfg['baseline_depth'].append(4) # 5
    cfg['baseline_depth'].append(4) # 6
    cfg['baseline_depth'].append(4) # 7
    cfg['baseline_depth'].append(4) # 8
    cfg['baseline_depth'].append(4) # 9
    cfg['baseline_depth'].append(4) # 10
    cfg['baseline_depth'].append(4) # 11
    cfg['baseline_depth'].append(4) # 12
    cfg['baseline_depth'].append(4) # 13
    cfg['baseline_depth'].append(3) # 14
    cfg['baseline_depth'].append(2) # 15
    cfg['baseline_depth'].append(1) # 16

    # Weight deduction per excess player
    cfg['weight_decrement'] = 0.2

    # Return tuple of configuration parameters
    return cfg

# Main Loop
def main():
    
    # Get configuration parameters
    cfg = set_config()
    
    # Get Player Database
    player_db = PlayerDatabase(cfg)
    
    # Add teams to database
    draftteams = DraftTeams(cfg)
    for team in cfg['teams']:
        draftteams.add_team(team)
    
    # Startup console
    print '-'*50
    print 'DraftMatic!!!'
    print '-'*50
    print ''
    
    # Main Loop
    while True:
	
        # Get round number
        n_round = draftteams.round()

        # Print round number
        print '-'*50
        print 'Round {}'.format(n_round+1)
        print '-'*50
        print ''

        # Get list of drafted players
        drafted_players = draftteams.drafted_players()

        # Rank players
        player_db.rank_players(drafted_players, n_round)
	
        # Prompt user for pick
        print '(''exit'' to quit)'
        console_inp = raw_input('Enter Pick: ')
		
        # Exit on command
        if console_inp.find('exit') >= 0:
            break

if __name__ == '__main__':
  main()

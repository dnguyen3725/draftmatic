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
from yhandler import YHandler
import pdb

# Set configuration parameters
def set_config():
    
    cfg = {}

    # Directory of player projection data
    cfg['root_dir'] = '2015_data'
    
    # Directory of draft team data
    cfg['team_dir'] = '2015_teams'
    
    # Player projection files
    cfg['f_proj'] = {}
    cfg['f_proj']['QB'] = 'FantasyPros_Fantasy_Football_Rankings_QB.xls'
    cfg['f_proj']['RB'] = 'FantasyPros_Fantasy_Football_Rankings_RB.xls'
    cfg['f_proj']['WR'] = 'FantasyPros_Fantasy_Football_Rankings_WR.xls'
    cfg['f_proj']['TE'] = 'FantasyPros_Fantasy_Football_Rankings_TE.xls'
    cfg['f_proj']['K']  = 'FantasyPros_Fantasy_Football_Rankings_K.xls'
    cfg['f_proj']['DST']  = 'FantasySharks_DST.xls'
    cfg['f_proj']['IDP']  = 'FantasySharks_IDP.xls'
    
    # Average draft position
    cfg['f_adp'] = 'FantasyPros_2015_Preseason_Overall_Rankings.xls'
    
    # Draft teams in order
    cfg['teams'] = []
    cfg['teams'].append('1')
    cfg['teams'].append('Don')
    cfg['teams'].append('3')
    cfg['teams'].append('4')
    cfg['teams'].append('5')
    cfg['teams'].append('6')
    cfg['teams'].append('7')
    cfg['teams'].append('8')
    cfg['teams'].append('9')
    cfg['teams'].append('10')
    cfg['teams'].append('11')
    cfg['teams'].append('12')
    
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
    
    # Offensive player scoring (pts/unit)
    cfg['off_pts'] = {}
    cfg['off_pts']['pass_att'] = 0.0
    cfg['off_pts']['pass_cmp'] = 0.0
    cfg['off_pts']['pass_yds'] = 1.0/25.0
    cfg['off_pts']['pass_tds'] = 4.0
    cfg['off_pts']['pass_ints'] = -1.0
    cfg['off_pts']['rush_att'] = 0.0
    cfg['off_pts']['rush_yds'] = 1.0/10.0
    cfg['off_pts']['rush_tds'] = 6.0
    cfg['off_pts']['rec_att'] = 0.0
    cfg['off_pts']['rec_yds'] = 1.0/10.0
    cfg['off_pts']['rec_tds'] = 6.0
    cfg['off_pts']['fumbles'] = -2.0
    
    # Kicker scoring
    cfg['off_pts']['fg'] = 3.0
    cfg['off_pts']['fga'] = 0.0
    cfg['off_pts']['xpt'] = 1.0
    
    # Defense/Special Teams Scoring
    cfg['DST_pts'] = {}
    cfg['DST_pts']['Yds Allowed'] = 0.0
    cfg['DST_pts']['0-99'] = 0.0
    cfg['DST_pts']['100-199'] = 0.0
    cfg['DST_pts']['200-299'] = 0.0
    cfg['DST_pts']['300-349'] = 0.0
    cfg['DST_pts']['350-399'] = 0.0
    cfg['DST_pts']['400-449'] = 0.0
    cfg['DST_pts']['450-499'] = 0.0
    cfg['DST_pts']['500-549'] = 0.0
    cfg['DST_pts']['550+'] = 0.0
    cfg['DST_pts']['Pts Agn'] = 0.0
    cfg['DST_pts']['0'] = 10
    cfg['DST_pts']['1-6'] = 7
    cfg['DST_pts']['7-13'] = 4
    cfg['DST_pts']['14-17'] = 1
    cfg['DST_pts']['18-20'] = 1
    cfg['DST_pts']['21-27'] = 0
    cfg['DST_pts']['28-34'] = -1
    cfg['DST_pts']['35-45'] = -4
    cfg['DST_pts']['46+'] = -4
    cfg['DST_pts']['Scks'] = 1
    cfg['DST_pts']['Int'] = 2
    cfg['DST_pts']['Fum'] = 2
    cfg['DST_pts']['DefTD'] = 6
    cfg['DST_pts']['Safts'] = 2
    
    # Individual Defensive Player scoring
    cfg['IDP_pts'] = {}
    cfg['IDP_pts']['Tack'] = 1.0
    cfg['IDP_pts']['Asst'] = 0.5
    cfg['IDP_pts']['Scks'] = 2.0
    cfg['IDP_pts']['PassDef'] = 1.0
    cfg['IDP_pts']['Int'] = 2.0
    cfg['IDP_pts']['FumFrc'] = 2.0
    cfg['IDP_pts']['Fum'] = 2.0
    cfg['IDP_pts']['DefTD'] = 6.0
        
    # Number of rounds to establish baseline depth
    cfg['baseline_depth'] = []
    cfg['baseline_depth'].append(8) # 1
    cfg['baseline_depth'].append(7) # 2
    cfg['baseline_depth'].append(6) # 3
    cfg['baseline_depth'].append(6) # 4
    cfg['baseline_depth'].append(6) # 5
    cfg['baseline_depth'].append(6) # 6
    cfg['baseline_depth'].append(6) # 7
    cfg['baseline_depth'].append(6) # 8
    cfg['baseline_depth'].append(6) # 9
    cfg['baseline_depth'].append(6) # 10
    cfg['baseline_depth'].append(6) # 11
    cfg['baseline_depth'].append(5) # 12
    cfg['baseline_depth'].append(4) # 13
    cfg['baseline_depth'].append(3) # 14
    cfg['baseline_depth'].append(2) # 15
    cfg['baseline_depth'].append(1) # 16

    # Positions allowed to draft in each round
    cfg['draftable'] = []
    cfg['draftable'].append(('QB','RB','WR','TE')) # 1
    cfg['draftable'].append(('QB','RB','WR','TE')) # 2
    cfg['draftable'].append(('QB','RB','WR','TE')) # 3
    cfg['draftable'].append(('QB','RB','WR','TE')) # 4
    cfg['draftable'].append(('QB','RB','WR','TE')) # 5
    cfg['draftable'].append(('QB','RB','WR','TE')) # 6
    cfg['draftable'].append(('QB','RB','WR','TE')) # 7
    cfg['draftable'].append(('QB','RB','WR','TE')) # 8
    cfg['draftable'].append(('QB','RB','WR','TE')) # 9
    cfg['draftable'].append(('QB','RB','WR','TE')) # 10
    cfg['draftable'].append(('QB','RB','WR','TE')) # 11
    cfg['draftable'].append(('QB','RB','WR','TE')) # 12
    cfg['draftable'].append(('QB','RB','WR','TE')) # 13
    cfg['draftable'].append(('DST','K')) # 14
    cfg['draftable'].append(('DST','K')) # 15
    cfg['draftable'].append(('DST','K')) # 16

    # Max number of players to draft at each position
    cfg['draft_max'] = {}
    cfg['draft_max']['QB'] = 2
    cfg['draft_max']['RB'] = 5
    cfg['draft_max']['WR'] = 6
    cfg['draft_max']['TE'] = 2
    cfg['draft_max']['K'] = 1
    cfg['draft_max']['IDP'] = 2
    cfg['draft_max']['DST'] = 2

    # Weight deduction per excess player
    cfg['weight_decrement'] = 0.2

    # Distribution weights
    # A, low, high
    cfg['distribution_weight'] = [1.0, 0.0, 0.0]

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
        
    #yhandler = YHandler('auth.csv')
    #yhandler.reg_user()
    
    # Startup console
    print
    print '*'*50
    print 'DraftMatic!!!'
    print '*'*50
    print ''
    
    # Main Loop
    while True:
        
        # Read in draft state
        draftteams.load_state()
        
        # Get round number
        n_round = draftteams.round()
        
        # Get pick number
        n_pick = draftteams.get_pick_num()
        n_overall_pick = draftteams.get_overall_pick_num()

        # Get drafter
        drafter = draftteams.get_drafter()

        # Get player counts
        pos_counts = draftteams.teams[drafter].get_pos_counts();
        pos_count_string = ''
        for pos in cfg['starters']:
            pos_count_string = pos_count_string+pos+':{}'.format(pos_counts[pos])+' '

        # Print round number
        print '-'*50
        print 'Round {}-{} ({})'.format(n_round+1,n_pick+1,n_overall_pick+1)
        print '{} is next to draft'.format(drafter)
        print pos_count_string
        print '-'*50
        print ''

        # Get list of drafted players
        drafted_players = draftteams.drafted_players()

        # Get position weights for the next drafter
        pos_weights = draftteams.teams[drafter].get_pos_weights(n_round)

        # Rank players
        player_db.rank_players(drafted_players, n_round, pos_weights)
	
        # Only print 1 ranking by default
        n_print_players = 1

        # Console loop until valid draft command is received
        while True:
        
            # Print out rankings short list
            for i in range(0, n_print_players):
                print_str = '{}:'.format(n_overall_pick+i+1)
                print_str = print_str + ' {}'.format(player_db.rank[i])
                print_str = print_str + ' at {}'.format(player_db.position[player_db.rank[i]])
                print_str = print_str + ' from {}'.format(player_db.team[player_db.rank[i]])
                print_str = print_str + ' ('
                if player_db.rank[i] in player_db.adp:
                    print_str = print_str + 'ADP{}'.format(player_db.adp[player_db.rank[i]])
                print_str = print_str + ')'
                print print_str
        
            
            # Prompt user for pick
            print ''
            console_inp = raw_input('Enter Pick (''h'' for help): ')
		
            # Process command
            if console_inp == 'h':
            
                print ''
                print 'Type desired player to draft or one of the following commands'
                print 'exit    - exit program'
                print 'reset   - restart draft'
                print '#       - desired number of players to see'
                print ''
            
            elif console_inp == 'exit':
                
                # Exit on command
                sys.exit()
                
            elif console_inp == 'reset':
            
                # Reset draft 
                draftteams.reset()
                
                break
                
            elif console_inp.isdigit():
                
                # Set number of rankings list to print
                n_print_players = int(console_inp)
                
                # Saturate at max ranking
                n_print_players = min(n_print_players, len(player_db.rank))
                
                print ''
                
            elif console_inp in player_db.adp:
            
                # Draft player and break loop
                draftteams.teams[drafter].draft_player(n_round,
                                                       console_inp,
                                                       player_db.position[console_inp])
                
                break
                
            else:
                
                # Don't reprint list
                n_print_players = 0
                
                # Print error message
                print ''
                print console_inp+' not recognized'
                                               
        # Write out draft state
        draftteams.write_state()

if __name__ == '__main__':
  main()

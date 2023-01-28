import psycopg2
from openpyxl import load_workbook
from insertTeams import get_team_player1_and_player_2
from insertTeams import get_team_id


# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="babyfoot3",
    user="postgres",
    password="519173"
)


# Create a cursor
cur = conn.cursor()

def calculate_elo(old_rating, opponent_rating, outcome):
    K = 32  # The constant that determines the impact of the match on the rating
    expected_outcome = 1 / (1 + 10 ** ((opponent_rating - old_rating) / 400))
    return old_rating + K * (outcome - expected_outcome)



# Load the workbook
wb = load_workbook('data.xlsx')

# Select the active sheet
ws = wb.active

# Iterate through the rows of the sheet

for row in ws.rows:

    # checking if the rows are not null
    if all(cell.value == None for cell in row):
        break
    date = row[0].value
    player1_name = row[1].value
    player2_name = row[2].value
    team1_score = row[3].value
    player3_name = row[4].value
    player4_name = row[5].value
    team2_score = row[6].value

    # Calculate the Elo ratings for the individual players
    player1_outcome = 0
    player2_outcome = 0
    player3_outcome = 0
    player4_outcome = 0
    if team1_score > team2_score:
        # Team 1 won, so players 1 and 2 get a win
        player1_outcome = 1
        player2_outcome = 1
    else:
        # Team 1 lost, so players 1 and 2 get a loss
        player1_outcome = 0
        player2_outcome = 0

    if team2_score > team1_score:
        # Team 2 won, so players 3 and 4 get a win
        player3_outcome = 1
        player4_outcome = 1
    else:
        # Team 2 lost, so players 3 and 4 get a loss
        player3_outcome = 0
        player4_outcome = 0

    # Get the current IDs of the players
    cur.execute("SELECT id FROM players WHERE name=%s", (player1_name,))
    player1_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM players WHERE name=%s", (player2_name,))
    player2_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM players WHERE name=%s", (player3_name,))
    player3_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM players WHERE name=%s", (player4_name,))
    player4_id = cur.fetchone()[0]
    
    # Get the current ratings of the players
    cur.execute("SELECT rating FROM eloratings WHERE playerid=%s", (player1_id,))
    result = cur.fetchone()
    if result is not None:
        player1_rating = result[0]
    else:
        # handle the case where the query did not return any rows
        player1_rating = 1200


    cur.execute("SELECT rating FROM eloratings WHERE playerid=%s", (player2_id,))
    result = cur.fetchone()
    if result is not None:
        player2_rating = result[0]
    else:
        # handle the case where the query did not return any rows
        player2_rating = 1200
    
    # print the value for testing
    print(f'Processing player2 {player2_name} with elo = {player2_rating}')
 
    cur.execute("SELECT rating FROM eloratings WHERE playerid=%s", (player3_id,))
    result = cur.fetchone()
    if result is not None:
        player3_rating = result[0]
    else:
        # handle the case where the query did not return any rows
        player3_rating = 1200

    cur.execute("SELECT rating FROM eloratings WHERE playerid=%s", (player4_id,))
    result = cur.fetchone()
    if result is not None:
        player4_rating = result[0]
    else:
        # handle the case where the query did not return any rows
        player4_rating = 1200                                                                                        

    conn.commit()
    # Calculate the new ratings for the players
    player1_new_rating = calculate_elo(player1_rating, player3_rating, player1_outcome) + calculate_elo(player1_rating, player4_rating, player1_outcome)
    player2_new_rating = calculate_elo(player2_rating, player3_rating, player2_outcome) + calculate_elo(player2_rating, player4_rating, player2_outcome)
    player3_new_rating = calculate_elo(player3_rating, player1_rating, player3_outcome) + calculate_elo(player3_rating, player2_rating, player3_outcome)
    player4_new_rating = calculate_elo(player4_rating, player1_rating, player4_outcome) + calculate_elo(player4_rating, player2_rating, player4_outcome)

    # Update the player ratings in the database
    cur.execute("UPDATE eloratings SET rating=%s WHERE playerid=%s", (player1_new_rating, player1_id))
    cur.execute("UPDATE eloratings SET rating=%s WHERE playerid=%s", (player2_new_rating, player2_id))
    cur.execute("UPDATE eloratings SET rating=%s WHERE playerid=%s", (player3_new_rating, player3_id))
    cur.execute("UPDATE eloratings SET rating=%s WHERE playerid=%s", (player4_new_rating, player4_id))

    conn.commit()

    # Calculate the Elo ratings for the teams
    team1_rating = (player1_new_rating + player2_new_rating) / 2
    team2_rating = (player3_new_rating + player4_new_rating) / 2

    #Call the function get_team_ids from the players ID
    team1_id = get_team_id(player1_id, player2_id,cur)
    team2_id = get_team_id(player3_id, player4_id,cur)


  

   # Update the team ratings in the elorating_teams table
    cur.execute("UPDATE eloratings_teams SET rating = %s WHERE teamid = %s", (team1_rating, team1_id))
    cur.execute("UPDATE eloratings_teams SET rating = %s WHERE teamid = %s", (team2_rating, team2_id))



    # Commit the changes to the database
    conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
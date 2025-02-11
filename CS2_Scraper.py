import subprocess
import json
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

def fetch_matches():
    """Runs the Node.js script to fetch matches."""
    try:
        result = subprocess.run(["node", "fetchMatches.js"], capture_output=True, text=True, check=True)
        matches = json.loads(result.stdout)
        return matches
    except subprocess.CalledProcessError as e:
        print("Error running Node.js script:", e)
        return []
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return []

def filter_matches(matches):
    """Filters matches for CS2 (or specific teams if needed)."""
    return [match for match in matches if match.get('team1', {}).get('name') and match.get('team2', {}).get('name')]

def convert_timestamp_to_readable(timestamp):
    """Converts Unix timestamp to a human-readable format."""
    if isinstance(timestamp, int):
        return datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S UTC')
    return 'Invalid timestamp'

def process_matches():
    """Fetches and processes CS2 matches."""
    with ProcessPoolExecutor() as executor:
        future = executor.submit(fetch_matches)
        matches = future.result()
        return filter_matches(matches)

def get_team_link(team_id, team_name):
    """Generates the link to the team's page on HLTV based on team id and name."""
    formatted_name = team_name.lower().replace(" ", "-")
    return f"https://www.hltv.org/team/{team_id}/{formatted_name}"

def get_event_link(event_id, event_name):
    """Generates the link to the event page on HLTV based on event id and name."""
    formatted_name = event_name.lower().replace(" ", "-")
    return f"https://www.hltv.org/events/{event_id}/{formatted_name}"

def get_cs2_matches():
    """Main entry point to fetch CS2 matches."""
    matches = process_matches()
    formatted_matches = []
    
    for match in matches:
        date = match.get('date', 'Unknown')
        readable_date = convert_timestamp_to_readable(date)
        tournament_name = match.get('event', {}).get('name', 'Unknown')
        tournament_id = match.get('event', {}).get('id', '')
        
        # Get the team links
        team1 = match.get('team1', {})
        team2 = match.get('team2', {})
        
        team1_link = get_team_link(team1.get('id'), team1.get('name')) if team1 else '#'
        team2_link = get_team_link(team2.get('id'), team2.get('name')) if team2 else '#'
        
        # Extract roster and coach data directly from match data
        team1_starters = team1.get('starters', [])
        team1_coach = team1.get('coach', [])
        
        team2_starters = team2.get('starters', [])
        team2_coach = team2.get('coach', [])
        
        # Get the event link
        event_link = get_event_link(tournament_id, tournament_name) if tournament_id and tournament_name else '#'
        
        formatted_matches.append({
            'match_date': readable_date,
            'team1': team1.get('name', 'Unknown'),
            'team1_link': team1_link,
            'team1_starters': team1_starters,
            'team1_coach': team1_coach,
            'team2': team2.get('name', 'Unknown'),
            'team2_link': team2_link,
            'team2_starters': team2_starters,
            'team2_coach': team2_coach,
            'tournament': tournament_name,
            'match_url': event_link,
            'stream_link': match.get('stream', '#')
        })
    
    return formatted_matches

if __name__ == "__main__":
    print("Fetching CS2 matches...")
    cs2_matches = get_cs2_matches()
    
    if cs2_matches:
        print("\nCS2 Matches Found:")
        for match in cs2_matches:
            print(f"{match['match_date']} - {match['team1']} vs {match['team2']} - {match['tournament']} ({match['match_url']})")
            print(f"  Team 1: {', '.join(match['team1_starters'])} (Coach: {', '.join(match['team1_coach'])})")
            print(f"  Team 2: {', '.join(match['team2_starters'])} (Coach: {', '.join(match['team2_coach'])})")
    else:
        print("No upcoming CS2 matches.")

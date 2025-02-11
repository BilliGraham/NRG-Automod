import praw
from datetime import datetime

# Import your custom scraper classes or functions
from RL_Scraper import LiquipediaScraper
from CS2_Scraper import get_cs2_matches  # Importing the function to get CS2 matches

# Reddit API credentials
reddit = praw.Reddit(
    client_id='v9HobV3f-rXD6onIpSzFCA',
    client_secret='60-XUf9xm4j6_u74p4dK12wuTrsFgw',
    username='Slender_Slayer96',
    password='Dyr301ec!',
    user_agent='NRG_Automod_Bot/0.1 by u/Slender_Slayer96'
)

# Format match data into a Reddit-friendly post
def format_reddit_post(matches):
    post_title = "Upcoming NRG & CS2 Matches"
    post_body = "Here are the upcoming NRG and CS2 matches:\n\n"
    
    for match in matches:
        match_date_str = match['match_date'].replace("UTC", "").strip()  # Remove "UTC" and extra spaces
        match_datetime = datetime.strptime(match_date_str, '%Y-%m-%d %H:%M:%S')
        
        # Start building the table
        post_body += f"**[{match['team1']}]({match['team1_link']}) vs [{match['team2']}]({match['team2_link']})**\n"
        post_body += f"- **Date/Time (UTC):** {match_datetime.strftime('%Y-%m-%d %I:%M %p')}\n"
        post_body += f"- **Tournament:** [{match['tournament']}]({match['match_url']})\n"
        post_body += f"- **Watch it live:** [Stream Link]({match['stream_link']})\n\n"
        
        # Create table for teams and rosters
        post_body += "| Team | Players | Coach |\n"
        post_body += "|------|---------|-------|\n"
        
        post_body += f"| [{match['team1']}]({match['team1_link']}) | {', '.join(match['team1_starters'])} | {', '.join(match['team1_coach'])} |\n"
        post_body += f"| [{match['team2']}]({match['team2_link']}) | {', '.join(match['team2_starters'])} | {', '.join(match['team2_coach'])} |\n"
        
        post_body += "\n---\n"

    return post_title, post_body


# Post the data to Reddit
def post_to_reddit(subreddit_name, post_title, post_body):
    subreddit = reddit.subreddit(subreddit_name)
    subreddit.submit(title=post_title, selftext=post_body)
    print(f"Posted to r/{subreddit_name}")

# Main function
def main():
    # Scrape the data using both LiquipediaScraper and CS2Scraper
    scraper = LiquipediaScraper()
    nrg_matches = scraper.get_nrg_matches()  # Fetch NRG-specific matches
    
    cs2_matches = get_cs2_matches()  # Fetch CS2-specific matches
    
    # Combine NRG and CS2 matches
    all_matches = nrg_matches + cs2_matches
    
    if all_matches:
        post_title, post_body = format_reddit_post(all_matches)
        post_to_reddit('TestNRGScript', post_title, post_body)  # Replace with actual subreddit name
    else:
        print("No NRG or CS2 matches to post.")

if __name__ == "__main__":
    main()

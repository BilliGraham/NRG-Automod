import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

class LiquipediaScraper:
    BASE_URL = "https://liquipedia.net/rocketleague/Liquipedia:Matches"
    HEADERS = {
        'User-Agent': 'NRG_Automod_Bot/1.0 (https://example.com; billicgraham1@gmail.com)',
        'Accept-Encoding': 'gzip'
    }   

    def __init__(self, rate_limit_interval=2):
        self.rate_limit_interval = rate_limit_interval
        self.last_request_time = 0

    def rate_limited_request(self, url):
        """Handles rate-limiting between requests."""
        elapsed_time = time.time() - self.last_request_time
        if elapsed_time < self.rate_limit_interval:
            time.sleep(self.rate_limit_interval - elapsed_time)

        response = requests.get(self.BASE_URL, headers=self.HEADERS)
        self.last_request_time = time.time()

        response.raise_for_status()  # Raise an error for failed requests
        return response.text

    def fetch_matches(self):
        """Fetch and parse upcoming matches from the Liquipedia matches page."""
        html_content = self.rate_limited_request(self.BASE_URL)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Locate the matches table
        match_tables = soup.find_all('table', class_='wikitable wikitable-striped infobox_matches_content')
        if not match_tables:
            print("No match tables found!")
            return []

        matches = []

        for table in match_tables:
            rows = table.find_all('tr')

            for row in rows:
                columns = row.find_all('td')
                if len(columns) < 3:
                    continue  # Skip invalid rows

                # Extract Team Names and URLs using the 'title' attribute
                team1_tag = columns[0].find('span', class_='team-template-team2-short')
                team2_tag = columns[2].find('span', class_='team-template-team-short')

                # Extract team 1 information
                if team1_tag:
                    team1_link = team1_tag.find('a')
                    team1 = team1_link['title'] if team1_link else "Unknown"  # Get the team name from the 'title' attribute
                    team1_url = f"https://liquipedia.net{team1_link['href']}" if team1_link else "Unknown"  # Get the URL (href attribute)
                else:
                    team1, team1_url = "Unknown", "Unknown"

                # Extract team 2 information
                if team2_tag:
                    team2_link = team2_tag.find('a')
                    team2 = team2_link['title'] if team2_link else "Unknown"  # Get the team name from the 'title' attribute
                    team2_url = f"https://liquipedia.net{team2_link['href']}" if team2_link else "Unknown"  # Get the URL (href attribute)
                else:
                    team2, team2_url = "Unknown", "Unknown"

                # Extract Match Date
                date_tag = row.find('span', class_='timer-object timer-object-countdown-only')
                if date_tag:
                    match_date = date_tag.get_text(strip=True)
                else:
                    date_tag = soup.find('span', class_='timer-object timer-object-countdown-only')
                    match_date = date_tag.get_text(strip=True)

                # Extract Tournament Name (From 'a' tag in the second 'td' element)
                tournament_tag = soup.find('td', style="text-align:right;font-size:11px;line-height:12px;padding-right:4px").find('a')
                tournament = tournament_tag.get_text(strip=True) if tournament_tag else "Unknown"
                

                # Extract Match URL
                match_url = f"https://liquipedia.net{tournament_tag['href']}" if tournament_tag else None

                stream_links = soup.find_all('a', href=True)

                stream_link = "Unknown"

                # Extract the relevant stream links
                if team1 == "NRG" or team2 == "NRG":
                    for link in stream_links:
                        if 'Special:Stream/twitch' in link['href']:
                            twitch_link = link['href']
                            full_url = "https://liquipedia.net" + twitch_link  # Ensure the URL is complete
                            response = requests.get(full_url)
                        
                    if response.status_code == 200:
                        # Parse the page
                        soup2 = BeautifulSoup(response.text, 'html.parser')

                        # Find the iframe tag and extract the src attribute
                        iframe = soup2.find('iframe', src=True)
                        
                        if iframe:
                            stream_link = iframe['src']
                        else:
                            stream_link = "Unknown"
                
                # Append the match information to the list
                matches.append({
                    'match_date': match_date,
                    'team1': team1,
                    'team1_link': team1_url,
                    'team2': team2,
                    'team2_link': team2_url,
                    'tournament': tournament,
                    'match_url': match_url,
                    'stream_link': stream_link,
                    'game': 'Rocket League'
                })

                if len(matches) >= 40: 
                    break

            if len(matches) >= 40:
                break

        return matches


    def get_nrg_matches(self):
        """Check first few matches and return ones involving NRG."""
        matches = self.fetch_matches()
        nrg_matches = [match for match in matches if "NRG" in (match['team1'], match['team2'])]

        return nrg_matches

# Run the script
if __name__ == "__main__":
    scraper = LiquipediaScraper()
    print("Fetching upcoming matches...")

    nrg_matches = scraper.get_nrg_matches()

    if nrg_matches:
        print("\nNRG Matches Found:")
        for match in nrg_matches:
            print(f"{match['match_date']} - {match['team1']} [{match['team1_link']}] vs {match['team2']} [{match['team2_link']}] ({match['tournament']}) [{match['match_url']}] - Stream: {match['stream_link']}")
    else:
        print("NRG is not playing soon.")

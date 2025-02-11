const HLTV = require('hltv');

const NRG_TEAM_ID = 6673;

async function fetchTeamRoster(teamId) {
    try {
        const team = await HLTV.default.getTeam({ id: teamId });

        // Separate the starters and coach from the rest
        const starters = team.players.filter(player => player.type === 'Starter').map(player => player.name);
        const coach = team.players.filter(player => player.type === 'Coach').map(player => player.name);
        
        return { starters, coach };
    } catch (error) {
        console.error(`Error fetching roster for team ${teamId}:`, error);
        return { starters: [], coach: [] }; // Return empty arrays if fetching fails
    }
}

async function fetchMatches() {
    try {
        const matches = await HLTV.default.getMatches();

        const nrgMatches = matches.filter(match => 
            match.team1?.id === NRG_TEAM_ID || match.team2?.id === NRG_TEAM_ID
        );

        for (let match of nrgMatches) {
            // Fetch and separate the roster info for both teams
            const team1Roster = await fetchTeamRoster(match.team1.id);
            const team2Roster = await fetchTeamRoster(match.team2.id);

            // Attach rosters to the match data
            match.team1.starters = team1Roster.starters;
            match.team1.coach = team1Roster.coach;
            match.team2.starters = team2Roster.starters;
            match.team2.coach = team2Roster.coach;
        }

        // Log the matches with the updated roster data
        console.log(JSON.stringify(nrgMatches, null, 2));
    } catch (error) {
        console.error('Error fetching matches:', error);
        process.exit(1);
    }
}

fetchMatches();

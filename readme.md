# CarromBot

### A Telegram bot to keep track of Carrom tournament points

Carrom is an incredible game that shares some mechanics with pool. My roommates and I spent a couple of months playing it day and night, recording every match on a large
sheet of paper to determine the winner of the month. But at the end of the month, nobody wanted to calculate all the stats by hand. So, eight months after we stopped
playing, I developed a bot that you can use to record your matches and get stats for every player.

#### How to use:
- Make yourself a telegram bot using the Botfather, get your API KEY.
- Install Docker on your machine
- Clone this repo. Move into the repo directory. 
- Replace your API KEY in `db_init.py`
- Run: `docker compose up`
- The bot should be running

##### Future updates

Add more stats (like our made-up  "grado smerdatico medio"), optimize navigation, and create a simple deployment process for everyone.

#### What am i doing?

*25/07/2025* : Deployment done(?)

*25/07/2025* : The bot is done. Did "go back" work. Graphical will be added in next times.

*22/07/2025*: The bot works. I need to add the "go back" button and make it work, add some stats, make it output graphical stats, but the bare structure is done.

*21/07/2025*: I should have done the structure of the _match registration_. Now I have to put up some MySQL database to handle everything.
Update: made work the db: now it saves players and matches. Next thing to do is to show stats.


*20/07/2025*: I decided to change strategy with respect to first iteration of this bot. No more commands just buttons to press.

*16/07/25* : Started working again on this. Did a dockerfile but i think it is a thing that is to be done after the bot code has been written.

 

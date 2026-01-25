import discord
from discord.ext import tasks, commands
import datetime
from zoneinfo import ZoneInfo

# custom files
import weather_predictor

# class that configures the Discord bot
class weather_predicting_bot(commands.Bot):
    def __init__(self,  DISCORD_TOKEN, DISCORD_CHANNELS, LOCATIONS):
        self.last_sent_date = None
        self.latest_observed_messages = None
        self.DISCORD_TOKEN = DISCORD_TOKEN
        self.DISCORD_CHANNELS = DISCORD_CHANNELS
        self.LOCATIONS = LOCATIONS
        
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    # start the Discord bot
    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        
        # start the weather data storage task
        if (not self.hourly_weather_collection.is_running()):
            self.hourly_weather_collection.start()

        # start the daily Discord update task
        if (not self.daily_discord_update.is_running()):
            self.daily_discord_update.start()

    # collect weather data every hour
    @tasks.loop(hours=1)
    async def hourly_weather_collection(self):
        print(f"Running hourly weather data collection...\n")

        # collect latest weather data
        self.latest_observed_messages = weather_predictor.weather_data_storage()
        pass

    # print weather data to Discord at 12:00 PM every day
    #@tasks.loop(minutes=10)
    @tasks.loop(time=datetime.time(hour=12, minute=0, second=0, tzinfo=ZoneInfo("America/Phoenix")))
    async def daily_discord_update(self):
        # check if the Discord message was already sent today
        today = datetime.date.today()
        if (self.last_sent_date == today):
            print(f"Discord daily update already sent today ({today}). Skipping...\n")
            return
        else:
            self.last_sent_date = today

        # prepare Discord message
        print(f"Preparing to send Discord daily update for {today}...\n")
        discord_message = (
            f"```\n"
            f"Daily Weather Update at 12:00:00 hours:\n"
            f"```\n"
        )

        # send Discord message to each channel
        for discord_channel_id in self.DISCORD_CHANNELS:
            discord_channel = self.get_channel(int(discord_channel_id)) or await self.fetch_channel(int(discord_channel_id))
            await discord_channel.send(discord_message)
        
        # prepare weather data for each city
        for message in self.latest_observed_messages:
            discord_message = (
                f"```\n"
                f"{message}\n"
                f"```"
            )

            # send Discord message to each channel
            for discord_channel_id in self.DISCORD_CHANNELS:
                discord_channel = self.get_channel(int(discord_channel_id)) or await self.fetch_channel(int(discord_channel_id))
                await discord_channel.send(discord_message)
        pass

    pass
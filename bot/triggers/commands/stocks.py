from . import Command
from .. import utils

import discord
import io
import json


class Stocks(Command):
    names = ["stock", "stocks", "stonk", "stonks"]
    description = "Retrieves stock price information using Yahoo! Finance"
    usage = "!stock <stock 1> <stock 2> .... <stock N>"
    examples = f"!stock GME BB"

    async def execute_command(self, client, msg, content, **kwargs):
        # At the moment, Yahoo! Finance has no way to get a random stock easily.
        # So not having a ticker passed in means we just fail out
        if len(content) == 0:
            return await utils.delay_send(
                msg.channel, "Error: Must have at least one stock to query!"
            )

        # prepare query str
        query = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={','.join(content.split(' '))}"

        async with utils.get_aiohttp().get(query) as stock_request:
            # Ensure HTTP request succeeded
            if stock_request.status != 200:
                stock_request_text = await stock_request.text()
                return await utils.delay_send(
                    msg.channel,
                    f"Failed to retrieve stock information :-(. HTTP {stock_request.status}: ```{stock_request_text}```",
                )
            forecast = json.loads(await stock_request.read())["quoteResponse"]["result"]

            if len(forecast) == 0:
                return await utils.delay_send(
                    msg.channel, "No stock information found (are those valid stocks?)."
                )
            else:
                # Iterate through each stock
                for data in forecast:
                    historic = False

                    # The get_info function is an easy way of ensuring all needed data is available
                    # in the event a field doesn't exist, we assume the stock is 'historic' and therefore no useful information
                    # can be found.
                    def get_info(id):
                        nonlocal historic
                        if id in data:
                            return data[id]
                        historic = True
                        return None

                    name = get_info("shortName")
                    percent_change = get_info("regularMarketChangePercent")
                    change = get_info("regularMarketChange")
                    curr_price = get_info("regularMarketPrice")
                    symbol = get_info("symbol")
                    currency = get_info("currency")
                    yearRange = get_info("fiftyTwoWeekRange")

                    if historic:
                        await utils.delay_send(
                            msg.channel, f"Error: {symbol} is a historic stock symbol."
                        )
                        continue

                    after_hours = False
                    after_hours_price = None
                    after_hours_pc = None
                    after_hours_change = None
                    # Try to see if we can or should acquire after hours trading information
                    try:
                        post_market_time = get_info("postMarketTime")
                        regular_market_time = get_info("regularMarketTime")
                        after_hours = post_market_time > regular_market_time

                        if after_hours:
                            after_hours_price = get_info("postMarketPrice")
                            after_hours_pc = get_info("postMarketChangePercent")
                            after_hours_change = get_info("postMarketChange")
                    except:
                        pass

                    color = 15158332 if percent_change < 0 else 3066993

                    regular_info = f"{curr_price:.2f} {currency} -> ({change:+,.2f} / {percent_change:+,.2f}%)"
                    embed = discord.Embed(
                        title=f"{name} - ${symbol}",
                        color=color,
                    )
                    if after_hours:
                        embed.description = f"After Hours: {after_hours_price:.2f} {currency} -> ({after_hours_change:+,.2f} / {after_hours_pc:+,.2f}%)"
                        embed.add_field(
                            name="Regular: ", value=regular_info, inline=False
                        )
                    else:
                        embed.description = regular_info

                    embed.add_field(
                        name="Fifty Two Week Range", value=yearRange, inline=False
                    )

                    try:
                        await utils.delay_send(msg.channel, embed=embed)
                    except:
                        await utils.delay_send(
                            msg.channel, f"Error: Failed to send information for {name}"
                        )

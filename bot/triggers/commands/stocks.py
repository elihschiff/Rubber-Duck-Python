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
        if len(content) == 0:
            return await utils.delay_send(
                msg.channel, "Error: Must have at least one stock to query!"
            )

        # prepare query str
        query = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={','.join(content.split(' '))}"

        async with utils.get_aiohttp().get(query) as stock_request:
            if stock_request.status != 200:
                return await utils.delay_send(
                    msg.channel,
                    f"Failed to retrieve stock information :-(. HTTP {stock_request.status}: ```{await stock_request.text()}```",
                )
            forecast = json.loads(await stock_request.read())["quoteResponse"]["result"]

            if len(forecast) == 0:
                return await utils.delay_send(
                    msg.channel, "No stock information found (are those valid stocks?)."
                )
            else:
                for data in forecast:

                    name = data["shortName"]
                    percent_change = data["regularMarketChangePercent"]
                    change = data["regularMarketChange"]
                    curr_price = data["regularMarketPrice"]
                    symbol = data["symbol"]
                    currency = data["currency"]

                    color = 15158332 if percent_change < 0 else 3066993

                    embed = discord.Embed(
                        title=f"{name} - ${symbol}",
                        description=f"{curr_price:.2f} {currency} -> ({change:+,.2f} / {percent_change:+,.2f}%)",
                        color=color,
                    )

                    try:
                        await utils.delay_send(msg.channel, embed=embed)
                    except:
                        await utils.delay_send(
                            msg.channel, f"Error: Failed to send information for {name}"
                        )

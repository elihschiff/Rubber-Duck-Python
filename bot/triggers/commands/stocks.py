from . import Command
from .. import utils

import datetime
import discord
import io
import json
import random

from enum import Enum


class MarketState(Enum):
    PRE = (1, "Premarket")
    REGULAR = (2, "Regular")
    POST = (3, "Postmarket")


# Rounds the value to 2 decimal places if price >= $1 and 6 if < $1
# also has an option to show the sign (+/-) before the number
def round_price(value, price, show_sign=False):
    if show_sign:
        return f"{value:+.2f}" if abs(price) >= 1 else f"{value:+.6f}"
    return f"{value:.2f}" if abs(price) >= 1 else f"{value:.6f}"


async def get_json(query):
    async with utils.get_aiohttp().get(query) as stock_request:
        # Ensure HTTP request was successful
        stock_request_text = await stock_request.text()
        if stock_request.status != 200:
            return f"Failed to retrieve stock information :-(. HTTP {stock_request.status}: ```{stock_request_text}```"
        else:
            return json.loads(stock_request_text)


async def get_stock_data(content):
    # prepare query str -- we want to load balance between query1 and query2 to be good netizens
    stock_json = await get_json(
        f"https://query{random.choice((1,2))}.finance.yahoo.com/v7/finance/quote?symbols={content}"
    )

    # Propagate error messages up
    if isinstance(stock_json, str):
        return stock_json

    forecast = stock_json["quoteResponse"]["result"]
    if len(forecast) == 0:
        return None

    data = forecast[0]
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
        return None

    market_time = get_info("regularMarketTime")

    after_hours_price = None
    after_hours_pc = None
    after_hours_change = None
    # Try to see if we can or should acquire after hours trading information

    state = MarketState.REGULAR

    def try_state(new_state, header):
        nonlocal state
        nonlocal after_hours_price
        nonlocal after_hours_pc
        nonlocal after_hours_change
        nonlocal market_time
        try:
            time = get_info(f"{header}MarketTime")

            if time > market_time:
                after_hours_price = get_info(f"{header}MarketPrice")
                after_hours_pc = get_info(f"{header}MarketChangePercent")
                after_hours_change = get_info(f"{header}MarketChange")
                state = new_state
                market_time = time
        except:
            pass

    try_state(MarketState.PRE, "pre")
    try_state(MarketState.POST, "post")
    color = 15158332 if percent_change < 0 else 3066993

    regular_info = f"{round_price(curr_price, curr_price)} {currency} -> ({round_price(change, curr_price, True)} / {percent_change:+,.2f}%)"
    embed = discord.Embed(
        title=f"{name} - ${symbol}",
        color=color,
        timestamp=datetime.datetime.fromtimestamp(
            market_time, tz=datetime.timezone.utc
        ),
    )

    embed.set_author(
        name="Yahoo! Finance",
        url=f"https://finance.yahoo.com/quote/{symbol}",
    )

    if "coinImageUrl" in data:
        embed.set_thumbnail(url=data["coinImageUrl"])

    if state != MarketState.REGULAR:
        embed.add_field(
            name=state.value[1],
            value=f"{round_price(after_hours_price, after_hours_price)} {currency} -> ({round_price(after_hours_change, after_hours_price, True)} / {after_hours_pc:+,.2f}%)",
            inline=False,
        )
        embed.add_field(name="Regular: ", value=regular_info, inline=False)
    else:
        embed.description = regular_info

    if "regularMarketDayRange" in data:
        embed.add_field(
            name="Daily Range", value=data["regularMarketDayRange"], inline=False
        )
    embed.add_field(name="Fifty Two Week Range", value=yearRange, inline=False)

    return embed


class Stocks(Command):
    names = ["stock", "stocks", "stonk", "stonks"]
    description = "Retrieves stock price information using Yahoo! Finance"
    usage = "!stock <stock>"
    examples = "!stock GME"
    causes_spam = True

    async def execute_command(self, client, msg, content, **kwargs):
        # At the moment, Yahoo! Finance has no way to get a random stock easily.
        # So not having a ticker passed in means we just fail out
        if len(content) == 0:
            return await utils.delay_send(
                msg.channel,
                "Error: Must have at least one stock to query!",
                reply_to=msg,
            )

        # Try to send content as a ticker (if we have an exact match, we don't need to search)
        data = await get_stock_data(content)

        # Propagate error messages
        if isinstance(data, str):
            return await utils.delay_send(msg.channel, data, reply_to=msg)

        # Fuzzy search fallback for search by related tickers / company names / security names
        if data == None:
            search_json = await get_json(
                f"https://query{random.choice([1,2])}.finance.yahoo.com/v1/finance/search?q={content}&lang=en-US&region=US&quotesCount=6&newsCount=0&enableFuzzyQuery=true&quotesQueryId=tss_match_phrase_query&multiQuoteQueryId=multi_quote_single_token_query&enableEnhancedTrivialQuery=true"
            )
            # Propagate error messages
            if isinstance(search_json, str):
                return await utils.delay_send(msg.channel, data, reply_to=msg)
            quotes = search_json["quotes"]

            if len(quotes) > 0:
                data = await get_stock_data(quotes[0]["symbol"])

            # Propagate error messages
            if isinstance(data, str):
                return await utils.delay_send(msg.channel, data, reply_to=msg)

            # If we didn't find anything again, let the user know
            if data == None:
                return await utils.delay_send(
                    msg.channel,
                    f"Error: Could not find stock data for query ```{content}``` :-(",
                    reply_to=msg,
                )

        # Send embed back if we managed to find a match
        await utils.delay_send(msg.channel, embed=data, reply_to=msg)

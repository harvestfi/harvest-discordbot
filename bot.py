#!/usr/bin/env python

import requests
import datetime
import time
import random
import asyncio
import discord
import os
from discord.ext.commands import Bot
from discord.ext import commands, tasks
from web3 import Web3
from dotenv import load_dotenv

load_dotenv(override=True)

DISCORD_WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
NODE_URL = os.getenv("NODE_URL")
START_BLOCK = os.getenv("START_BLOCK")
UNIROUTER_ADDR = os.getenv("UNIROUTER_ADDR")
UNIROUTER_ABI = os.getenv("UNIROUTER_ABI")
UNIPOOL_ADDR= os.getenv("UNIPOOL_ADDR")
UNIPOOL_ABI = os.getenv("UNIPOOL_ABI")
VAULT_ABI = os.getenv("VAULT_ABI")
CURVEPOOL_ABI = os.getenv("CURVEPOOL_ABI")
PS_ABI = os.getenv("PS_ABI")
ONE_18DEC = 1000000000000000000
ZERO_ADDR = '0x0000000000000000000000000000000000000000'
FARM_ADDR = '0xa0246c9032bC3A600820415aE600c6388619A14D'


w3 = Web3(Web3.HTTPProvider(NODE_URL))
controller_contract = w3.eth.contract(address=UNIROUTER_ADDR, abi=UNIROUTER_ABI)
pool_contract = w3.eth.contract(address=UNIPOOL_ADDR, abi=UNIPOOL_ABI)

vaults = {
  '0x8e298734681adbfC41ee5d17FF8B0d6d803e7098': {'asset': 'fWETH', 'decimals': 18,},
  '0xe85C8581e60D7Cd32Bbfd86303d2A4FA6a951Dac': {'asset': 'fDAI', 'decimals': 18,},
  '0xc3F7ffb5d5869B3ade9448D094d81B0521e8326f': {'asset': 'fUSDC', 'decimals': 6,},
  '0xc7EE21406BB581e741FBb8B21f213188433D9f2F': {'asset': 'fUSDT', 'decimals': 6,},
  '0xF2B223Eb3d2B382Ead8D85f3c1b7eF87c1D35f3A': {'asset': 'FARM yDAI+yUSDC+yUSDT+yTUSD', 'decimals': 18,},
  '0xfBe122D0ba3c75e1F7C80bd27613c9f35B81FEeC': {'asset': 'fRenBTC', 'decimals': 8,},
  '0xc07EB91961662D275E2D285BdC21885A4Db136B0': {'asset': 'fWBTC', 'decimals': 8,},
  '0x192E9d29D43db385063799BC239E772c3b6888F3': {'asset': 'fCRVRenWBTC', 'decimals': 18,},
  '0xb1FeB6ab4EF7d0f41363Da33868e85EB0f3A57EE': {'asset': 'fUNI-ETH-WBTC', 'decimals': 18,},
  '0xB19EbFB37A936cCe783142955D39Ca70Aa29D43c': {'asset': 'fUNI-ETH-USDT', 'decimals': 18,},
  '0x63671425ef4D25Ec2b12C7d05DE855C143f16e3B': {'asset': 'fUNI-ETH-USDC', 'decimals': 18,},
  '0x1a9F22b4C385f78650E7874d64e442839Dc32327': {'asset': 'fUNI-ETH-DAI', 'decimals': 18,},
  '0x8f5adC58b32D4e5Ca02EAC0E293D35855999436C': {'asset': 'FARM', 'decimals': 18,},
  '0xef4Da1CE3f487DA2Ed0BE23173F76274E0D47579': {'asset': 'fCRV-USDN', 'decimals': 18,},
  '0x6D1b6Ea108AA03c6993d8010690264BA96D349A8': {'asset': 'fyCRV', 'decimals': 18,},
  '0x27F12d1a08454402175b9F0b53769783578Be7d9': {'asset': 'f3CRV', 'decimals': 18,},
  '0x017eC1772A45d2cf68c429A820eF374f0662C57c': {'asset': 'fCRV-TBTC', 'decimals': 18,},
  '0xC0f51a979e762202e9BeF0f62b07F600d0697DE1': {'asset': 'fCRV-COMPOUND', 'decimals': 18,},
  '0x093C2ae5E6F3D2A897459aa24551289D462449AD': {'asset': 'fCRV-BUSD', 'decimals': 18,},
  '0x9523FdC055F503F73FF40D7F66850F409D80EF34': {'asset': 'fSUSHI-WBTC-TBTC', 'decimals': 18,},
  '0x76Aef359a33C02338902aCA543f37de4b01BA1FA': {'asset': 'fSUSHI-ETH-DAI', 'decimals': 18,},
  '0x6B4e1E0656Dd38F36c318b077134487B9b0cf7a6': {'asset': 'fSUSHI-ETH-USDC', 'decimals': 18,},
  '0xA56522BCA0A09f57B85C52c0Cc8Ba1B5eDbc64ef': {'asset': 'fSUSHI-ETH-USDT', 'decimals': 18,},
  '0xE2D9FAe95f1e68afca7907dFb36143781f917194': {'asset': 'fSUSHI-ETH-WBTC', 'decimals': 18,},
}


vault_addr = {
    'fdai'        : {'addr': '0xab7FA2B2985BCcfC13c6D86b1D5A17486ab1e04C', 'decimals': 18},
    'fusdc'       : {'addr': '0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE', 'decimals': 6},
    'fusdt'       : {'addr': '0x053c80eA73Dc6941F518a68E2FC52Ac45BDE7c9C', 'decimals': 6},
    'fwbtc'       : {'addr': '0x5d9d25c7C457dD82fc8668FFC6B9746b674d4EcB', 'decimals': 8},
    'frenbtc'     : {'addr': '0xC391d1b08c1403313B0c28D47202DFDA015633C4', 'decimals': 8},
    'fcrvrenwbtc' : {'addr': '0x9aA8F427A17d6B0d91B6262989EdC7D45d6aEdf8', 'startblock': 10815917, 'decimals': 18},
    'fweth'       : {'addr': '0xFE09e53A81Fe2808bc493ea64319109B5bAa573e', 'decimals': 18},
    'fycrv'       : {'addr': '0x0FE4283e0216F94f5f9750a7a11AC54D3c9C38F3', 'decimals': 18},
    'f3crv'       : {'addr': '0x71B9eC42bB3CB40F017D8AD8011BE8e384a95fa5', 'decimals': 18},
    'fcrvtbtc'    : {'addr': '0x640704D106E79e105FDA424f05467F005418F1B5', 'decimals': 18},
    'ftusd'       : {'addr': '0x7674622c63Bee7F46E86a4A5A18976693D54441b', 'decimals': 18},
    'funi-eth-wbtc': {'addr': '0x01112a60f427205dcA6E229425306923c3Cc2073',},
    'funi-eth-usdt': {'addr': '0x7DDc3ffF0612E75Ea5ddC0d6Bd4e268f70362Cff',},
    'funi-eth-usdc': {'addr': '0xA79a083FDD87F73c2f983c5551EC974685D6bb36',},
    'funi-eth-dai':  {'addr': '0x307E2752e8b8a9C29005001Be66B1c012CA9CDB7',},
    'fsushi-wbtc-tbtc': {'addr': '0xF553E1f826f42716cDFe02bde5ee76b2a52fc7EB',},
    'fsushi-eth-usdc': {'addr': '0x01bd09A1124960d9bE04b638b142Df9DF942b04a', 'decimals': 18},
    'fsushi-eth-usdt': {'addr': '0x64035b583c8c694627A199243E863Bb33be60745', 'decimals': 18},
    'fsushi-eth-wbtc': {'addr': '0x5C0A3F55AAC52AA320Ff5F280E77517cbAF85524', 'decimals': 18},
    'fsushi-eth-dai': {'addr': '0x203E97aa6eB65A1A02d9E80083414058303f241E', 'decimals': 18},
    'profitshare': {'addr': '0x8f5adC58b32D4e5Ca02EAC0E293D35855999436C',},
    'fcrvbusd': {'addr': '0x4b1cBD6F6D8676AcE5E412C78B7a59b4A1bbb68a', 'decimals': 18},
    'fcrvusdn': {'addr': '0x683E683fBE6Cf9b635539712c999f3B3EdCB8664', 'decimals': 18},
    'fcrvcompound': {'addr': '0x998cEb152A42a3EaC1f555B1E911642BeBf00faD', 'decimals': 18}
}

tokens_price = {
    'uni-eth-dai': {'addr': '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11', 'decimals0': 18, 'decimals1': 18, 'decimalsTotal': 18 }, #0:DAI 1:WETH
    'uni-eth-wbtc': {'addr': '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940', 'decimals0': 8, 'decimals1': 18, 'decimalsTotal': 18 }, #0:WBTC 1:WETH
    'uni-eth-usdt': {'addr': '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852', 'decimals0': 18, 'decimals1': 6,'decimalsTotal': 18 }, #0:WETH 1:USDT
    'uni-eth-usdc': {'addr': '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc', 'decimals0': 6, 'decimals1': 18, 'decimalsTotal': 18}, #0:USDC 1:WETH
    'uni-eth-comp': {'addr': '0xCFfDdeD873554F362Ac02f8Fb1f02E5ada10516f', 'decimals0': 18, 'decimals1': 18, 'decimalsTotal': 18}, #0:COMP 1:WETH
    '3crv': {'addr': '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7', 'decimalsTotal': 18},
    'ycrv': {'addr': '0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51', 'decimalsTotal': 18},
    'crvtbtc': {'addr': '0xC25099792E9349C7DD09759744ea681C7de2cb66', 'decimalsTotal': 18},
    'crvcompound': {'addr': '0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56', 'decimalsTotal': 18},
    'crvbusd': {'addr': '0x79a8C46DeA5aDa233ABaFFD40F3A0A2B1e5A4F27', 'decimalsTotal': 18},
    'crvusdn': {'addr': '0x0f9cb53Ebe405d49A0bbdBD291A65Ff571bC83e1', 'decimalsTotal': 18},
    'crvrenwbtc': {'addr': '0x93054188d876f558f4a66B2EF1d97d16eDf0895B', 'decimalsTotal': 18},
    'sushi-wbtc-tbtc': {'addr': '0x2Dbc7dD86C6cd87b525BD54Ea73EBeeBbc307F68', 'decimals0': 8, 'decimals1': 18,'decimalsTotal': 18}, #0:WBTC 1:TBTC
    'sushi-eth-usdc': {'addr': '0x397FF1542f962076d0BFE58eA045FfA2d347ACa0', 'decimals0': 6, 'decimals1': 18,'decimalsTotal': 18}, #0:USDC 1:WETH
    'sushi-eth-usdt': {'addr': '0x06da0fd433C1A5d7a4faa01111c044910A184553', 'decimals0': 18, 'decimals1': 6,'decimalsTotal': 18}, #0:WETH 1:USDT
    'sushi-eth-wbtc': {'addr': '0xCEfF51756c56CeFFCA006cD410B03FFC46dd3a58', 'decimals0': 8, 'decimals1': 18,'decimalsTotal': 18}, #0:WBTC 1:WETH
    'sushi-eth-dai': {'addr': '0xC3D03e4F041Fd4cD388c549Ee2A29a9E5075882f', 'decimals0': 18, 'decimals1': 18,'decimalsTotal': 18}, #0:DAI 1:WETH
        }
assets = ['weth', 'wbtc', '3crv', 'ycrv', 'crvtbtc', 'crvcompound', 'crvbusd', 'crvusdn', 'crvrenwbtc', 'renbtc', 'usdc', 'usdt', 'tusd', 'dai', 'lp', 'sushi-eth-wbtc', 'sushi-eth-dai', 'sushi-eth-usdc', 'sushi-eth-usdt', 'total', 'farm']
# global variables with locked value in USD and price of asset in each pool
locked, prices = {}, {}
for a in assets:
    locked[a] = 0
    prices[a] = 0

earlyemissions = [
    57569.10,
    51676.20,
    26400.00,
    24977.50
]

def emissions(weeknum):
    weeknum = int(weeknum)
    emitted_this_week = 0
    supply_this_week = 0
    EMISSIONS_WEEK5 = 23555.00
    EMISSIONS_WEEKLY_SCALE = 0.95554375
    if weeknum > 208:
        emitted_this_week = 0
        supply_this_week = 690420
    elif weeknum >= 5:
        emitted_this_week = EMISSIONS_WEEK5 * EMISSIONS_WEEKLY_SCALE ** (weeknum - 5)
        supply_this_week = sum(earlyemissions) + EMISSIONS_WEEK5 * (1 - EMISSIONS_WEEKLY_SCALE ** (weeknum - 4) ) / (1 - EMISSIONS_WEEKLY_SCALE)
    else:
        emitted_this_week = earlyemissions[weeknum-1]
        supply_this_week = sum(earlyemissions[:weeknum])
    return emitted_this_week, supply_this_week


client = discord.Client(command_prefix='!')
activity_start = discord.Streaming(
                name='the prices',
                url='https://uniswap.info/token/0xa0246c9032bc3a600820415ae600c6388619a14d'
)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=activity_start)
    update_price.start()
    update_tvl.start()

@tasks.loop(seconds=15)
async def update_price():
    print(f'fetching pool reserves...')
    poolvals = pool_contract.functions['getReserves']().call()
    print(f'calculating price...')
    price = controller_contract.functions['quote'](ONE_18DEC, poolvals[0], poolvals[1]).call()*10**-6

    print(f'updating the price...')
    msg = f'${price:0.2f} FARM'
    new_price = discord.Streaming(
        name=msg,
        url='https://uniswap.info/token/0xa0246c9032bc3a600820415ae600c6388619a14d'
    )
    print(msg)
    global prices
    prices['farm'] = price
    await client.change_presence(activity=new_price)

@client.event
async def on_message(msg):
    if client.user.id != msg.author.id:
        if '!foo' in msg.content:
            await msg.channel.send('bar')
        if '!bot' in msg.content:
            embed = discord.Embed(
                    title='Autonomous Agricultural Assistant, at your service :tractor:',
                    description=':bar_chart: `!trade`: FARM markets and trading\n'
                                ':thinking: `!payout`: information on farming rewards\n'
                                ':globe_with_meridians: `!contribute`: contribute to the community wiki\n'
                                ':bank: `!vault fdai/fwbtc/etc`: Harvest vault state\n'
                                ':chart_with_upwards_trend: improve me [on GitHub](https://github.com/brandoncurtis/harvest-discordbot)'
                    )
            await msg.channel.send(embed=embed)
        if '!payout' in msg.content:
            embed = discord.Embed(
                    title='When do I get the CRV/SWRV/UNI/&etc? :thinking:',
                    description='Farmed tokens are sold to grow the value of your deposit :seedling: '
                                '[read more about farming strategies](https://farm.chainwiki.dev/en/strategy)',
                    )
            await msg.channel.send(embed=embed)
        if '!contribute' in msg.content:
            embed = discord.Embed(
                    title='**:sparkles: Great Idea :sparkles:**',
                    description='please add that [to the wiki](https://farm.chainwiki.dev/en/contribute)!',
                    )
            await msg.channel.send(embed=embed)
        if '!ap' in msg.content:
            val = float(msg.content.split(' ')[-1])
            # APY = (1 + APR / n) ** n - 1
            APYfromAPR_daily = 100 * ((1 + val / (100 * 365)) ** 365 - 1)
            APYfromAPR_weekly = 100 * ((1 + val / (100 * 52)) ** 52 - 1)
            # APR = n * (1 + APY) ** (1 / n) -n
            APRfromAPY_daily = 100 * (365 * ((1 + val / 100) ** (1 / 365)) - 365)
            APRfromAPY_weekly = 100 * (52 * ((1 + val / 100) ** (1 / 52)) - 52)
            embed = discord.Embed(
                    title=':man_teacher: **Convert between APR and APY?**',
                    )
            embed.add_field(name = 'Compounded Daily', value = 'If you redeem and reinvest rewards daily...', inline=False)
            embed.add_field(
                    name = f'APR to APY',
                    value = f'{val:,.2f}% APR is equal to {APYfromAPR_daily:,.2f}% APY. $1000 will make about ${1000*val/100/365:,.2f} per day.',
                    inline = True
                    )
            embed.add_field(
                    name = f'APY to APR',
                    value = f'{val:,.2f}% APY is equal to {APRfromAPY_daily:,.2f}% APR. $1000 will make about ${1000*APRfromAPY_daily/100/365:,.2f} per day.',
                    inline = True
                    )
            embed.add_field(name = 'Compounded Weekly', value = 'If you redeem and reinvest rewards weekly...', inline=False)
            embed.add_field(
                    name = f'APR to APY',
                    value = f'{val:,.2f}% APR is equal to {APYfromAPR_weekly:,.2f}% APY. $1000 will make about ${1000*val/100/365:,.2f} per day.',
                    inline = True
                    )
            embed.add_field(
                    name = f'APY to APR',
                    value = f'{val:,.2f}% APY is equal to {APRfromAPY_weekly:,.2f}% APR. $1000 will make about ${1000*APRfromAPY_weekly/100/365:,.2f} per day.',
                    inline = True
                    )
            await msg.channel.send(embed=embed)
        if '!supply' in msg.content:
            embed = discord.Embed(
                    title=':bar_chart: **What is the FARM token supply?**',
                    )
            embed.add_field(
                    name = 'Maximum Supply',
                    value = 'Emission is capped at 690,420 FARM tokens. 630,741.56 (91.4%) will be emitted in the first year.',
                    inline = False
                    )
            if 'week' in msg.content:
                    weeknum = msg.content.split(' ')[-1]
                    emissions_this_week, supply_this_week = emissions(weeknum)
                    embed.add_field(
                            name = f'Emissions during Week {weeknum}',
                            value = f'{emissions_this_week:,.2f} FARM will be emitted',
                            inline = True
                            )
                    embed.add_field(
                            name = f'Supply at the end of Week {weeknum}',
                            value = f'{supply_this_week:,.2f} FARM total supply',
                            inline = True
                            )
            await msg.channel.send(embed=embed)
        if '!trade' in msg.content:
            embed = discord.Embed(
                    title='**How To Buy FARM :bar_chart:**',
                    )
            embed.add_field(
                    name = 'Token Info :mag:',
                    value = '[0xa0246c9032bC3A600820415aE600c6388619A14D](https://etherscan.io/address/0xa0246c9032bc3a600820415ae600c6388619a14d)',
                    inline = False
                    )
            embed.add_field(
                    name = 'Uniswap :arrows_counterclockwise:',
                    value = '[swap now](https://app.uniswap.org/#/swap?outputCurrency=0xa0246c9032bc3a600820415ae600c6388619a14d), '
                            '[pool info](https://uniswap.info/token/0xa0246c9032bc3a600820415ae600c6388619a14d)',
                    inline = True
                    )
            embed.add_field(
                    name = 'DEX Aggregators :arrow_right::arrow_left:',
                    value = '[debank](https://debank.com/swap?to=0xa0246c9032bc3a600820415ae600c6388619a14d), '
                            '[1inch](https://1inch.exchange/#/USDC/FARM), '
                            '[limit orders](https://1inch.exchange/#/limit-order/USDC/FARM)',
                    inline = True
                    )
            embed.add_field(
                    name = 'Trading Stats :chart_with_upwards_trend:',
                    value = '[CoinGecko](https://www.coingecko.com/en/coins/harvest-finance), '
                            '[CoinMarketCap](https://coinmarketcap.com/currencies/harvest-finance/), '
                            '[DeBank](https://debank.com/projects/harvest), '
                            '[dapp.com](https://www.dapp.com/app/harvest-finance), '
                            #'[defiprime](https://defiprime.com/product/harvest), '
                            'defipulse (soon!)',
                    inline = False
                    )
            await msg.channel.send(embed=embed)
        if '!vault' in msg.content:
            vault = msg.content.split(' ')[-1].lower()
            underlying = vault[1:]
            address, shareprice, vault_total, vault_buffer, vault_target, vault_strat, vault_strat_future, vault_strat_future_time = get_vaultstate(vault)
            vault_invested = vault_total - vault_buffer
            embed = discord.Embed(
                    title=f'{vault} Vault State :bank::mag:',
                    description=f':map: {vault} address: [{address}](https://etherscan.io/address/{address})\n'
                                f':moneybag: {vault} share price = {shareprice} {underlying}\n'
                                f':sponge: {underlying} withdrawal buffer = {vault_buffer:,.4f} {underlying}\n'
                                f':bar_chart: {underlying} invested = {vault_invested:,.4f} '
                                f'{underlying} ({100*vault_invested/vault_total:0.2f}%, target {100*vault_target:0.2f}%)\n'
                                f':compass: vault strategy: [{vault_strat}](https://etherscan.io/address/{vault_strat})\n'
                    )
            if vault_strat_future_time != 0:
                vault_update_dt = datetime.datetime.fromtimestamp(vault_strat_future_time)
                embed.description += f':rocket: future strategy: [{vault_strat_future}](https://etherscan.io/address/{vault_strat_future})\n'
                vault_update_timeleft = ( vault_update_dt - datetime.datetime.now() )
                if vault_update_timeleft.total_seconds() < 0:
                    embed.description += f':alarm_clock: future strategy can be activated at any time; [subscribe to updates on Twitter](https://twitter.com/farmer_fud)'
                else:
                    embed.description += f':alarm_clock: future strategy can be activated at {vault_update_dt} GMT '
                    embed.description += f'({vault_update_timeleft.total_seconds()/3600:.1f} hours); [subscribe to updates on Twitter](https://twitter.com/farmer_fud)'
            else:
                embed.description += f':alarm_clock: no strategy updates are pending; [subscribe to updates on Twitter](https://twitter.com/farmer_fud)'
            await msg.channel.send(embed=embed)
        if '!profitshare' in msg.content:
            ps_address = vault_addr['profitshare']['addr']
            ps_deposits, ps_rewardperday, ps_rewardfinish, ps_stake_frac = get_profitsharestate()
            ps_apr = 100* (ps_rewardperday / ps_deposits) * 365
            ps_timeleft = ( ps_rewardfinish - datetime.datetime.now() )
            embed = discord.Embed(
                    title=f':bank::mag: FARM Profit Sharing',
                    description=f':map: Profitshare address: [{ps_address}](https://etherscan.io/address/{ps_address})\n'
                                f':moneybag: Profitshare deposits: `{ps_deposits:,.2f}` FARM (`{100*ps_stake_frac:0.2f}%` of supply)\n'
                                f':bar_chart: Profitshare rewards per day: `{ps_rewardperday:,.2f}` FARM'
                                f' (`{ps_apr:.2f}%` instantaneous APR)\n'
                                f':alarm_clock: Current harvests pay out until: `{ps_rewardfinish} GMT`'
                                f' (`{ps_timeleft.total_seconds()/3600:.1f}` hours)'
                    )
            await msg.channel.send(embed=embed)
        if '!uniswap' in msg.content:
            uni_addr, uni_deposit_farm, uni_deposit_usdc, uni_farm_frac = get_uniswapstate()
            embed = discord.Embed(
                    title=f':mag: FARM:USDC Uniswap Pool',
                    description=f':bank: Uniswap contract: [{uni_addr}](https://etherscan.io/address/{uni_addr})\n'
                                f':moneybag: Liquidity: `{uni_deposit_farm:,.2f}` FARM (`{100*uni_farm_frac:.2f}%` of supply), `{uni_deposit_usdc:,.2f}` USDC\n'
                                f':arrows_counterclockwise: [Trade FARM](https://app.uniswap.org/#/swap?outputCurrency=0xa0246c9032bc3a600820415ae600c6388619a14d), '
                                f'[Add Liquidity](https://app.uniswap.org/#/add/0xa0246c9032bC3A600820415aE600c6388619A14D/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48), '
                                f'[Remove Liquidity](https://app.uniswap.org/#/remove/0xa0246c9032bC3A600820415aE600c6388619A14D/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48)\n'
                                f':bar_chart: [FARM:USDC Uniswap chart](https://beta.dex.vision/?ticker=UniswapV2:FARMUSDC-0x514906FC121c7878424a5C928cad1852CC545892&interval=15)'
                    )
            await msg.channel.send(embed=embed)
        if '!tvl' in msg.content:
            embed = discord.Embed(
                    title = 'Total Value Locked in Harvest',
                    description = ':bar_chart: Calculated with :bar_chart:'
                    )
            embed.add_field(
                    name = 'WBTC',
                    value = f'`${prices["wbtc"]:,.2f}` :moneybag:',
                    inline = True
                    )
            embed.add_field(
                    name = 'ETH',
                    value = f'`${prices["weth"]:,.2f}` :moneybag:',
                    inline = True
                    )
            embed.add_field(
                    name = ':bank: Vaults :bank:',
                    value = '```'+
                            tvl_format('ETH', locked['weth'])+
                            tvl_format('WBTC', locked['wbtc'])+
                            tvl_format('3CRV', locked['3crv'])+
                            tvl_format('yCRV', locked['ycrv'])+
                            tvl_format('CRV:TBTC', locked['crvtbtc'])+
                            tvl_format('CRV:COMPOUND', locked['crvcompound'])+
                            tvl_format('CRV:BUSD', locked['crvbusd'])+
                            tvl_format('CRV:USDN', locked['crvusdn'])+
                            tvl_format('CRV:RENWBTC', locked['crvrenwbtc'])+
                            tvl_format('RENBTC', locked['renbtc'])+
                            tvl_format('USDC', locked['usdc'])+
                            tvl_format('USDT', locked['usdt'])+
                            tvl_format('TUSD', locked['tusd'])+
                            tvl_format('DAI', locked['dai'])+
                            tvl_format('SUSHI-ETH-WBTC', locked['sushi-eth-wbtc'])+
                            tvl_format('SUSHI-ETH-DAI', locked['sushi-eth-dai'])+
                            tvl_format('SUSHI-ETH-USDC', locked['sushi-eth-usdc'])+
                            tvl_format('SUSHI-ETH-USDT', locked['sushi-eth-usdt'])+
                            tvl_format('PROFIT SHARE', locked['farm'])+
                            tvl_format('FARM/USDC UNI LP', locked['lp'])+
                            '```',
                    inline = False
                    )
            embed.add_field(
                    name = 'Total',
                    value = f':bank::moneybag: `${locked["total"]:,.0f}` :moneybag::bank:',
                    inline = False
                    )
            await msg.channel.send(embed=embed)

def human_readable(number):
    for unit in ['','K','M','B']:
        if abs(number) < 1000.0:
            return f'{number:,.2f}{unit}'
        number /= 1000.0
    return f'{number:,.2f}T'

def tvl_format(left:str, right:float, char:int = 16):
    right = human_readable(right)
    string = left.ljust(char, ' ')+right.rjust(8, ' ')+'\n'
    return string

def get_lockedinvault(token):
    vault_contract = w3.eth.contract(address=vault_addr[token]['addr'], abi=VAULT_ABI)
    vault_decimals = int(vault_addr[token]['decimals'])
    vault_total = vault_contract.functions['underlyingBalanceWithInvestment']().call()*10**(-1*vault_decimals)
    return vault_total

def get_tokenprice(token, id):
    pool_contract = w3.eth.contract(address=tokens_price[token]['addr'], abi=UNIPOOL_ABI)
    poolvals = pool_contract.functions['getReserves']().call()
    price = controller_contract.functions['quote'](10**(tokens_price[token]['decimals0' if (id == 0) else 'decimals1']), poolvals[id], poolvals[1 if (id == 0) else 0]).call()*10**(-1*tokens_price[token]['decimals1' if (id == 0) else 'decimals0'])
    return price

def get_lptokenprice(token, price0, price1):
    pool_contract = w3.eth.contract(address=tokens_price[token]['addr'], abi=UNIPOOL_ABI)
    poolvals = pool_contract.functions['getReserves']().call()
    price = (poolvals[0]*10**(-1*tokens_price[token]['decimals0'])*price0+poolvals[1]*10**(-1*tokens_price[token]['decimals1'])*price1)/(pool_contract.functions['totalSupply']().call()*10**(-1*tokens_price[token]['decimalsTotal']))
    return price

def get_curveprice(token):
    pool_contract = w3.eth.contract(address=tokens_price[token]['addr'], abi=CURVEPOOL_ABI)
    return pool_contract.functions['get_virtual_price']().call()*10**(-1*tokens_price[token]['decimalsTotal'])

def get_lockedfarm():
    lp_contract = w3.eth.contract(address=UNIPOOL_ADDR, abi=UNIPOOL_ABI)
    poolvals = lp_contract.functions['getReserves']().call()
    locked_lp = poolvals[0]*10**-18*prices['farm']+poolvals[1]*10**-6
    ps_contract = w3.eth.contract(address=vault_addr['profitshare']['addr'], abi=UNIPOOL_ABI)
    locked_ps = ps_contract.functions['totalSupply']().call()*10**-18*prices['farm']
    return locked_ps, locked_lp

@tasks.loop(seconds=310)
async def update_tvl():
    global locked, prices
    print('fetching tvl data...')
    start = datetime.datetime.now()

    for s in ['usdt','usdc','dai','tusd']: prices[s] = 1
    for c in ['3crv','ycrv','crvcompound','crvbusd','crvusdn']: prices[c] = get_curveprice(c)
    prices['weth'] = get_tokenprice('uni-eth-usdc', 1)*prices['usdc']
    prices['wbtc'] = get_tokenprice('uni-eth-wbtc', 0)*prices['weth']
    prices['renbtc'] = prices['wbtc']
    prices['crvtbtc'] = get_curveprice('crvtbtc')*prices['wbtc']
    prices['crvrenwbtc'] = get_curveprice('crvrenwbtc')*prices['wbtc']
    prices['sushi-eth-wbtc'] = get_lptokenprice('sushi-eth-wbtc', prices['wbtc'], prices['weth'])
    prices['sushi-eth-dai'] = get_lptokenprice('sushi-eth-dai', prices['dai'], prices['weth'])
    prices['sushi-eth-usdc'] = get_lptokenprice('sushi-eth-usdc', prices['usdc'], prices['weth'])
    prices['sushi-eth-usdt'] = get_lptokenprice('sushi-eth-usdt', prices['weth'], prices['usdt'])
    
    for a in assets:
        if a in ['total','farm','lp']: pass
        else: locked[a] = get_lockedinvault('f'+a)*prices[a]

    locked['farm'], locked['lp'] = get_lockedfarm() 
    locked['total'] = 0
    for a in assets: 
        if a != 'total': locked['total'] += locked[a]
    print (f'TVL ${locked["total"]:,.4f} fetched in {(datetime.datetime.now()-start).total_seconds()}s')

def get_uniswapstate():
    uni_addr = UNIPOOL_ADDR
    poolvals = pool_contract.functions['getReserves']().call()
    uni_deposit_farm = poolvals[0]*10**-18
    uni_deposit_usdc = poolvals[1]*10**-6
    farm_contract = w3.eth.contract(address=FARM_ADDR, abi=VAULT_ABI)
    farm_totalsupply = farm_contract.functions['totalSupply']().call()*10**-18
    uni_farm_frac = uni_deposit_farm / farm_totalsupply
    return (uni_addr, uni_deposit_farm, uni_deposit_usdc, uni_farm_frac)


def get_profitsharestate():
    ps_address = vault_addr['profitshare']['addr']
    ps_contract = w3.eth.contract(address=ps_address, abi=PS_ABI)
    lp_addr = ps_contract.functions['lpToken']().call()
    lp_contract = w3.eth.contract(address=lp_addr, abi=VAULT_ABI)
    ps_decimals = lp_contract.functions['decimals']().call()
    lp_totalsupply = lp_contract.functions['totalSupply']().call()*10**(-1*ps_decimals)
    ps_rewardrate = ps_contract.functions['rewardRate']().call()
    ps_totalsupply = ps_contract.functions['totalSupply']().call()*10**(-1*ps_decimals)
    ps_rewardfinish = ps_contract.functions['periodFinish']().call()
    ps_rewardperday = ps_rewardrate * 3600 * 24 * 10**(-1*ps_decimals)
    ps_rewardfinishdt = datetime.datetime.fromtimestamp(ps_rewardfinish)
    ps_stake_frac = ps_totalsupply / lp_totalsupply
    return (ps_totalsupply, ps_rewardperday, ps_rewardfinishdt, ps_stake_frac)

def get_vaultstate(vault):
    vault_address = vault_addr[vault]['addr']
    vault_contract = w3.eth.contract(address=vault_address, abi=VAULT_ABI)
    vault_strat = vault_contract.functions['strategy']().call()
    vault_strat_future = vault_contract.functions['futureStrategy']().call()
    vault_strat_future_time = int(vault_contract.functions['strategyUpdateTime']().call())
    vault_decimals = int(vault_contract.functions['decimals']().call())
    vault_shareprice = vault_contract.functions['getPricePerFullShare']().call()*10**(-1*vault_decimals)
    vault_total = vault_contract.functions['underlyingBalanceWithInvestment']().call()*10**(-1*vault_decimals)
    vault_buffer = vault_contract.functions['underlyingBalanceInVault']().call()*10**(-1*vault_decimals)
    vault_target_numerator = vault_contract.functions['vaultFractionToInvestNumerator']().call()
    vault_target_denominator = vault_contract.functions['vaultFractionToInvestDenominator']().call()
    vault_target = vault_target_numerator / vault_target_denominator
    return (vault_address, vault_shareprice, vault_total, vault_buffer, vault_target, vault_strat, vault_strat_future, vault_strat_future_time)

def main():
    client.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    main()


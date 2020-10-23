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
ONE_18DEC = 1000000000000000000

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
}


vault_addr = {
    'fdai'        : {'addr': '0xab7FA2B2985BCcfC13c6D86b1D5A17486ab1e04C',},
    'fusdc'       : {'addr': '0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE',},
    'fusdt'       : {'addr': '0x053c80eA73Dc6941F518a68E2FC52Ac45BDE7c9C',},
    'fwbtc'       : {'addr': '0x5d9d25c7C457dD82fc8668FFC6B9746b674d4EcB',},
    'frenbtc'     : {'addr': '0xC391d1b08c1403313B0c28D47202DFDA015633C4',},
    'fcrvrenwbtc' : {'addr': '0x9aA8F427A17d6B0d91B6262989EdC7D45d6aEdf8', 'startblock': 10815917},
    'fweth'       : {'addr': '0xFE09e53A81Fe2808bc493ea64319109B5bAa573e',},
    'fycrv'       : {'addr': '0xF2B223Eb3d2B382Ead8D85f3c1b7eF87c1D35f3A',},
    'ftusd'       : {'addr': '0x7674622c63Bee7F46E86a4A5A18976693D54441b',},
    'funi-eth-wbtc': {'addr': '0x01112a60f427205dcA6E229425306923c3Cc2073',},
    'funi-eth-usdt': {'addr': '0x7DDc3ffF0612E75Ea5ddC0d6Bd4e268f70362Cff',},
    'funi-eth-usdc': {'addr': '0xA79a083FDD87F73c2f983c5551EC974685D6bb36',},
    'funi-eth-dai':  {'addr': '0x307E2752e8b8a9C29005001Be66B1c012CA9CDB7',},
    'fsushi-wbtc-tbtc': {'addr': '0xF553E1f826f42716cDFe02bde5ee76b2a52fc7EB',},
}

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

@tasks.loop(seconds=120)
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
            address, shareprice, vault_total, vault_buffer, vault_target = get_vaultstate(vault)
            vault_invested = vault_total - vault_buffer
            embed = discord.Embed(
                    title=f'{vault} Vault State :bank::mag:',
                    description=f':map: {vault} address: [{address}](https://etherscan.io/address/{address})\n'
                                f':moneybag: {vault} share price = {shareprice} {underlying}\n'
                                f':sponge: {underlying} withdrawal buffer = {vault_buffer:,.4f} {underlying}\n'
                                f':bar_chart: {underlying} invested = {vault_invested:,.4f} '
                                f'{underlying} ({100*vault_invested/vault_total:0.2f}%, target {100*vault_target:0.2f}%)\n'
                    )
            await msg.channel.send(embed=embed)

def get_vaultstate(vault):
    vault_address = vault_addr[vault]['addr']
    vault_contract = w3.eth.contract(address=vault_address, abi=VAULT_ABI)
    vault_decimals = vault_contract.functions['decimals']().call()
    vault_shareprice = vault_contract.functions['getPricePerFullShare']().call()*10**(-1*vault_decimals)
    vault_total = vault_contract.functions['underlyingBalanceWithInvestment']().call()*10**(-1*vault_decimals)
    vault_buffer = vault_contract.functions['underlyingBalanceInVault']().call()*10**(-1*vault_decimals)
    vault_target_numerator = vault_contract.functions['vaultFractionToInvestNumerator']().call()
    vault_target_denominator = vault_contract.functions['vaultFractionToInvestDenominator']().call()
    vault_target = vault_target_numerator / vault_target_denominator
    return (vault_address, vault_shareprice, vault_total, vault_buffer, vault_target)

def main():
    client.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    main()

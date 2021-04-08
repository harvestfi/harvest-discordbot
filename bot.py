#!/usr/bin/env python

import math
import requests
import datetime
import time
import random
import asyncio
import discord
import os
import re
from discord.ext.commands import Bot
from discord.ext import commands, tasks
from web3 import Web3
from dotenv import load_dotenv

load_dotenv(override=True)

DISCORD_WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
NODE_URL = os.getenv("NODE_URL")
NODE_URL_MATIC = os.getenv("NODE_URL_MATIC")
NODE_URL_BSC = os.getenv("NODE_URL_BSC")
EXPLORER_MATIC = 'https://explorer-mainnet.maticvigil.com/'
UNIROUTER_ADDR = os.getenv("UNIROUTER_ADDR")
UNIROUTER_ABI = os.getenv("UNIROUTER_ABI")
UNIPOOL_ABI = os.getenv("UNIPOOL_ABI")
MOONISWAP_ABI = os.getenv("MOONISWAP_ABI")
VAULT_ABI = os.getenv("VAULT_ABI")
PS_ABI = os.getenv("PS_ABI")
POOL_ABI = os.getenv("POOL_ABI")
TOKEN_ABI = os.getenv("TOKEN_ABI")
ROOTCHAIN_ABI = os.getenv("ROOTCHAIN_ABI")
FARM_ADDR = '0xa0246c9032bC3A600820415aE600c6388619A14D'
FARM_ADDR_BSC = '0x4B5C23cac08a567ecf0c1fFcA8372A45a5D33743'
MODEL_ADDR = '0x814055779F8d2F591277b76C724b7AdC74fb82D9'
TRACTOR_ADDR = '0xbed04C43E74150794F2ff5b62B4F73820EDaF661'
ROOTCHAIN_ADDR = '0x86E4Dc95c7FBdBf52e33D563BbDB00823894C287'
TRACTOR_ETH_MINLIMIT = 3.0
UPDATE_SECONDS = 10

ONE_18DEC = 1000000000000000000
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
BLOCKS_PER_DAY = int((60/13.2)*60*24) #~7200 at 12 sec

w3 = Web3(Web3.HTTPProvider(NODE_URL))
m3 = Web3(Web3.HTTPProvider(NODE_URL_MATIC))
b3 = Web3(Web3.HTTPProvider(NODE_URL_BSC))
controller_contract = w3.eth.contract(address=UNIROUTER_ADDR, abi=UNIROUTER_ABI)

ASSETS = {
    'FARM': {
        'addr':'0xa0246c9032bC3A600820415aE600c6388619A14D',
        'main_quotetoken':'ETH',
        'pools': {
            'USDC': {
                'router':UNIROUTER_ADDR,
                'addr':'0x514906FC121c7878424a5C928cad1852CC545892',
                'basetoken_index': 0,
                'quotetoken_index': 1,
                'rewards':'0x99b0d6641A63Ce173E6EB063b3d3AED9A35Cf9bf',
                'oracles': [],
                #'oracles': [
                #    {'addr':'0xBb2b8038a1640196FbE3e38816F3e67Cba72D940','basetoken_index':0,'quotetoken_index':1,},
                #    {'addr':'0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc','basetoken_index':1,'quotetoken_index':0,},
                #    ],
                },
        'ETH': {
                'router':UNIROUTER_ADDR,
                'addr':'0x56feAccb7f750B997B36A68625C7C596F0B41A58',
                'basetoken_index': 0,
                'quotetoken_index': 1,
                'rewards':'0x6555c79a8829b793F332f1535B0eFB1fE4C11958',
                'oracles': [
                #    {'addr':'0xBb2b8038a1640196FbE3e38816F3e67Cba72D940','basetoken_index':0,'quotetoken_index':1,},
                    {'addr':'0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc','basetoken_index':1,'quotetoken_index':0,},
                    ],
                },
            },

        },
    'GRAIN': {
        'addr':'0x6589fe1271A0F29346796C6bAf0cdF619e25e58e',
        'main_quotetoken':'FARM',
        'pools': {
            'FARM': {
                'router':UNIROUTER_ADDR,
                'addr':'0xB9Fa44B0911F6D777faAb2Fa9d8Ef103f25Ddf49',
                'basetoken_index': 0,
                'quotetoken_index': 1,
                'rewards':'',
                'oracles': [
                    {'addr':'0x514906FC121c7878424a5C928cad1852CC545892','basetoken_index':0,'quotetoken_index':1,},
                    ],
                },
            },
        },

}

## this is used for the portfolio command
vaults = {
#  '0x8e298734681adbfC41ee5d17FF8B0d6d803e7098': {'asset': 'fWETH-v0', 'decimals': 18,},
#  '0xe85C8581e60D7Cd32Bbfd86303d2A4FA6a951Dac': {'asset': 'fDAI-v0', 'decimals': 18,},
#  '0xc3F7ffb5d5869B3ade9448D094d81B0521e8326f': {'asset': 'fUSDC-v0', 'decimals': 6,},
#  '0xc7EE21406BB581e741FBb8B21f213188433D9f2F': {'asset': 'fUSDT-v0', 'decimals': 6,},
#  '0xF2B223Eb3d2B382Ead8D85f3c1b7eF87c1D35f3A': {'asset': 'FARM yDAI+yUSDC+yUSDT+yTUSD', 'decimals': 18,},
#  '0xfBe122D0ba3c75e1F7C80bd27613c9f35B81FEeC': {'asset': 'fRenBTC-v0', 'decimals': 8,},
#  '0xc07EB91961662D275E2D285BdC21885A4Db136B0': {'asset': 'fWBTC-v0', 'decimals': 8,},
#  '0x192E9d29D43db385063799BC239E772c3b6888F3': {'asset': 'fCRVRenWBTC-v0', 'decimals': 18,},
#  '0xb1FeB6ab4EF7d0f41363Da33868e85EB0f3A57EE': {'asset': 'fUNI-ETH-WBTC-v0', 'decimals': 18,},
#  '0xB19EbFB37A936cCe783142955D39Ca70Aa29D43c': {'asset': 'fUNI-ETH-USDT-v0', 'decimals': 18,},
#  '0x63671425ef4D25Ec2b12C7d05DE855C143f16e3B': {'asset': 'fUNI-ETH-USDC-v0', 'decimals': 18,},
#  '0x1a9F22b4C385f78650E7874d64e442839Dc32327': {'asset': 'fUNI-ETH-DAI-v0', 'decimals': 18,},
  '0xFE09e53A81Fe2808bc493ea64319109B5bAa573e': {'asset': 'fWETH', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0xab7FA2B2985BCcfC13c6D86b1D5A17486ab1e04C': {'asset': 'fDAI', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE': {'asset': 'fUSDC', 'decimals': 6, 'type': 'timelock', 'lptype': 'none',},
  '0x053c80eA73Dc6941F518a68E2FC52Ac45BDE7c9C': {'asset': 'fUSDT', 'decimals': 6, 'type': 'timelock', 'lptype': 'none',},
  '0x7674622c63Bee7F46E86a4A5A18976693D54441b': {'asset': 'fTUSD', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x5d9d25c7C457dD82fc8668FFC6B9746b674d4EcB': {'asset': 'fWBTC', 'decimals': 8, 'type': 'timelock', 'lptype': 'none',},
  '0xC391d1b08c1403313B0c28D47202DFDA015633C4': {'asset': 'fRENBTC', 'decimals': 8, 'type': 'timelock', 'lptype': 'none',},
  '0x8Bf3c1c7B1961764Ecb19b4FC4491150ceB1ABB1': {'asset': 'fDSD', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x45a9e027DdD8486faD6fca647Bb132AD03303EC2': {'asset': 'fESD', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x371E78676cd8547ef969f89D2ee8fA689C50F86B': {'asset': 'fBAC', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x71B9eC42bB3CB40F017D8AD8011BE8e384a95fa5': {'asset': 'fCRV-3POOL', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x0FE4283e0216F94f5f9750a7a11AC54D3c9C38F3': {'asset': 'fCRV-YPOOL', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x998cEb152A42a3EaC1f555B1E911642BeBf00faD': {'asset': 'fCRV-COMP', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x4b1cBD6F6D8676AcE5E412C78B7a59b4A1bbb68a': {'asset': 'fCRV-BUSD', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0xB8671E33fcFC7FEA2F7a3Ea4a117F065ec4b009E': {'asset': 'fCRV-GUSD', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x29780C39164Ebbd62e9DDDE50c151810070140f2': {'asset': 'fCRV-HUSD', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x683E683fBE6Cf9b635539712c999f3B3EdCB8664': {'asset': 'fCRV-USDN', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x84A1DfAdd698886A614fD70407936816183C0A02': {'asset': 'fCRV-UST', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x6eb941BD065b8a5bd699C5405A928c1f561e2e5a': {'asset': 'fCRV-EURS', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x9aA8F427A17d6B0d91B6262989EdC7D45d6aEdf8': {'asset': 'fCRV-RENWBTC', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x640704D106E79e105FDA424f05467F005418F1B5': {'asset': 'fCRV-TBTC', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0xCC775989e76ab386E9253df5B0c0b473E22102E2': {'asset': 'fCRV-HBTC', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x966A70A4d3719A6De6a94236532A0167d5246c72': {'asset': 'fCRV-OBTC', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0xc27bfE32E0a934a12681C1b35acf0DBA0e7460Ba': {'asset': 'fCRV-stETH', 'decimals': 18, 'type': 'timelock', 'lptype': 'none',},
  '0x6Bccd7E983E438a56Ba2844883A664Da87E4C43b': {'asset': 'fUNI-BAC:DAI', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0xf8b7235fcfd5A75CfDcC0D7BC813817f3Dd17858': {'asset': 'fUNI-BAS:DAI', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x633C4861A4E9522353EDa0bb652878B079fb75Fd': {'asset': 'fUNI-DAI:BSGS', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x639d4f3F41daA5f4B94d63C2A5f3e18139ba9E54': {'asset': 'fUNI-DAI:BSG', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x11804D69AcaC6Ae9466798325fA7DE023f63Ab53': {'asset': 'fUNI-UST:mAAPL', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x8334A61012A779169725FcC43ADcff1F581350B7': {'asset': 'fUNI-mAMZN:UST', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x07DBe6aA35EF70DaD124f4e2b748fFA6C9E1963a': {'asset': 'fUNI-mGOOGL:UST', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0xC800982d906671637E23E031e907d2e3487291Bc': {'asset': 'fUNI-mTSLA:UST', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x01112a60f427205dcA6E229425306923c3Cc2073': {'asset': 'fUNI-ETH:WBTC', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x7DDc3ffF0612E75Ea5ddC0d6Bd4e268f70362Cff': {'asset': 'fUNI-ETH:USDT', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0xA79a083FDD87F73c2f983c5551EC974685D6bb36': {'asset': 'fUNI-ETH:USDC', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x307E2752e8b8a9C29005001Be66B1c012CA9CDB7': {'asset': 'fUNI-ETH:DAI', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0xF553E1f826f42716cDFe02bde5ee76b2a52fc7EB': {'asset': 'fSUSHI-WBTC:TBTC', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x6F14165c6D529eA3Bfe1814d0998449e9c8D157D': {'asset': 'fSUSHI-MIC:USDT', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x145f39B3c6e6a885AA6A8fadE4ca69d64bab69c8': {'asset': 'fSUSHI-MIS:USDT', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x5aDe382F38A09A1F8759D06fFE2067992ab5c78e': {'asset': 'fSUSHI-SUSHI:ETH', 'decimals': 18, 'type': 'timelock', 'lptype': 'uniswap',},
  '0x8e53031462E930827a8d482e7d80603B1f86e32d': {'asset': 'f1INCH-ETH:DAI', 'decimals': 18, 'type': 'timelock', 'lptype': '1inch',},
  '0x859222DD0B249D0ea960F5102DaB79B294d6874a': {'asset': 'f1INCH-ETH:WBTC', 'decimals': 18, 'type': 'timelock', 'lptype': '1inch',},
  '0x4bf633A09bd593f6fb047Db3B4C25ef5B9C5b99e': {'asset': 'f1INCH-ETH:USDT', 'decimals': 18, 'type': 'timelock', 'lptype': '1inch',},
  '0xD162395C21357b126C5aFED6921BC8b13e48D690': {'asset': 'f1INCH-ETH:USDC', 'decimals': 18, 'type': 'timelock', 'lptype': '1inch',},
#  '0x8f5adC58b32D4e5Ca02EAC0E293D35855999436C': {'asset': 'profitshare', 'decimals': 18, },
}

# this is used for all other vault status commands
vault_addr = {
    'fdai'        : {'addr': '0xab7FA2B2985BCcfC13c6D86b1D5A17486ab1e04C',
                     'pool': '0x15d3A64B2d5ab9E152F16593Cdebc4bB165B5B4A',
                     },
    'fusdc'       : {'addr': '0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE',
                     'pool': '0x4F7c28cCb0F1Dbd1388209C67eEc234273C878Bd',
                     },
    'fusdt'       : {'addr': '0x053c80eA73Dc6941F518a68E2FC52Ac45BDE7c9C',
                     'pool': '0x6ac4a7AB91E6fD098E13B7d347c6d4d1494994a2',
                     },
    'fwbtc'       : {'addr': '0x5d9d25c7C457dD82fc8668FFC6B9746b674d4EcB',
                     'pool': '0x917d6480Ec60cBddd6CbD0C8EA317Bcc709EA77B',
                     },
    'frenbtc'     : {'addr': '0xC391d1b08c1403313B0c28D47202DFDA015633C4',
                     'pool': '0x7b8Ff8884590f44e10Ea8105730fe637Ce0cb4F6',
                     },
    'fcrv-renwbtc' : {'addr': '0x9aA8F427A17d6B0d91B6262989EdC7D45d6aEdf8', 'startblock': 10815917,
                     'pool': '0xA3Cf8D1CEe996253FAD1F8e3d68BDCba7B3A3Db5',
                     },
    'fweth'       : {'addr': '0xFE09e53A81Fe2808bc493ea64319109B5bAa573e',
                     'pool': '0x3DA9D911301f8144bdF5c3c67886e5373DCdff8e',
                     },
    'ftusd'       : {'addr': '0x7674622c63Bee7F46E86a4A5A18976693D54441b',
                     'pool': '0xeC56a21CF0D7FeB93C25587C12bFfe094aa0eCdA',
                     },
    'funi-eth:wbtc': {'addr': '0x01112a60f427205dcA6E229425306923c3Cc2073',
                     'pool': '0xF1181A71CC331958AE2cA2aAD0784Acfc436CB93',
                     },
    'funi-eth:usdt': {'addr': '0x7DDc3ffF0612E75Ea5ddC0d6Bd4e268f70362Cff',
                     'pool': '0x75071F2653fBC902EBaff908d4c68712a5d1C960',
                     },
    'funi-eth:usdc': {'addr': '0xA79a083FDD87F73c2f983c5551EC974685D6bb36',
                     'pool': '0x156733b89Ac5C704F3217FEe2949A9D4A73764b5',
                     },
    'funi-eth:dai':  {'addr': '0x307E2752e8b8a9C29005001Be66B1c012CA9CDB7',
                     'pool': '0x7aeb36e22e60397098C2a5C51f0A5fB06e7b859c',
                     },
    'funi-eth:dpi':  {'addr': '0x2a32dcBB121D48C106F6d94cf2B4714c0b4Dfe48',
                     'pool': '0xAd91695b4BeC2798829ac7a4797E226C78f22Abd',
                     },
    'fsushi-wbtc:tbtc': {'addr': '0xF553E1f826f42716cDFe02bde5ee76b2a52fc7EB',
                     'pool': '0x9523FdC055F503F73FF40D7F66850F409D80EF34',
                     },
    'fsushi-eth:dai': {
        'addr': '0x203E97aa6eB65A1A02d9E80083414058303f241E',
        'pool': '0x76Aef359a33C02338902aCA543f37de4b01BA1FA',
        'underlying': '0xC3D03e4F041Fd4cD388c549Ee2A29a9E5075882f',
        },
    'fsushi-eth:usdt': {
        'addr': '0x64035b583c8c694627A199243E863Bb33be60745',
        'pool': '0xA56522BCA0A09f57B85C52c0Cc8Ba1B5eDbc64ef',
        'underlying': '0x06da0fd433C1A5d7a4faa01111c044910A184553',
        },
    'fsushi-eth:usdc': {
        'addr': '0x01bd09A1124960d9bE04b638b142Df9DF942b04a',
        'pool': '0x6B4e1E0656Dd38F36c318b077134487B9b0cf7a6',
        'underlying': '0x397FF1542f962076d0BFE58eA045FfA2d347ACa0',
        },
    'fsushi-eth:wbtc': {
        'addr': '0x5C0A3F55AAC52AA320Ff5F280E77517cbAF85524',
        'pool': '0xE2D9FAe95f1e68afca7907dFb36143781f917194',
        'underlying': '0xCEfF51756c56CeFFCA006cD410B03FFC46dd3a58',
        },
    'fsushi-eth:sushi': { # sushi:eth
        'addr': '0x5aDe382F38A09A1F8759D06fFE2067992ab5c78e',
        'pool': '0x16fBb193f99827C92A4CC22EFe8eD7390465BFa3',
        },
    'profitshare': {
        'addr': '0x8f5adC58b32D4e5Ca02EAC0E293D35855999436C',
        'pool': '0x25550Cccbd68533Fa04bFD3e3AC4D09f9e00Fc50',
        },
    'ifarm': {
        'addr': '0x1571eD0bed4D987fe2b498DdBaE7DFA19519F651',
        'pool': '',
        },
    'fcrv-3pool': {
        'addr': '0x71B9eC42bB3CB40F017D8AD8011BE8e384a95fa5',
        'pool': '0x27F12d1a08454402175b9F0b53769783578Be7d9',
        },
    'fcrv-ypool': {
        'addr': '0x0FE4283e0216F94f5f9750a7a11AC54D3c9C38F3',
        'pool': '0x6D1b6Ea108AA03c6993d8010690264BA96D349A8',
        },
    'fcrv-tbtc': {
        'addr': '0x640704D106E79e105FDA424f05467F005418F1B5',
        'pool': '0x017eC1772A45d2cf68c429A820eF374f0662C57c',
        },
    'fcrv-busd': {
        'addr': '0x4b1cBD6F6D8676AcE5E412C78B7a59b4A1bbb68a',
        'pool': '0x093C2ae5E6F3D2A897459aa24551289D462449AD',
        },
    'fcrv-usdn': {
        'addr': '0x683E683fBE6Cf9b635539712c999f3B3EdCB8664',
        'pool': '0xef4Da1CE3f487DA2Ed0BE23173F76274E0D47579',
        },
    'fcrv-comp': {
        'addr': '0x998cEb152A42a3EaC1f555B1E911642BeBf00faD',
        'pool': '0xC0f51a979e762202e9BeF0f62b07F600d0697DE1',
        },
    'fcrv-husd': {
        'addr': '0x29780C39164Ebbd62e9DDDE50c151810070140f2',
        'pool': '0x72C50e6FD8cC5506E166c273b6E814342Aa0a3c1',
        },
    'fcrv-hbtc': {
        'addr': '0xCC775989e76ab386E9253df5B0c0b473E22102E2',
        'pool': '0x01f9CAaD0f9255b0C0Aa2fBD1c1aA06ad8Af7254',
        },
    'fcrv-usdp': {
        'addr': '0x02d77f6925f4ef89EE2C35eB3dD5793f5695356f',
        'pool': '0x15AEB9B209FEC67c672dBF5113827daB0b80f390',
        },
    'uniswap': {
        'addr': '0x514906FC121c7878424a5C928cad1852CC545892',
        'pool': '0x99b0d6641A63Ce173E6EB063b3d3AED9A35Cf9bf',
        },
    'funi-bac:dai': {
        'addr': '0x6Bccd7E983E438a56Ba2844883A664Da87E4C43b',
        'pool': '0x797F1171DC5001B7A79ff7Dca68c9539329ccE48',
        },
    'funi-bas:dai': {
        'addr': '0xf8b7235fcfd5A75CfDcC0D7BC813817f3Dd17858',
        'pool': '0xf330891f02F8182D7D4e1A962ED0F3086D626020',
        },
    'fsushi-mic:usdt': {
        'addr': '0x6F14165c6D529eA3Bfe1814d0998449e9c8D157D',
        'pool': '0x98Ba5E432933E2D536e24A2C021deBb8404588C1',
        },
    'fsushi-mis:usdt': {
        'addr': '0x145f39B3c6e6a885AA6A8fadE4ca69d64bab69c8',
        'pool': '0xf4784d07136b5b10c6223134E8B36E1DC190725b',
        },
    'fcrv-obtc': {
        'addr': '0x966A70A4d3719A6De6a94236532A0167d5246c72',
        'pool': '0x91B5cD52fDE8dbAC37C95ECafEF0a70bA4c182fC',
        },
    'f1inch-eth:dai': {
#        'addr': '',
#        'pool': '',
        'addr': '0x8e53031462E930827a8d482e7d80603B1f86e32d',
        'pool': '0xDa5E9706274D88bbf1bD1877a9b462fC40cDcfAd',
        },
    'f1inch-eth:wbtc': {
        'addr': '0x859222DD0B249D0ea960F5102DaB79B294d6874a',
        'pool': '0x747318Cf3171D4E2a1A52bBD3Fcc9f9c690448B4',
        },
    'f1inch-eth:usdt': {
        'addr': '0x4bf633A09bd593f6fb047Db3B4C25ef5B9C5b99e',
        'pool': '0x2A80e0B572e7EF61Ef81EF05eC024e1e52Bd70BD',
        },
    'f1inch-eth:usdc': {
        'addr': '0xD162395C21357b126C5aFED6921BC8b13e48D690',
        'pool': '0x9a9A6148f7b0A9767AC1fdC67343D1e3E219FdDf',
        },
    'fdsd': {
        'addr': '0x8Bf3c1c7B1961764Ecb19b4FC4491150ceB1ABB1',
        'pool': '0x7c497298d9576499e17F9564CE4E13faa87A9b33',
        },
    'fesd': {
        'addr': '0x45a9e027DdD8486faD6fca647Bb132AD03303EC2',
        'pool': '0xDB9C2EbA87301e6951d6FBE7a458832eaab2137E',
        },
    'fbac': {
        'addr': '0x371E78676cd8547ef969f89D2ee8fA689C50F86B',
        'pool': '0x3cddE34C96eCB95A1232c9673e23f2dB5fA72280',
        },
    'funi-dai:bsgs': {
        'addr': '0x633C4861A4E9522353EDa0bb652878B079fb75Fd',
        'pool': '0x63e7D3F6e208ccE4967b7a0E6A50A397Af0b0E7A',
        },
    'funi-dai:bsg': {
        'addr': '0x639d4f3F41daA5f4B94d63C2A5f3e18139ba9E54',
        'pool': '0xf5b221E1d9C3a094Fb6847bC3E241152772BbbF8',
        },
    'fcrv-ust': {
        'addr': '0x84A1DfAdd698886A614fD70407936816183C0A02',
        'pool': '0xDdb5D3CCd968Df64Ce48b577776BdC29ebD3120e',
        },
    'fcrv-eurs': {
        'addr': '0x6eb941BD065b8a5bd699C5405A928c1f561e2e5a',
        'pool': '0xf4d50f60D53a230abc8268c6697972CB255Cd940',
        },
    'fcrv-steth': {
        'addr': '0xc27bfE32E0a934a12681C1b35acf0DBA0e7460Ba',
        'pool': '0x2E25800957742C52b4d69b65F9C67aBc5ccbffe6',
        },
    'funi-mtsla:ust': {
        'addr': '0xC800982d906671637E23E031e907d2e3487291Bc',
        'pool': '0x40C34B0E1bb6984810E17474c6B0Bcc6A6B46614',
        },
    'funi-mgoogl:ust': {
        'addr': '0x07DBe6aA35EF70DaD124f4e2b748fFA6C9E1963a',
        'pool': '0xfE83a00DF3A98dE218c08719FAF7e3741b220D0D',
        },
    'funi-mamzn:ust': {
        'addr': '0x8334A61012A779169725FcC43ADcff1F581350B7',
        'pool': '0x8Dc427Cbcc75cAe58dD4f386979Eba6662f5C158',
        },
    'funi-ust:maapl': { #ust:maapl
        'addr': '0x11804D69AcaC6Ae9466798325fA7DE023f63Ab53',
        'pool': '0xc02d1Da469d68Adc651Dd135d1A7f6b42F4d1A57',
        },
    'fcrv-gusd': {
        'addr': '0xB8671E33fcFC7FEA2F7a3Ea4a117F065ec4b009E',
        'pool': '0x538613A19Eb84D86a4CcfcB63548244A52Ab0B68',
        },
    'fcrv-aave': {
        'addr': '0xc3EF8C4043D7cf1D15B6bb4cd307C844E0BA9d42',
        'pool': '0x10f1fc85eAA1F064e38EEffDa82fBa414841f438',
        },
    'iFARM': {
        'addr': '0x1571eD0bed4D987fe2b498DdBaE7DFA19519F651',
        'pool': '',
        },
    'funi-wbtc:klon': { #wbtc:klon
        'addr': '0xB4E3fC276532f27Bd0F738928Ce083A3b064ba61',
        'pool': '0x719d70457658358f2e785B38307CfE24071b7417',
        },
    'funi-wbtc:kbtc': { #wbtc:kbtc
        'addr': '0x5cd9Db40639013A08d797A839C9BECD6EC5DCD4D',
        'pool': '0xdD496A6Ba1B4Cf2b3ef42dEf132e2B2c570941FE',
        },
    'fsushi-eth:ust': {
        'addr': '0x4D4D85c6a1ffE6Bb7a1BEf51c9E2282893feE521',
        'pool': '0x59eeb34065dB1621c68d26f37ffEFf3A89E5FA8b',
        },
    'funi-ust:mtwtr': { #ust:mtwtr
        'addr': '0xb37c79f954E3e1A4ACCC14A5CCa3E46F226038b7',
        'pool': '0x677AD66025063bE55B070685E618a84FF3dd62be',
        },
    'funi-ust:mnflx': { #ust:mnflx
        'addr': '0x99C2564C9D4767C13E13F38aB073D4758af396Ae',
        'pool': '0x937D4b84f139bec548b825FdCE33B172C5Bf755a',
        },
    'fcrv-link': {
        'addr': '0x24C562E24A4B5D905f16F2391E07213efCFd216E',
        'pool': '0x9c6FbDBF59808CD920fDb166c25E2E9FcF708dD1',
        },
    'fsushi': {
        'addr': '0x274AA8B58E8C57C4e347C8768ed853Eb6D375b48',
        'pool': '0xf550804Ebd6f89CdC9EC8E92CE8DE91A2F64a82E',
        },
    'fsushi-wbtc:eth-hodl': { #wbtc:eth
        'addr': '0xB677bcA369f2523F62862F88d83471D892dD55B9',
        'pool': '0x08aA65118996eaa61372B65978Cfa684F2C749b2',
        },
    'fsushi-eth:usdt-hodl': {
        'addr': '0x4D4B6f8EFb685b774234Fd427201b3a9bF36ffc8',
        'pool': '0x0c67FBa277A3FE1B0a792ef5bc798cBbDA15a7f5',
        },
    'fsushi-usdc:eth-hodl': { #usdc:eth
        'addr': '0x5774260CcD87F4FfFc4456260857207fc8BCb89A',
        'pool': '0x378C314028071C92efE15d6990B6cf93594fCB9D',
        },
    'fsushi-dai:eth-hodl': { #dai:eth
        'addr': '0x29EC64560ab14d3166222Bf07c3F29c4916E0027',
        'pool': '0xF5833723b150929D1Fddf785ED9D92eEe722387d',
        },
    'funi-rope20:eth': { #rope20:eth
        'addr': '0xAF9486E3DA0cE8d125aF9b256b3ecd104a3031B9',
        'pool': '0x14ac1BDdd9160866590C6c4ec16853A1510845b9',
        },
    'funi-dudes20:eth': { #dudes20:eth
        'addr': '0x1E5f4e7127ea3981551D2Bf97dCc8f17a4ECEbEf',
        'pool': '0x3B808A7d8CCdF8893d1360ff421beF4440376842',
        },
    'funi-eth:mask20': {
        'addr': '0xF2a671645D0DF54d2f03E9ad7916c8F7368D1C29',
        'pool': '0xC5fc56779b5925218D2Cdac093d0bFc6de7Cc2D1',
        },
    'funi-muse:eth': {
        'addr': '0xc45d471c77ff31C39474d68a5080Fe1FfACDBC04',
        'pool': '0x743BD82331CAe227Fa2c8c97f345A6846f8383b1',
        },
    'funi-mcat20:eth': {
        'addr': '0x0cA19915439C12B16C0A8C119eC05fA801365a15',
        'pool': '0xE7E1C3624188052a2367B63048a32A7429980113',
        },
    'f1inch-eth:1inch': {
        'addr': '0xFCA949E34ecd9dE519542CF02054DE707Cf361cE',
        'pool': '0x16b5089ED717409849b2748AC73adFbfE7ec0301',
        },
    'f1inch-1inch:usdc': {
        'addr': '0xF174DDDD9DBFfeaeA5D908a77d695a77e53025b3',
        'pool': '0x516658d83A68747C34FD5aeCba7068ad4bD4783d',
        },
    'f1inch-1inch:wbtc': {
        'addr': '0xDdB4669f39c03A6edA92ffB5B78A9C1a74615F1b',
        'pool': '0xd8a3C7d1dEcCB8445a4391F6052E5a0726f2F270',
        },
#    'f': {
#        'addr': '',
#        'pool': '',
#       },
}

earlyemissions = [
    57569.10,
    51676.20,
    26400.00,
    24977.50
]

update_index = 0

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
                name='node desynced',
                url='https://uniswap.info/token/0xa0246c9032bc3a600820415ae600c6388619a14d'
)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=activity_start)
    update_price.start()
    check_tractor.start()

@tasks.loop(seconds=UPDATE_SECONDS)
async def update_price():
    global update_index
    asset_list = list(ASSETS.keys())
    basetoken_name = asset_list[update_index % len(asset_list)]
    basetoken = ASSETS[basetoken_name]
    basetoken_addr = basetoken['addr']
    basetoken_contract = w3.eth.contract(address=basetoken_addr, abi=TOKEN_ABI)
    quotetoken_name = basetoken['main_quotetoken']
    pool = basetoken['pools'][quotetoken_name]
    pool_contract = w3.eth.contract(address=pool['addr'], abi=UNIPOOL_ABI)
    basetoken_index = pool['basetoken_index']
    quotetoken_index = pool['quotetoken_index']
    quotetoken_addr = pool_contract.functions[f'token{quotetoken_index}']().call()
    quotetoken_contract = w3.eth.contract(address=quotetoken_addr, abi=TOKEN_ABI)
    router_contract = w3.eth.contract(address=pool['router'], abi=UNIROUTER_ABI)

    # fetch pool state
    print(f'update_price: fetching pool reserves for {basetoken_name} ({basetoken_addr}) and {quotetoken_name} ({quotetoken_addr})...')
    poolvals = pool_contract.functions['getReserves']().call()

    # calculate price
    print(f'update_price: calculating price...')
    atoms_per_basetoken = 10**basetoken_contract.functions['decimals']().call()
    atoms_per_quotetoken = 10**quotetoken_contract.functions['decimals']().call()
    print(f'update_price: atoms per basetoken {basetoken_name}: {atoms_per_basetoken}; atoms per quotetoken {quotetoken_name}: {atoms_per_quotetoken}')
    token_price = router_contract.functions['quote'](atoms_per_basetoken, poolvals[basetoken_index], poolvals[quotetoken_index]).call() / atoms_per_quotetoken
    print(f'update_price: base pool price: {token_price}')
    oracle_price = 1
    for oracle in pool['oracles']:
        oracle_contract = w3.eth.contract(address=oracle['addr'], abi=UNIPOOL_ABI)
        oracle_reserves = oracle_contract.functions['getReserves']().call()
        oracle_basetoken = f'token{oracle["basetoken_index"]}'
        oracle_quotetoken = f'token{oracle["quotetoken_index"]}'
        atoms_per_oracle_basetoken = 10**w3.eth.contract(address=oracle_contract.functions[oracle_basetoken]().call(), abi=TOKEN_ABI).functions['decimals']().call()
        atoms_per_oracle_quotetoken = 10**w3.eth.contract(address=oracle_contract.functions[oracle_quotetoken]().call(), abi=TOKEN_ABI).functions['decimals']().call()
        oraclevals = oracle_contract.functions['getReserves']().call()
        oracle_price_step = router_contract.functions['quote'](atoms_per_oracle_basetoken, oraclevals[oracle['basetoken_index']], oraclevals[oracle['quotetoken_index']]).call()  / atoms_per_oracle_quotetoken
        oracle_price = oracle_price * oracle_price_step
    print(f'update_price: oracle price: {oracle_price}')
    price = token_price * oracle_price

    # update price
    price_decimals = max(-1 * math.floor(math.log10(price)) + 1, 2)
    print(f'update_price: updating the price...')
    msg = f'${price:.{price_decimals}f} {basetoken_name}'
    # twap hack
    #if (update_index % 3 == 0):
    #    msg = f'${get_twap():0.2f} FARM TWAP'

    new_price = discord.Streaming(name=msg,url=f'https://etherscan.io/token/basetoken["addr"]')
    print(f'update_price: post: {msg}')
    await client.change_presence(activity=new_price)
    update_index += 1


@tasks.loop(seconds=14400)
async def check_tractor():
    channel = client.get_channel(802268512079839302) #msig channel
    tractor_balance_eth_display = get_tractor_state()['eth']
    if (tractor_balance_eth_display < TRACTOR_ETH_MINLIMIT):
        print(f'Tractor balance low! {tractor_balance_eth_display:.4f} ETH')
        embed = discord.Embed(
                    title=':wrench: Tractor Maintenance Needed!',
                    description=f':map: tractor is parked at [{TRACTOR_ADDR}](https://etherscan.io/address/{TRACTOR_ADDR})\n'
                                f':fuelpump: fuel gauge low: {tractor_balance_eth_display:.4f} ETH',
                    )
        await channel.send(embed=embed)


@client.event
async def on_message(msg):
    if client.user.id != msg.author.id:
        if '!foo' in msg.content:
            await msg.channel.send('bar')
        if '!bot' in msg.content:
            embed = discord.Embed(
                    title='Autonomous Agricultural Assistant, at your service :tractor:',
                    description=':arrows_counterclockwise: `!uniswap`: FARM:ETH Uniswap pool stats\n'
                                ':farmer: `!profitshare`: FARM profit share pool stats\n'
                                ':bar_chart: `!trade`: FARM markets and trading\n'
                                ':teacher: `!apy {number}`: convert between APR and APY\n'
                                ':thinking: `!payout`: information on farming rewards\n'
                                ':bank: `!vault vaultname`: Harvest vault state of supported vaults\n'
                                ':lock: `f{coin}`, `funi-eth:{coin}`, `fsushi-eth:{coin}`\n'
                                ':dollar: LP $USD: `fcrv-ypool`, `fcrv-3pool`, `fcrv-comp`\n'
                                ':dollar: LP $USD: `fcrv-husd`, `fcrv-busd`, `fcrv-usdn`\n'
                                ':mountain: LP $BTC: `fcrv-renwbtc`, `fcrv-tbtc`, `fcrv-obtc`\n'
                                ':globe_with_meridians: `!contribute`: contribute to the community wiki\n'
                                ':chart_with_upwards_trend: improve me [on GitHub](https://github.com/brandoncurtis/harvest-discordbot)'
                    )
            await msg.channel.send(embed=embed)
        if '!bfarm' or '!bsc' in msg.content:
            farm_bsc = b3.eth.contract(address=FARM_ADDR_BSC, abi=TOKEN_ABI)
            farm_bsc_supply = farm_bsc.functions['totalSupply']().call()
            farm_bsc_supply_display = farm_bsc_supply*10**-18
            embed = discord.Embed(
                    title=':tractor: bFARM: FARM on BSC',
                    description=f':triangular_ruler: There is `{farm_bsc_supply_display:,.2f}` FARM on BSC\n'
                    f':map:  [{FARM_ADDR_BSC}](https://bscscan.com/address/{FARM_ADDR_BSC})\n'
                    f':bridge_at_night: Move FARM between ETH and BSC using the [Anyswap bridge](https://multichain.xyz)\n'
                    f':arrows_counterclockwise: Trade FARM on [Pancakeswap](https://exchange.pancakeswap.finance/#/swap?inputCurrency=0x4b5c23cac08a567ecf0c1ffca8372a45a5d33743)',
                    )
            await msg.channel.send(embed=embed)
        # information on the harvesting address
        if '!tractor' in msg.content:
            tractor_balance_eth_display = get_tractor_state()['eth']
            embed = discord.Embed(
                    title=':tractor: Status of Chad\'s Tractor',
                    description=f':map: tractor is parked at [{TRACTOR_ADDR}](https://etherscan.io/address/{TRACTOR_ADDR})\n'
                                f':fuelpump: fuel gauge: {tractor_balance_eth_display:.4f} ETH',
                    )
            await msg.channel.send(embed=embed)
        # information about how Harvest distributes incentives
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
            try:
                underlying = vault[1:]
                address, shareprice, vault_total, vault_buffer, vault_target, vault_strat, vault_strat_future, vault_strat_future_time = get_vaultstate(vault)
                vault_invested = vault_total - vault_buffer
                embed = discord.Embed(
                        title=f'{vault} Vault State :bank::mag:',
                        description=f':map: address: [{address}](https://etherscan.io/address/{address})\n'
                                f':moneybag: share price = {shareprice} {underlying}\n'
                                f':sponge: withdrawal buffer = {vault_buffer:,.4f} {underlying}\n'
                                f':bar_chart: invested = {vault_invested:,.4f} '
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
            except Exception as e:
                print(f'error: vault {vault}: {e}')
                embed = discord.Embed(
                        title=f'{vault} Vault State :bank::mag:',
                        description=f':bank: `!vault vaultname`: Harvest vault state of supported vaults\n'
                                ':lock: `f{coin}`, `funi-eth:{coin}`, `fsushi-eth:{coin}`\n'
                                ':dollar: LP $USD: `fcrv-ypool`, `fcrv-3pool`, `fcrv-comp`\n'
                                ':dollar: LP $USD: `fcrv-husd`, `fcrv-busd`, `fcrv-usdn`\n'
                                ':mountain: LP $BTC: `fcrv-renwbtc`, `fcrv-tbtc`, `fcrv-obtc`'
                                )
                await msg.channel.send(embed=embed)
        if '!profitshare' in msg.content:
            ps_address = vault_addr['profitshare']['addr']
            ps_deposits, ps_rewardperday, ps_rewardfinish, ps_stake_frac, ps_ifarm_deposits, ps_ifarm_pending = get_profitsharestate()
            ps_apr = 100* (ps_rewardperday / ps_deposits) * 365
            ps_timeleft = ( ps_rewardfinish - datetime.datetime.now() )
            embed = discord.Embed(
                    title=f':bank::mag: FARM Profit Sharing',
                    description=f':map: Profitshare address: [{ps_address}](https://etherscan.io/address/{ps_address})\n'
                                f':moneybag: Profitshare deposits: `{ps_deposits:,.2f}` FARM (`{100*ps_stake_frac:0.2f}%` of supply)\n'
                                f':bar_chart: Profitshare rewards per day: `{ps_rewardperday:,.2f}` FARM'
                                f' (`{ps_apr:.2f}%` instantaneous APR)\n'
                                f':alarm_clock: Current harvests pay out until: `{ps_rewardfinish} GMT`'
                                f' (`{ps_timeleft.total_seconds()/3600:.1f}` hours)\n'
                                f':bank: iFARM supply: `{ps_ifarm_deposits:,.2f}` (`{ps_ifarm_pending:,.2f}` pending)'
                    )
            await msg.channel.send(embed=embed)
        if '!uniswap' in msg.content:
            uni_addr, uni_deposit_farm, uni_deposit_eth, uni_farm_frac = get_uniswapstate()
            embed = discord.Embed(
                    title=f':mag: FARM:ETH Uniswap Pool',
                    description=f':bank: Uniswap contract: [{uni_addr}](https://etherscan.io/address/{uni_addr})\n'
                                f':moneybag: Liquidity: `{uni_deposit_farm:,.2f}` FARM (`{100*uni_farm_frac:.2f}%` of supply), `{uni_deposit_eth:,.2f}` ETH\n'
                                f':arrows_counterclockwise: [Trade FARM](https://app.uniswap.org/#/swap?outputCurrency=0xa0246c9032bc3a600820415ae600c6388619a14d), '
                                f'[Add Liquidity](https://app.uniswap.org/#/add/0xa0246c9032bC3A600820415aE600c6388619A14D/ETH), '
                                f'[Remove Liquidity](https://app.uniswap.org/#/remove/0xa0246c9032bC3A600820415aE600c6388619A14D/ETH)\n'
                                f':bar_chart: [FARM:ETH Uniswap chart](https://beta.dex.vision/?ticker=UniswapV2:FARMUSD-0x56feAccb7f750B997B36A68625C7C596F0B41A58&interval=15)'
                    )
            await msg.channel.send(embed=embed)
        if '!returns' in msg.content:
            try:
                vault = msg.content.split(' ')[-2].lower()
                amount_str = msg.content.split(' ')[-1]
                # get vault info
                delta_day, delta_week, delta_month, vault_delta_day, vault_delta_week, vault_delta_month = get_poolreturns(vault)
                bal = 0
                if amount_str[-1] == '%':
                    try:
                        vault_address, vault_shareprice, vault_total, vault_buffer, vault_target, vault_strat, vault_strat_future, vault_strat_future_time = get_vaultstate(vault)
                        bal = float(amount_str[:-1]) / 100 * vault_total
                    except:
                        pass
                else:
                    bal = float(amount_str)
                weekmsg = ''
                monthmsg = ''
                daymsg = f'\nIn the last day: `{vault_delta_day*100:.2f}%` plus `{bal*delta_day:.4f}` FARM'
                if delta_week > 0:
                    APYfromAPR_daily_week = 100 * ((1 + (vault_delta_week*100*52) / (100 * 365)) ** 365 - 1)
                    weekmsg = f'\nIn the last week: `{vault_delta_week*100:.2f}%` (~`{APYfromAPR_daily_week:.2f}%` APY) plus `{bal*delta_week:.4f}` FARM'
                if delta_month > 0:
                    APYfromAPR_daily_month = 100 * ((1 + (vault_delta_month*100*12) / (100 * 365)) ** 365 - 1)
                    monthmsg = f'\nIn the last month: `{vault_delta_month*100:.2f}%` (~`{APYfromAPR_daily_month:.2f}%` APY) plus `{bal*delta_month:.4f}` FARM'
                embed = discord.Embed(
                        title = f':tractor: Historical returns for a deposit of {bal:.4f} {vault}',
                        description = daymsg + weekmsg + monthmsg
                        )
                await msg.channel.send(embed=embed)
            except Exception as e:
                print(f'error: returns {vault}: {e}')
                embed = discord.Embed(
                        title=f':bank: `!returns vaultname #`: historical rewards to supported vaults\n',
                        description=':pencil: note: must include # of tokens to calculate returns on\n'
                                ':dollar: `f{dai,usdc,usdt,tusd}`, `fcrv-{ypool,3pool,comp,aave}`\n'
                                ':dollar: `f{bac,esd,dsd}`, `fcrv-{busd,gusd,husd,usdn,ust,eurs}`\n'
                                ':mountain: `f{wbtc,renbtc}`, `fcrv-{tbtc,hbtc,obtc,renwbtc}`\n'
                                ':chart_with_upwards_trend: `funi-{ust:maapl,mamzn:ust,mgoogl:ust,mtsla:ust}`\n'
                                ':lock: `funi-{eth:dpi,farm:eth,farm:grain}`\n'
                                )
                await msg.channel.send(embed=embed)
        if '!portfolio' in msg.content:
            address = msg.content.split(' ')[-1].lower()
            if w3.isAddress(address):
                portfolio = get_portfolio(address)
                # Discord has message length limits
                for i in range(0, len(portfolio), 25):
                    embed = discord.Embed(
                            title=f':bank: Portfolio for `{address}`\n',
                            description= f'Balances are listed in the underlying token. [Etherscan ↗](https://etherscan.io/address/{address})\n'
                                    + '```' + "\n".join(portfolio[i:i+25]) + '```'
                            )
                    await msg.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                        title=f':bank: Portfolio for `{address}`\n',
                        description=f'This is NOT a valid Ethereum address.\n'
                                f'Please provide a valid Ethereum address.\n'
                        )
                await msg.channel.send(embed=embed)

        if '!limit usdc' in msg.content:
            sell_farm_usdc_url = 'https://api.0x.org/sra/v3/orders?makerAssetData=0xf47261b0000000000000000000000000a0246c9032bc3a600820415ae600c6388619a14d&takerAssetData=0xf47261b0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
            res = requests.get(sell_farm_usdc_url)
            buy_orders = res.json()["records"]
            buy_desc = []
            for order in buy_orders:
                buy_amount = int(order["order"]["takerAssetAmount"])*10**-6
                buy_amount_remaining = int(order["metaData"]["remainingFillableTakerAssetAmount"])*10**-6
                sell_amount = int(order["order"]["makerAssetAmount"])*10**-18
                buy_price = sell_amount / buy_amount
                sell_price = buy_amount / sell_amount
                sell_amount_remaining = buy_price * buy_amount_remaining
                buy_desc.append(f'`{sell_price:07.2f}` USDC: `{sell_amount_remaining:.2f}` FARM')
            buy_desc.sort(reverse=True)
            embed = discord.Embed(
                    title=f':mag: FARM limit sell orders',
                    description='\n'.join(buy_desc)
                    )
            # send buys
            await msg.channel.send(embed=embed)
            buy_farm_usdc_url = 'https://api.0x.org/sra/v3/orders?takerAssetData=0xf47261b0000000000000000000000000a0246c9032bc3a600820415ae600c6388619a14d&makerAssetData=0xf47261b0000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
            res = requests.get(buy_farm_usdc_url)
            buy_orders = res.json()["records"]
            buy_desc = []
            for order in buy_orders:
                buy_amount = int(order["order"]["takerAssetAmount"])*10**-18
                buy_amount_remaining = int(order["metaData"]["remainingFillableTakerAssetAmount"])*10**-18
                sell_amount = int(order["makerAssetAmount"])*10**-6
                buy_price = sell_amount / buy_amount
                buy_desc.append(f'`{buy_price:07.2f}` USDC: `{buy_amount_remaining:.2f}` FARM')
            buy_desc.sort(reverse=True)
            embed = discord.Embed(
                    title=f':mag: FARM limit buy orders',
                    description='\n'.join(buy_desc)
                    )
            # send buys
            await msg.channel.send(embed=embed)

        if '!limit eth' in msg.content:
            sell_farm_eth_url = 'https://api.0x.org/sra/v3/orders?makerAssetData=0xf47261b0000000000000000000000000a0246c9032bc3a600820415ae600c6388619a14d&takerAssetData=0xf47261b0000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
            res = requests.get(sell_farm_eth_url)
            buy_orders = res.json()["records"]
            buy_desc = []
            for order in buy_orders:
                buy_amount = int(order["order"]["takerAssetAmount"])*10**-18 # ETH
                buy_amount_remaining = int(order["metaData"]["remainingFillableTakerAssetAmount"])*10**-18 # ETH
                sell_amount = int(order["order"]["makerAssetAmount"])*10**-18 # FARM
                buy_price = sell_amount / buy_amount
                sell_price = buy_amount / sell_amount
                sell_amount_remaining = buy_price * buy_amount_remaining
                buy_desc.append(f'`{sell_price:07.3f}` ETH: `{sell_amount_remaining:.2f}` FARM')
            buy_desc.sort(reverse=True)
            embed = discord.Embed(
                    title=f':mag: FARM limit sell orders',
                    description='\n'.join(buy_desc)
                    )
            # send buys
            await msg.channel.send(embed=embed)
            buy_farm_eth_url = 'https://api.0x.org/sra/v3/orders?takerAssetData=0xf47261b0000000000000000000000000a0246c9032bc3a600820415ae600c6388619a14d&makerAssetData=0xf47261b0000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
            res = requests.get(buy_farm_eth_url)
            buy_orders = res.json()["records"]
            buy_desc = []
            for order in buy_orders:
                buy_amount = int(order["order"]["takerAssetAmount"])*10**-18 # FARM
                buy_amount_remaining = int(order["metaData"]["remainingFillableTakerAssetAmount"])*10**-18 # FARM
                sell_amount = int(order["order"]["makerAssetAmount"])*10**-18 # ETH
                buy_price = sell_amount / buy_amount
                buy_desc.append(f'`{buy_price:07.3f}` ETH: `{buy_amount_remaining:.2f}` FARM')
            buy_desc.sort(reverse=True)
            embed = discord.Embed(
                    title=f':mag: FARM limit buy orders',
                    description='\n'.join(buy_desc)
                    )
            # send buys
            await msg.channel.send(embed=embed)

        if '!matic' in msg.content:
            matic_state = get_matic_state()
            mifarm_supply_display = matic_state['mifarm_supply']
            ifarm_supply_display = matic_state['ifarm_supply']
            farm_supply_display = matic_state['farm_supply']
            mifarm_addr = matic_state['mifarm_addr']
            matic_checkpoint_time = datetime.datetime.fromtimestamp(matic_state['last_checkpoint_time'])
            matic_checkpoint_delta = matic_checkpoint_time - datetime.datetime.now()
            embed = discord.Embed(
                    title=f':mag: Harvest on Matic',
                    description=f':rocket: There is `{mifarm_supply_display:,.2f}` iFARM on [Matic Mainnet]({EXPLORER_MATIC + "token/" + mifarm_addr})\n'
                                f':teacher: (`{100*mifarm_supply_display/ifarm_supply_display:,.2f}%` of `{ifarm_supply_display:,.2f}` iFARM;'
                                f' `{100*mifarm_supply_display/farm_supply_display:,.2f}%` of `{farm_supply_display:,.2f}` FARM)\n'
                                f':fox: [Configure Metamask](https://docs.matic.network/docs/develop/metamask/config-matic/)'
                                f' and use the [Matic Bridge](https://wallet.matic.network/bridge) to move iFARM to Matic\n'
                                f':arrows_counterclockwise: Trade iFARM on [Matic Quickswap](https://quickswap.exchange/#/swap?inputCurrency=0xab0b2ddb9c7e440fac8e140a89c0dbcbf2d7bbff)'
                                f' ([iFARM stats on Quickswap](https://info.quickswap.exchange/token/0xab0b2ddb9c7e440fac8e140a89c0dbcbf2d7bbff))\n'
                                f':alarm_clock: last [checkpoint](https://etherscan.io/address/0x86e4dc95c7fbdbf52e33d563bbdb00823894c287) on Ethereum: `{matic_checkpoint_time}` GMT'
                                f' (`{-1*matic_checkpoint_delta.total_seconds()/3600:.1f}` hours ago)'
                    )
            await msg.channel.send(embed=embed)


def get_matic_state():
    state = {}
    mifarm_addr = '0xab0b2ddB9C7e440fAc8E140A89c0dbCBf2d7Bbff'
    mifarm_contract = m3.eth.contract(address=mifarm_addr, abi=TOKEN_ABI)
    mifarm_supply = mifarm_contract.functions['totalSupply']().call()*10**-18
    ifarm_addr = vault_addr['ifarm']['addr']
    ifarm_contract = w3.eth.contract(address=ifarm_addr, abi=TOKEN_ABI)
    ifarm_supply = ifarm_contract.functions['totalSupply']().call()*10**-18
    farm_addr = FARM_ADDR
    farm_contract = w3.eth.contract(address=farm_addr, abi=TOKEN_ABI)
    farm_supply = farm_contract.functions['totalSupply']().call()*10**-18
    # last checkpoint
    rootchain_contract = w3.eth.contract(address=ROOTCHAIN_ADDR, abi=ROOTCHAIN_ABI)
    state['last_checkpoint_block'] = rootchain_contract.functions['currentHeaderBlock']().call()
    state['last_checkpoint_time'] = rootchain_contract.functions['headerBlocks'](state['last_checkpoint_block']).call()[3]
    # save some info to send back
    state['mifarm_addr'] = mifarm_addr
    state['mifarm_supply'] = mifarm_supply
    state['ifarm_addr'] = ifarm_addr
    state['ifarm_supply'] = ifarm_supply
    state['farm_addr'] = farm_addr
    state['farm_supply'] = farm_supply
    return state

def get_portfolio(address):
    addr = w3.toChecksumAddress(address)
    portfolio = []
    # pending rewards
    rewards_claimable = 0
    
    # free FARM
    reward_token = w3.eth.contract(address=FARM_ADDR, abi=TOKEN_ABI)
    wallet_balance_display = reward_token.functions['balanceOf'](addr).call()*10**-18
    if wallet_balance_display > 0:
        balance_decimals = max(-1 * math.floor(math.log10(wallet_balance_display)) + 3, 2)
        msg = f'{"wallet FARM:":16}: {wallet_balance_display:,.{balance_decimals}f}'
        portfolio.append(msg)
    # iFARM
    ifarm_address = '0x1571eD0bed4D987fe2b498DdBaE7DFA19519F651'
    ifarm_contract = w3.eth.contract(address=ifarm_address, abi=TOKEN_ABI)
    ifarm_balance_display = ifarm_contract.functions['balanceOf'](addr).call()*10**-18
    if ifarm_balance_display > 0:
        balance_decimals = max(-1 * math.floor(math.log10(ifarm_balance_display)) + 3, 2)
        msg = f'{"wallet iFARM":16}: {ifarm_balance_display:,.{balance_decimals}f}'
        portfolio.append(msg)
    # matic iFARM
    mifarm_address = '0xab0b2ddB9C7e440fAc8E140A89c0dbCBf2d7Bbff'
    mifarm_contract = m3.eth.contract(address=mifarm_address, abi=TOKEN_ABI)
    mifarm_balance_display = mifarm_contract.functions['balanceOf'](addr).call()*10**-18
    if mifarm_balance_display > 0:
        balance_decimals = max(-1 * math.floor(math.log10(mifarm_balance_display)) + 3, 2)
        msg = f'{"Matic iFARM":16}: {mifarm_balance_display:,.{balance_decimals}f}'
        portfolio.append(msg)
    # profitshare
    ps_address = vault_addr['profitshare']['pool']
    ps_contract = w3.eth.contract(address=ps_address, abi=PS_ABI)
    ps_balance_display = ps_contract.functions['balanceOf'](addr).call()*10**-18
    if ps_balance_display > 0:
        balance_decimals = max(-1 * math.floor(math.log10(ps_balance_display)) + 3, 2)
        msg = f'{"profitshare":16}: {ps_balance_display:,.{balance_decimals}f}'
        portfolio.append(msg)
    # vaults
    for vault in vaults:
        msg = ''
        try:
            vault_address = vault
            vault_name = vaults[vault]['asset'].lower()
            vault_rewards_address = vault_addr[vault_name]['pool']
            #print(vault_name, vault_address, vault_rewards_address)
            vault_contract = w3.eth.contract(address=vault_address, abi=VAULT_ABI)
            pool_contract = w3.eth.contract(address=vault_rewards_address, abi=POOL_ABI)
            wallet_balance = vault_contract.functions['balanceOf'](addr).call()
            rewards_balance = 0
            if vault_rewards_address is not '':
                rewards_balance = pool_contract.functions['balanceOf'](addr).call()
            if rewards_balance > 0 or wallet_balance > 0:
                lptype = vaults[vault]['lptype']
                vault_shareprice = vault_contract.functions['getPricePerFullShare']().call()
                token_decimals = vault_contract.functions['decimals']().call()
                rewards_balance_display = rewards_balance * vault_shareprice * 10**(-1*token_decimals*2)
                balance_decimals = max(-1 * math.floor(math.log10(rewards_balance_display)) + 3, 2)
                msg += f'{vault_name:16}: {rewards_balance_display:,.{balance_decimals}f}'
                # earned rewards
                if vault_rewards_address is not '':
                    rewards_claimable += pool_contract.functions['earned'](addr).call()*10**-18
                if wallet_balance > 0:
                    wallet_balance_display = wallet_balance * vault_shareprice * 10**(-1*token_decimals*2)
                    balance_decimals = max(-1 * math.floor(math.log10(wallet_balance)) + 3, 2)
                    msg += f' (+ {wallet_balance_display:,.{balance_decimals}f} unstaked)'
                if lptype == 'uniswap' or lptype == '1inch':
                    underlying_address = vault_contract.functions['underlying']().call()
                    # shared logic for Uniswap derivs and 1inch
                    if lptype == 'uniswap':
                        underlying_contract = w3.eth.contract(address=underlying_address, abi=UNIPOOL_ABI)
                        token0_address = underlying_contract.functions['token0']().call()
                        token1_address = underlying_contract.functions['token1']().call()
                        underlying_token0_supply, underlying_token1_supply, ts_updated = underlying_contract.functions['getReserves']().call()
                        token0_contract = w3.eth.contract(address=token0_address, abi=TOKEN_ABI)
                        token1_contract = w3.eth.contract(address=token1_address, abi=TOKEN_ABI)
                        token0_symbol = token0_contract.functions['symbol']().call()
                        token1_symbol = token1_contract.functions['symbol']().call()
                        token0_decimals = token0_contract.functions['decimals']().call()
                        token1_decimals = token1_contract.functions['decimals']().call()
                    if lptype == '1inch':
                        underlying_contract = w3.eth.contract(address=underlying_address, abi=MOONISWAP_ABI)
                        token0_address = underlying_contract.functions['token0']().call()
                        token1_address = underlying_contract.functions['token1']().call()
                        underlying_token0_supply = underlying_contract.functions['getBalanceForRemoval'](token0_address).call()
                        underlying_token1_supply = underlying_contract.functions['getBalanceForRemoval'](token1_address).call()
                        if token0_address == ZERO_ADDRESS:
                            token0_symbol = 'ETH'
                            token0_decimals = 18
                        else:
                            token0_contract = w3.eth.contract(address=token0_address, abi=TOKEN_ABI)
                            token0_symbol = token0_contract.functions['symbol']().call()
                            token0_decimals = token0_contract.functions['decimals']().call()
                        if token1_address == ZERO_ADDRESS:
                            token1_symbol = 'ETH'
                            token1_decimals = 18
                        else:
                            token1_contract = w3.eth.contract(address=token1_address, abi=TOKEN_ABI)
                            token1_symbol = token1_contract.functions['symbol']().call()
                            token1_decimals = token1_contract.functions['decimals']().call()
                    # shared logic for Uniswap derivs and 1inch
                    underlying_supply = underlying_contract.functions['totalSupply']().call()
                    underlying_decimals = underlying_contract.functions['decimals']().call()
                    token0_per_underlying = underlying_token0_supply / underlying_supply
                    token1_per_underlying = underlying_token1_supply / underlying_supply
                    token0_balance = token0_per_underlying * (wallet_balance + rewards_balance)
                    token1_balance = token1_per_underlying * (wallet_balance + rewards_balance)
                    token0_balance_display = token0_balance * 10**(-1*token0_decimals)
                    token1_balance_display = token1_balance * 10**(-1*token1_decimals)
                    msg += f'\n - - - - - - - -: = {token0_balance_display:,.2f} {token0_symbol} + {token1_balance_display:,.2f} {token1_symbol}'
            if msg != '':
                portfolio.append(msg)
        except Exception as e:
            print(e)
    if rewards_claimable > 0:
        msg = f'FARM claimable  : {rewards_claimable:,.2f}'
        portfolio.append(msg)
    if portfolio == []:
        portfolio.append('Portfolio has no vault deposits.')
    return portfolio

def get_value_usd(token, amt):
    url = 'https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={token}&vs_currencies=USD'
    res = requests.get(url)
    print(token, amt, res)

def get_tractor_state():
    tractor_balance_eth_display = w3.eth.get_balance(TRACTOR_ADDR)*10**-18
    return {'eth': tractor_balance_eth_display}


def get_twap():
    #BLOCKS_PER_DAY = int((60/12)*60*24) # 7200 at 12 sec;
    # calculate the twap
    pool_contract = w3.eth.contract(address=ASSETS['FARM']['pools']['USDC']['addr'], abi=UNIPOOL_ABI)
    blocknum_t0 = w3.eth.blockNumber - BLOCKS_PER_DAY
    time_t1  = pool_contract.functions['getReserves']().call()[-1]
    time_t0 = pool_contract.functions['getReserves']().call(block_identifier = blocknum_t0)[-1]
    price_t1 = pool_contract.functions['price0CumulativeLast']().call()
    price_t0 = pool_contract.functions['price0CumulativeLast']().call(block_identifier = blocknum_t0)
    elapsed_seconds = time_t1 - time_t0
    twap = ( int( (10 ** 24) * (price_t1 - price_t0) / elapsed_seconds) >> 112 ) * (10 ** -12)
    print(f'TWAP since last checkpoint is: ${twap:0.4f}')
    return twap


def get_poolreturns(vault):
    blocknum = w3.eth.blockNumber
    if vault == 'profitshare':
        ps_pool_addr = vault_addr['profitshare']['pool']
        ps_contract = w3.eth.contract(address=ps_pool_addr, abi=PS_ABI)
        ps_current = ps_contract.functions['balanceOf'](MODEL_ADDR).call()
        try:
            ps_day = ps_contract.functions['balanceOf'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY)
            ps_delta_day = (ps_current - ps_day) / (ps_day)
        except:
            ps_delta_day = 0
        try:
            ps_week = ps_contract.functions['balanceOf'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY*7)
            ps_delta_week = (ps_current - ps_week) / (ps_week)
        except:
            ps_delta_week = 0
        try:
            ps_month = ps_contract.functions['balanceOf'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY*30)
            ps_delta_month = (ps_current - ps_month) / (ps_month)
        except:
            ps_delta_month = 0
        return ps_delta_day, ps_delta_week, ps_delta_month, 0, 0, 0
    vault_address = get_vaultaddress(vault)
    vault_contract = w3.eth.contract(address=vault_address, abi=VAULT_ABI)
    try:
        vault_decimals = int(vault_contract.functions['decimals']().call())
    except:
        vault_decimals = 18
    pool_addr = get_pooladdress(vault)
    pool_contract = w3.eth.contract(address=pool_addr, abi=POOL_ABI)
    reward_current = pool_contract.functions['earned'](MODEL_ADDR).call()
    vault_current = vault_contract.functions['getPricePerFullShare']().call()
    try:
        # FARM rewards
        reward_day = pool_contract.functions['earned'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY)
        balance_day = pool_contract.functions['balanceOf'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY)
        delta_day = ((10**-18) / (10**(-1*vault_decimals))) * (reward_current - reward_day) / balance_day
        # vault return
        vault_day = vault_contract.functions['getPricePerFullShare']().call(block_identifier=blocknum-BLOCKS_PER_DAY)
        vault_delta_day = (vault_current - vault_day) / vault_day
    except:
        delta_day = 0
        vault_delta_day = 0
    try:
        reward_week = pool_contract.functions['earned'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY*7)
        balance_week = pool_contract.functions['balanceOf'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY*7)
        delta_week = ((10**-18) / (10**(-1*vault_decimals))) * (reward_current - reward_week) / balance_week
        # vault return
        vault_week = vault_contract.functions['getPricePerFullShare']().call(block_identifier=blocknum-BLOCKS_PER_DAY*7)
        vault_delta_week = (vault_current - vault_week) / vault_week
    except:
        delta_week= 0
        vault_delta_week = 0
    try:
        reward_month = pool_contract.functions['earned'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY*30)
        balance_month = pool_contract.functions['balanceOf'](MODEL_ADDR).call(block_identifier=blocknum-BLOCKS_PER_DAY*30)
        delta_month = ((10**-18) / (10**(-1*vault_decimals))) * (reward_current - reward_month) / balance_month
        # vault return
        vault_month = vault_contract.functions['getPricePerFullShare']().call(block_identifier=blocknum-BLOCKS_PER_DAY*30)
        vault_delta_month = (vault_current - vault_month) / vault_month
    except:
        delta_month= 0
        vault_delta_month = 0
    return delta_day, delta_week, delta_month, vault_delta_day, vault_delta_week, vault_delta_month

def get_uniswapstate():
    uni_addr = ASSETS['FARM']['pools']['ETH']['addr']
    pool_contract = w3.eth.contract(address=uni_addr, abi=UNIPOOL_ABI)
    poolvals = pool_contract.functions['getReserves']().call()
    uni_deposit_farm = poolvals[0]*10**-18
    uni_deposit_eth = poolvals[1]*10**-18
    farm_contract = w3.eth.contract(address=FARM_ADDR, abi=VAULT_ABI)
    farm_totalsupply = farm_contract.functions['totalSupply']().call()*10**-18
    uni_farm_frac = uni_deposit_farm / farm_totalsupply
    return (uni_addr, uni_deposit_farm, uni_deposit_eth, uni_farm_frac)


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
    # iFARM stuff
    ifarm_addr = vault_addr['ifarm']['addr']
    ifarm_contract = w3.eth.contract(address=ifarm_addr, abi=VAULT_ABI)
    ifarm_balance = lp_contract.functions['balanceOf'](ifarm_addr).call()*10**(-1*ps_decimals)
    ifarm_supply = ifarm_contract.functions['totalSupply']().call()*10**(-1*ps_decimals)
    return (ps_totalsupply, ps_rewardperday, ps_rewardfinishdt, ps_stake_frac, ifarm_supply, ifarm_balance)

def get_vaultaddress(vault):
    vault_address = None
    if vault in vault_addr:
        vault_address = vault_addr[vault]['addr']
    else:
        print(f'vaultstate: {vault} not in vault_addr list')
        print(f'vaultstate: {vault} split into {re.split("-|:| ", vault)}')
        vault_prefix, vault_asset0, vault_asset1, *vault_postfix = re.split('-|:| ', vault)
        if len(vault_postfix) == 0:
            vault_name = f'{vault_prefix}-{vault_asset0}:{vault_asset1}'
            vault_name_rev = f'{vault_prefix}-{vault_asset1}:{vault_asset0}'
            if vault_name in vault_addr:
                vault_address = vault_addr[vault_name]['addr']
            else:
                vault_address = vault_addr[vault_name_rev]['addr']
        else:
            vault_name = f'{vault_prefix}-{vault_asset0}:{vault_asset1}-{vault_postfix[0]}'
            vault_name_rev = f'{vault_prefix}-{vault_asset1}:{vault_asset0}-{vault_postfix[0]}'
            if vault_name in vault_addr:
                vault_address = vault_addr[vault_name]['addr']
            else:
                vault_address = vault_addr[vault_name_rev]['addr']
    print(f'get_vaultaddress: {vault_address}')
    return vault_address

def get_pooladdress(vault):
    pool_address = None
    if vault in vault_addr:
        pool_address = vault_addr[vault]['pool']
    else:
        print(f'vaultstate: {vault} not in vault_addr list')
        print(f'vaultstate: {vault} split into {re.split("-|:| ", vault)}')
        vault_prefix, vault_asset0, vault_asset1, *vault_postfix = re.split('-|:| ', vault)
        if len(vault_postfix) == 0:
            vault_name = f'{vault_prefix}-{vault_asset0}:{vault_asset1}'
            vault_name_rev = f'{vault_prefix}-{vault_asset1}:{vault_asset0}'
            if vault_name in vault_addr:
                pool_address = vault_addr[vault_name]['pool']
            else:
                pool_address = vault_addr[vault_name_rev]['pool']
        else:
            vault_name = f'{vault_prefix}-{vault_asset0}:{vault_asset1}-{vault_postfix[0]}'
            vault_name_rev = f'{vault_prefix}-{vault_asset1}:{vault_asset0}-{vault_postfix[0]}'
            if vault_name in vault_addr:
                pool_address = vault_addr[vault_name]['pool']
            else:
                pool_address = vault_addr[vault_name_rev]['pool']
    print(f'get_pooladdress: {pool_address}')
    return pool_address

def get_vaultstate(vault):
    # try different orderings of the assets
    vault_address = get_vaultaddress(vault)
    if vault_address is None:
        return None
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
    print(f'starting discord bot...')
    client.run(DISCORD_BOT_TOKEN)
    print(f'discord bot started')

if __name__ == '__main__':
    main()

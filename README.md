# harvest-discordbot

## Objective

Provide a simple Discord bot that can (eventually) be adapted to provide prices and utlity commands for a wide range of Ethereum projects.

A defining feature is the **lack of external dependencies**. PRs are accepted, but don't propose anything that adds dependencies on Etherscan, TheGraph, Coingecko, or any other 3rd party APIs. Even if the API is provided by an open source backend, these PRs will be closed.

## Ethereum Nodes

Several functions in this bot require an Ethereum archive node.  This will NOT work with a free Infura account.

Archive nodes are $700 per month from Infura, or can be synced from scratch in 1-3 months on bare metal.  Archive nodes require several terabytes of high-performance storage and are quite expensive to run in the cloud.

This has not been tested, but you can also try to sign up for an account on https://archivenode.io/.

## Deployment

Master is autodeployed to a Digital Ocean instance managed by @brandoncurtis.

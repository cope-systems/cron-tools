# Cron Tools
[![Build Status](https://travis-ci.org/cope-systems/cron-tools.svg?branch=initial-buildout)](https://travis-ci.org/cope-systems/cron-tools)
## What and Why
cron-tools provides a system to overlay on top of the traditional "cron" daemon to provide additional tracking and
control of periodically (and possibly single shot) run scripts and programs.

## Prior Art


## Architecture
cron-tools is broken down into three components: the wrapper, the agent, and the aggregator. The wrapper is the 
actual tooling that is used to "wrap" (by being the parent to whatever actually needs to be executed) the target
program or script. It is used to monitor and collect information about the execution target. The wrapper communicates
the results to the agent, which should be running on the given system.

 The agent is a long running daemon which accepts results over a unix domain socket and stores them locally in a spool.
The agent at some point later will attempt to upload the results to the aggregator. The agent uses SQLite3 as its 
backing store, and is designed so that even in the event of network failures, job results can be forwarded at some
later date.

 The aggregator is a results aggregator and web front end that the agents forward to. The end users utilize the web 
front end of the aggregator to view results. The aggregator is powered by a PostgreSQL database. 

## Technical Details

 cron-tools is written entirely in Python, and should support Python 2.7+ and Python 3.4+.
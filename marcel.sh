#!/bin/env bash
# functions and aliases

# resets the app
function resetapp () {
    python -c "import marcel;print marcel.reset() is None"
}

# starts a redis-cli session on epio-hosted instance
function epio-redis () {
    epio run_command python -a marcel -- -c "\"from bundle_config import config;from subprocess import call;r=config['redis'];call(['redis-cli','-h',r['host'],'-p',r['port'],'-a',r['password']])\""
}

# activate virtualenv and chdir
workon marcel
cd ~/projects/marcel

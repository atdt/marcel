function resetapp () {
    python -c "import marcel;print marcel.add_dummy_data() is None"
}

function epio-redis () {
    epio run_command python -- -c "\"from bundle_config import config;from subprocess import call;r=config['redis'];call(['redis-cli','-h',r['host'],'-p',r['port'],'-a',r['password']])\""
}

workon marcel

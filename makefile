MAKE:
	grunt

	scp static/bin/zb.action.min.js zba@zba:/var/www/zba/zb.action.min.js
	scp -r *.py zba@zba:/var/www/zba/.
	scp ../secrets.json zba@zba:/var/www/secrets.json

	ssh zba@zba "sudo killall -s SIGKILL python && python /var/www/zba/zb_sync.py &"
MAKE:
	grunt

	ssh zba@zba "mkdir -p /var/www/zba/static/js && mkdir -p /var/www/zba/static/css"

	scp static/bin/zb.action.min.js zba@zba:/var/www/zba/static/zb.action.min.js

	scp -r *.py zba@zba:/var/www/zba/.

	scp -r static/css/*.css zba@zba:/var/www/zba/static/css/.
	scp -r templates/*.html zba@zba:/var/www/zba/templates/.
	scp -r static/js/*.js zba@zba:/var/www/zba/static/js/.

	scp ../secrets.json zba@zba:/var/www/secrets.json

	ssh -f zba@zba "killall -s SIGKILL python; python /var/www/zba/zb_sync.py &> output"
MAKE: local copy deploy

local:
	grunt
	rm -r .sass-cache

copy:
	scp static/bin/zb.action.min.js zba@zba:/var/www/zba/static/bin/zb.action.min.js

	scp -r *.py zba@zba:/var/www/zba/.

	scp -r static/css/*.css zba@zba:/var/www/zba/static/css/.
	scp -r templates/*.html zba@zba:/var/www/zba/templates/.
	scp -r static/js/*.js zba@zba:/var/www/zba/static/js/.

	scp /zba/secrets.json zba@zba:/zba/secrets.json

deploy:
	ssh -f zba@zba "killall -s SIGKILL python; python /var/www/zba/zb_sync.py &> output"
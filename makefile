MAKE: local copy deploy

local:
	grunt

copy:
	ssh zba@zba " \
		mkdir -p /var/www/zba/static/bin; \
		mkdir -p /var/www/zba/static/css; \
		mkdir -p /var/www/zba/static/js; \
		mkdir -p /var/www/zba/static/fonts; \
		mkdir -p /var/www/zba/static/bin \
		mkdir -p /zba; \
		\
		chmod -R 777 /zba; \
		chmod -R 777 /var/www/zba; \
	"

	scp *.py zba@zba:/var/www/zba/.
	scp -r modules zba@zba:/var/www/zba/
	scp -r models zba@zba:/var/www/zba/

	scp -r static/css/*.css zba@zba:/var/www/zba/static/css/.
	scp -r static/fonts/* zba@zba:/var/www/zba/static/fonts
	scp -r templates zba@zba:/var/www/zba
	scp -r static/js/*.js zba@zba:/var/www/zba/static/js/.
	scp -r static/bin zba@zba:/var/www/zba/static/bin

	scp -r example zba@zba:/var/www/zba/

	# scp /zba/secrets.json zba@zba:/zba/secrets.json

deploy:
	ssh -f zba@zba "killall -s SIGKILL python; python /var/www/zba/zb_sync.py &>> socket_output; restart zba"

clean:
	grunt clean

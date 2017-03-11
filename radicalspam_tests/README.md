# RadicalSpam Tests


## Installation

	docker exec -it radicalspam bash
	pip3 install virtualenv
	virtualenv ./myenv
	source myenv/bin/activate
	pip install -r radicalspam_tests/requirements.txt
	python -m radicalspam_tests.radicalspam
	
	apt-get install --no-install-recommends python3-pip
	pip3 install -U pip virtualenv
	virtualenv ./myenv
	source myenv/bin/activate
	pip install -r radicalspam_tests/requirements.txt
	
	python -m radicalspam_tests.radicalspam
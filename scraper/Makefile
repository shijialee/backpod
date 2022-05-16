SHELL=/usr/bin/bash

.PHONY: sync.real
sync.real:
	rsync -cvrlOD -e 'ssh' . het_dev:~/play/backpod


.PHONY: sync.dry
sync.dry:
	rsync -cvrlOD -n -e 'ssh' . het_dev:~/play/backpod

.PHONY: run.cli
run.cli:
	source venv/bin/activate && STATIC_ROOT=/tmp  python3 -m backpod.cli

.PHONY: run.flask_dev
run.flask_dev:
	source venv/bin/activate && FLASK_APP=form flask run

.PHONY: run
run:
    source venv/bin/activate && python3 -m backpod.cli https://www.npr.org/rss/podcast.php?id=510289 >> money.xml


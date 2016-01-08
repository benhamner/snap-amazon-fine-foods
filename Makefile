input/Reviews.txt:
	mkdir -p input
	curl http://snap.stanford.edu/data/finefoods.txt.gz -o input/Reviews.txt.gz
	gzip -d input/Reviews.txt.gz
input: input/Reviews.txt

output/Reviews.csv: input/Reviews.txt
	mkdir -p working
	mkdir -p output
	python src/process.py
csv: output/Reviews.csv

working/noHeader/Reviews.csv: output/Reviews.csv
	mkdir -p working/noHeader
	tail +2 $^ > $@

output/database.sqlite: working/noHeader/Reviews.csv
	-rm output/database.sqlite
	sqlite3 -echo $@ < working/import.sql
db: output/database.sqlite

output/hashes.txt: output/database.sqlite
	-rm output/hashes.txt
	echo "Current git commit:" >> output/hashes.txt
	git rev-parse HEAD >> output/hashes.txt
	echo "\nCurrent input/ouput md5 hashes:" >> output/hashes.txt
	md5 output/*.csv >> output/hashes.txt
	md5 output/*.sqlite >> output/hashes.txt
	md5 input/*.csv >> output/hashes.txt
hashes: output/hashes.txt

release: output/database.sqlite output/hashes.txt
	cp -r output amazon-fine-foods
	zip -r -X output/amazon-fine-foods-release-`date -u +'%Y-%m-%d-%H-%M-%S'` amazon-fine-foods/*
	rm -rf amazon-fine-foods

all: csv db hashes release

clean:
	rm -rf working
	rm -rf output

python induct/induct.py data/string2geo.test.5BEST left nosplit ./grammar.irtg ./llmtrain.txt

python induct/prepareLogLinModel.py grammar.irtg > grammar.llm.irtg

java -jar bin/alto-2.0-SNAPSHOT-2015-07-21.jar -Xmx4G


ALTO=./bin/alto-1.1-SNAPSHOT-jar-with-dependencies.jar
GOLD=corpus.gold

grammar=$1
parse=$2

echo "== Evaluating result for "
#python extract/parsedToLisp.py $parse > $parse.tolisp
java -cp $ALTO:generate ConvertToLisp $grammar $parse > $parse.lisp
python extract/lispToEvalb.py $parse.lisp > $parse.eval
./EVALB/evalb -p sample.prm $GOLD $parse.eval > $parse.results
python extract/extractResults.py $parse.results ./

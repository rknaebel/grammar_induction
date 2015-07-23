ALIGNMENT=alignment-5best

export JAVA_HOME=/cl-tools/jdk1.8.0_05/
export PATH=$JAVA_HOME/bin:$PATH
export PATH=/cl-tools/scala-2.11.7/bin/:$PATH 

GDIR=./generate
EVAL=./evaluate
RESULTS=./$GDIR/results.csv

SCALA="scala -J-Xmx16G"
JAVA=java
JAVAC=javac
PY=python
ALTO=bin/alto-1.1-SNAPSHOT-jar-with-dependencies.jar

if [ -d $GDIR ]
then
    rm -R $GDIR
fi
mkdir ./$GDIR

touch $RESULTS

$JAVAC -cp $ALTO -d $GDIR  extract/ConvertToLisp.java

for fold in 0 # 1 2 3 4 5 6 7 8 9
do
    echo "==> Start of fold ${fold}"
    mkdir $GDIR/${fold}
    
    echo "-- Generate grammar 1 left  nosplit"
    $PY induct/induct.py $EVAL/${fold}/${ALIGNMENT}.${fold} left  nosplit   $GDIR/${fold}/grammar1.irtg $GDIR/${fold}/llmtrain1.txt 
    echo "-- Generate grammar 2 right nosplit"
    $PY induct/induct.py $EVAL/${fold}/${ALIGNMENT}.${fold} right nosplit   $GDIR/${fold}/grammar2.irtg $GDIR/${fold}/llmtrain2.txt &
    echo "-- Generate grammar 3 both  nosplit"
    $PY induct/induct.py $EVAL/${fold}/${ALIGNMENT}.${fold} both  nosplit   $GDIR/${fold}/grammar3.irtg $GDIR/${fold}/llmtrain3.txt &
    echo "-- Generate grammar 4 left  semsplit"
    $PY induct/induct.py $EVAL/${fold}/${ALIGNMENT}.${fold} left  semsplit  $GDIR/${fold}/grammar4.irtg /dev/null &
    echo "-- Generate grammar 5 right semsplit"
    $PY induct/induct.py $EVAL/${fold}/${ALIGNMENT}.${fold} right semsplit  $GDIR/${fold}/grammar5.irtg /dev/null &
    echo "-- Generate grammar 6 both  semsplit"
    $PY induct/induct.py $EVAL/${fold}/${ALIGNMENT}.${fold} both  semsplit  $GDIR/${fold}/grammar6.irtg /dev/null &
    
    for i in 1 2 3 4 5 6
    do
        echo "-- Generate weighted grammar ${i} + bulk parsing"
        $SCALA  -cp $ALTO RunAll.scala \
                $GDIR/${fold}/grammar${i}.irtg \
                $EVAL/${fold}/emtraining.${fold} \
                $GDIR/${fold}/grammar${i}_em.irtg \
                $EVAL/${fold}/teststring.${fold} \
                $GDIR/${fold}/parsed${i}_em.txt
        
        echo "== Evaluating result for em grammar ${i}"
        $PY extract/parsedToLisp.py $GDIR/${fold}/parsed${i}_em.txt > $GDIR/${fold}/parsed${i}_em.tolisp
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/grammar${i}_em.irtg     $GDIR/${fold}/parsed${i}_em.tolisp > $GDIR/${fold}/parsed${i}_em.lisp
        $PY extract/lispToEvalb.py $GDIR/${fold}/parsed${i}_em.lisp > $GDIR/${fold}/parsed${i}_em.eval
        ./bin/evalb -p bin/EVALB/sample/sample.prm $EVAL/${fold}/testfunql.${fold} $GDIR/${fold}/parsed${i}_em.eval > $GDIR/${fold}/parsed${i}_em.results
        $PY extract/extractResults.py $GDIR/${fold}/parsed${i}_em.results $RESULTS
    done

    for i in 1 2 3
    do
        echo "-- Generate loglinear grammar ${i}"
        $PY induct/prepareLogLinModel.py $GDIR/${fold}/grammar${i}.irtg > $GDIR/${fold}/grammar${i}_llm.irtg
        echo "-- Generate features weights for grammar ${i} + bulk parsing"
        $SCALA -cp $ALTO RunLogLin.scala \
                $GDIR/${fold}/grammar${i}_llm.irtg \
                $GDIR/${fold}/llmtrain${i}.txt \
                $GDIR/${fold}/grammar${i}_features.irtg \
                $EVAL/${fold}/teststring.${fold} \
                $GDIR/${fold}/parsed${i}_llm.txt

        echo "-- Generate lisp format for llm parse ${i}"
        $JAVA -cp $GDIR/:$ALTO ConvertToLisp $GDIR/${fold}/grammar${i}.irtg $GDIR/${fold}/parsed${i}_llm.txt > $GDIR/${fold}/parsed${i}_llm.lisp.txt
        
        echo "== Evaluating result for llm grammar ${i}"
        $PY extract/parsedToLisp.py $GDIR/${fold}/parsed${i}_llm.txt > $GDIR/${fold}/parsed${i}_llm.tolisp
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/grammar${i}_llm.irtg $GDIR/${fold}/parsed${i}_llm.tolisp > $GDIR/${fold}/parsed${i}_llm.lisp
        $PY extract/lispToEvalb.py $GDIR/${fold}/parsed${i}_llm.lisp > $GDIR/${fold}/parsed${i}_llm.eval
        ./bin/evalb -p bin/EVALB/sample/sample.prm $EVAL/${fold}/testfunql.${fold} $GDIR/${fold}/parsed${i}_llm.eval > $GDIR/${fold}/parsed${i}_llm.results
        $PY extract/extractResults.py $GDIR/${fold}/parsed${i}_llm.results $RESULTS
    done

    for i in 2 3 4 #5 6 7 8 9 10
    do
        echo "-- Generate grammar with ${i} splits"
        $PY induct/splitGrammar.py $GDIR/${fold}/grammar3_em.irtg ${i} > $GDIR/${fold}/grammar3_split${i}.irtg
    done

    for i in 2 3 4 #5 6 7 8 9 10
    do
        echo "-- Reweight EM grammar with ${i} splits + bulk parsing"
        $SCALA -cp $ALTO RunAll.scala \
                $GDIR/${fold}/grammar3_split${i}.irtg \
                $EVAL/${fold}/emtraining.${fold} \
                $GDIR/${fold}/grammar3_split${i}_em.irtg \
                $EVAL/${fold}/teststring.${fold} \
                $GDIR/${fold}/parsed3_split${i}.txt
        echo "-- Generate lisp format for parse ${i}"
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/grammar3_split${i}_em.irtg $GDIR/${fold}/parsed3_split${i}.txt > $GDIR/${fold}/parsed3_split${i}.lisp.txt
        
        echo "== Evaluating result for splitted grammar ${i}"
        $PY extract/parsedToLisp.py $GDIR/${fold}/parsed3_split${i}.txt > $GDIR/${fold}/parsed3_split${i}.tolisp
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/parsed3_split${i}.irtg $GDIR/${fold}/parsed3_split${i}.tolisp > $GDIR/${fold}/parsed3_split${i}.lisp
        $PY extract/lispToEvalb.py $GDIR/${fold}/parsed3_split${i}.lisp > $GDIR/${fold}/parsed3_split${i}.eval
        ./bin/evalb -p bin/EVALB/sample/sample.prm $EVAL/${fold}/testfunql.${fold} $GDIR/${fold}/parsed3_split${i}.eval > $GDIR/${fold}/parsed3_split${i}.results
        $PY extract/extractResults.py $GDIR/${fold}/parsed3_split${i}.results $RESULTS   
    done
    
done





ALIGNMENT=data/string2geo.A3.final5BEST

export JAVA_HOME=/cl-tools/jdk1.8.0_05/
export PATH=$JAVA_HOME/bin:$PATH
export PATH=/cl-tools/scala-2.11.7/bin/:$PATH 

GDIR=./generate
EVAL=./evaluate
SCALA=scala
JAVA=java
JAVAC=javac
PY=python
ALTO=bin/alto-1.1-SNAPSHOT-jar-with-dependencies.jar

if [ -d $GDIR ]
then
    rm -R $GDIR
fi
mkdir ./$GDIR

$JAVAC -cp $ALTO -d $GDIR  extract/ConvertToLisp.java

for fold in 0 1 2 3 4 5 6 7 8 9
do
    echo "==> Start of fold ${fold}"
    
    echo "-- Generate grammar 1 left  nosplit"
    $PY induct/induct.py $ALIGNMENT left  nosplit   $GDIR/$fold/grammar1.irtg $GDIR/$fold/llmtrain1.txt 
    echo "-- Generate grammar 2 right nosplit"
    $PY induct/induct.py $ALIGNMENT right nosplit   $GDIR/$fold/grammar2.irtg $GDIR/$fold/llmtrain2.txt 
    echo "-- Generate grammar 3 both  nosplit"
    $PY induct/induct.py $ALIGNMENT both  nosplit   $GDIR/$fold/grammar3.irtg $GDIR/$fold/llmtrain3.txt 
    echo "-- Generate grammar 4 left  semsplit"
    $PY induct/induct.py $ALIGNMENT left  semsplit  $GDIR/$fold/grammar4.irtg /dev/null
    echo "-- Generate grammar 5 right semsplit"
    $PY induct/induct.py $ALIGNMENT right semsplit  $GDIR/$fold/grammar5.irtg /dev/null
    echo "-- Generate grammar 6 both  semsplit"
    $PY induct/induct.py $ALIGNMENT both  semsplit  $GDIR/$fold/grammar6.irtg /dev/null
    
    for i in 1 2 3 4 5 6
    do
        echo "-- Generate weighted grammar $i + bulk parsing"
        $SCALA -J-Xmx4G -cp $ALTO RunAll.scala \
                $GDIR/$fold/grammar${i}.irtg \
                data/string_funql.txt \
                $GDIR/$fold/grammar${i}_em.irtg \
                data/string.txt \
                $GDIR/$fold/parsed$i.txt
        echo "-- Generate lisp format for parse $i"
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/$fold/grammar${i}.irtg $GDIR/$fold/parsed${i}.txt > $GDIR/$fold/parsed$i.lisp.txt
    done

    for i in 1 2 3
    do
        echo "-- Generate loglinear grammar $i"
        $PY induct/prepareLogLinModel.py $GDIR/$fold/grammar${i}.irtg > $GDIR/$fold/grammar${i}_llm.irtg
        echo "-- Generate features weights for grammar $i + bulk parsing"
        $SCALA -J-Xmx4G -cp $ALTO RunLogLin.scala \
                $GDIR/$fold/grammar${i}_llm.irtg \
                data/string_funql.txt \
                $GDIR/$fold/grammar${i}_features.irtg \
                data/string.txt \
                $GDIR/$fold/parsed$i_llm.txt

        echo "-- Generate lisp format for llm parse $i"
        $JAVA -cp $GDIR/:$ALTO ConvertToLisp $GDIR/$fold/grammar${i}.irtg $GDIR/$fold/parsed${i}.txt > $GDIR/$fold/parsed$i_llm.lisp.txt

    done

    for i in 2 3 4 5 6 7 8 9 10
    do
        echo "-- Generate grammar with $i splits"
        $PY induct/splitGrammar.py $GDIR/$fold/grammar3_em.irtg $i > $GDIR/$fold/grammar3_split$i.irtg
    done
    
done



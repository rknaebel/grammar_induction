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
ALTO=bin/alto-2.0.jar

if [ -d $GDIR ]
then
    rm -R $GDIR
fi
mkdir ./$GDIR

touch $RESULTS

$JAVAC -cp $ALTO -d $GDIR  extract/ConvertToLisp.java

for fold in 0 1 2 3 4 5 6 7 8 9
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
        $SCALA  -cp $ALTO TrainEM.scala \
                $GDIR/${fold}/grammar${i}.irtg \
                $EVAL/${fold}/emtraining.${fold} \
                $GDIR/${fold}/grammar${i}_em.irtg
    done

    for i in 2 3 4 #5 6 7 8 9 10
    do
        echo "-- Generate grammar with ${i} splits"
        $PY induct/splitGrammar.py $GDIR/${fold}/grammar3_em.irtg ${i} > $GDIR/${fold}/grammar3_split${i}.irtg

        echo "-- Reweight EM grammar with ${i} splits + bulk parsing"
        $SCALA -cp $ALTO TrainEM.scala \
                $GDIR/${fold}/grammar3_split${i}.irtg \
                $EVAL/${fold}/emtraining.${fold} \
                $GDIR/${fold}/grammar3_split${i}_em.irtg \
    done
    
done

for fold in 0 1 2 3 4 5 6 7 8 9
do
    for i in 1 2 3
    do
        echo "-- Generate loglinear grammar ${i}"
        $PY induct/prepareLogLinModel.py $GDIR/${fold}/grammar${i}.irtg > $GDIR/${fold}/grammar${i}_llm.irtg
        echo "-- Generate features weights for grammar ${i} + bulk parsing"
        $SCALA -cp $ALTO TrainLLM.scala \
                $GDIR/${fold}/grammar${i}_llm.irtg \
                $GDIR/${fold}/llmtrain${i}.txt \
                $GDIR/${fold}/grammar${i}_features.irtg
    done
done



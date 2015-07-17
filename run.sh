
ALIGNMENT=data/string2geo.A3.final5BEST

export JAVA_HOME=/cl-tools/jdk1.8.0_05/
export PATH=$JAVA_HOME/bin:$PATH
export PATH=/cl-tools/scala-2.11.7/bin/:$PATH 

GDIR=$1
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

$PY induct/induct.py $ALIGNMENT left  nosplit   $GDIR/grammar1.irtg $GDIR/llmtrain1.txt 
$PY induct/induct.py $ALIGNMENT right nosplit   $GDIR/grammar2.irtg $GDIR/llmtrain2.txt 
$PY induct/induct.py $ALIGNMENT both  nosplit   $GDIR/grammar3.irtg $GDIR/llmtrain3.txt 
$PY induct/induct.py $ALIGNMENT left  semsplit  $GDIR/grammar4.irtg /dev/null
$PY induct/induct.py $ALIGNMENT right semsplit  $GDIR/grammar5.irtg /dev/null
$PY induct/induct.py $ALIGNMENT both  semsplit  $GDIR/grammar6.irtg /dev/null

for i in 1 2 3 4 5 6
do
    echo "-- Generate weighted grammar $i"
    $SCALA -J-Xmx4G -cp $ALTO RunAll.scala \
            $GDIR/grammar${i}.irtg \
            data/string_funql.txt \
            $GDIR/grammar${i}_em.irtg \
            data/string.txt \
            $GDIR/parsed$i.txt
    $JAVA -cp $GDIR/:$ALTO ConvertToLisp $GDIR/grammar${i}_em.irtg $GDIR/parsed${i}.txt > $GDIR/parsed$i.lisp.txt
done

for i in 1 2 3
do
    echo "-- Generate loglinear grammar $i"
    $PY induct/prepareLogLinModel.py $GDIR/grammar${i}.irtg > $GDIR/grammar${i}_llm.irtg
done

for i in 2 3 4 5 6 7 8 9 10
do
    echo "-- Generate grammar with $i splits"
    $PY induct/readIrtg.py $GDIR/grammar3_em.irtg $i > $GDIR/grammar3_split$i.irtg
done


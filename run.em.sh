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


grammarBefore=$1
grammarAfter=$2
fold=$3
        echo "-- Generate weighted grammar ${i} + bulk parsing"
        $SCALA  -cp $ALTO TrainEM.scala \
                $GDIR/${fold}/${grammarBefore} \
                $EVAL/${fold}/emtraining.${fold} \
                $GDIR/${fold}/${grammarAfter}

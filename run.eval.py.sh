ALIGNMENT=alignment-5best

export JAVA_HOME=/cl-tools/jdk1.8.0_05/
export PATH=$JAVA_HOME/bin:$PATH
export PATH=/cl-tools/scala-2.11.7/bin/:$PATH

GDIR=./generate
EVAL=./evaluate
RESULTS=./$GDIR/results4.csv

SCALA="scala -J-Xmx4G"
JAVA="java -Xmx4G"
JAVAC=javac
PY=python
ALTO=bin/alto-2.0.jar

if [ ! -d $GDIR ]
then
    echo "No folder found!"
    exit
fi

$JAVAC -cp $ALTO -d $GDIR  extract/ConvertToLisp.java

for fold in $@
do
    echo "==> Evaluate fold ${fold}"
    
    for i in 1 2 3 4 5 6
    do
        $SCALA  -cp $ALTO BulkParse.scala \
            $GDIR/${fold}/grammar${i}.irtg \
            $EVAL/${fold}/teststring.${fold} \
            $GDIR/${fold}/parsed${i}.txt
        
        echo "== Evaluating result for grammar ${i}"
        $PY extract/parsedToLisp.py $GDIR/${fold}/parsed${i}.txt                                                 > $GDIR/${fold}/parsed${i}.tolisp
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/grammar${i}.irtg $GDIR/${fold}/parsed${i}.tolisp       > $GDIR/${fold}/parsed${i}.lisp
        $PY extract/lispToEvalb.py $GDIR/${fold}/parsed${i}.lisp                                                 > $GDIR/${fold}/parsed${i}.eval
        $PY extract/extractResults.py $EVAL/${fold}/testfunql.${fold} $GDIR/${fold}/parsed${i}.eval >> $RESULTS
        
        rm $GDIR/${fold}/parsed${i}.tolisp
        rm $GDIR/${fold}/parsed${i}.lisp 
        rm $GDIR/${fold}/parsed${i}.eval
        
        $SCALA  -cp $ALTO BulkParse.scala \
            $GDIR/${fold}/grammar${i}_em.irtg \
            $EVAL/${fold}/teststring.${fold} \
            $GDIR/${fold}/parsed${i}_em.txt
        
        echo "== Evaluating result for em grammar ${i}"
        $PY extract/parsedToLisp.py $GDIR/${fold}/parsed${i}_em.txt > $GDIR/${fold}/parsed${i}_em.tolisp
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/grammar${i}_em.irtg     $GDIR/${fold}/parsed${i}_em.tolisp > $GDIR/${fold}/parsed${i}_em.lisp
        $PY extract/lispToEvalb.py $GDIR/${fold}/parsed${i}_em.lisp > $GDIR/${fold}/parsed${i}_em.eval
        $PY extract/extractResults.py $EVAL/${fold}/testfunql.${fold} $GDIR/${fold}/parsed${i}_em.eval >> $RESULTS
        
        rm $GDIR/${fold}/parsed${i}_em.tolisp
        rm $GDIR/${fold}/parsed${i}_em.lisp
        rm $GDIR/${fold}/parsed${i}_em.eval
    done

    for i in 1 2 3
    do
        $SCALA  -cp $ALTO BulkParseLLM.scala \
            $GDIR/${fold}/grammar${i}_llm.irtg \
            $GDIR/${fold}/grammar${i}_features.irtg \
            $EVAL/${fold}/teststring.${fold} \
            $GDIR/${fold}/parsed${i}_llm.txt
        
        echo "== Evaluating result for llm grammar ${i}"
        $PY extract/parsedToLisp.py $GDIR/${fold}/parsed${i}_llm.txt > $GDIR/${fold}/parsed${i}_llm.tolisp
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/grammar${i}.irtg $GDIR/${fold}/parsed${i}_llm.tolisp > $GDIR/${fold}/parsed${i}_llm.lisp
        $PY extract/lispToEvalb.py $GDIR/${fold}/parsed${i}_llm.lisp > $GDIR/${fold}/parsed${i}_llm.eval
        $PY extract/extractResults.py $EVAL/${fold}/testfunql.${fold} $GDIR/${fold}/parsed${i}_llm.eval >> $RESULTS

        rm $GDIR/${fold}/parsed${i}_llm.tolisp
        rm $GDIR/${fold}/parsed${i}_llm.lisp
        rm $GDIR/${fold}/parsed${i}_llm.eval
    done

    for i in 2 3 4 #5 6 7 8 9 10
    do
        echo "-- Generate lisp format for parse ${i}"
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/grammar3_split${i}_em.irtg $GDIR/${fold}/parsed3_split${i}.txt > $GDIR/${fold}/parsed3_split${i}.lisp.txt
        
        echo "== Evaluating result for splitted grammar ${i}"
        $PY extract/parsedToLisp.py $GDIR/${fold}/parsed3_split${i}.txt > $GDIR/${fold}/parsed3_split${i}.tolisp
        $JAVA -cp $GDIR:$ALTO ConvertToLisp $GDIR/${fold}/parsed3_split${i}.irtg $GDIR/${fold}/parsed3_split${i}.tolisp > $GDIR/${fold}/parsed3_split${i}.lisp
        $PY extract/lispToEvalb.py $GDIR/${fold}/parsed3_split${i}.lisp > $GDIR/${fold}/parsed3_split${i}.eval
        $PY extract/extractResults.py $EVAL/${fold}/testfunql.${fold} $GDIR/${fold}/parsed3_split${i}.eval >> $RESULTS
        
        rm $GDIR/${fold}/parsed3_split${i}.tolisp
        rm $GDIR/${fold}/parsed3_split${i}.lisp
        rm $GDIR/${fold}/parsed3_split${i}.eval
    done
done


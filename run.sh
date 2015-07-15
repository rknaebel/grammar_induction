
ALIGNMENT=data/string2geo.A3.final5BEST
GDIR=generated

if [ -d $GDIR ]
then
    rm -R $GDIR
fi
mkdir ./$GDIR

python induct/induct.py $ALIGNMENT left  nosplit   $GDIR/grammar1.irtg $GDIR/llmtrain1.txt 
python induct/induct.py $ALIGNMENT right nosplit   $GDIR/grammar2.irtg $GDIR/llmtrain2.txt 
python induct/induct.py $ALIGNMENT both  nosplit   $GDIR/grammar3.irtg $GDIR/llmtrain3.txt 
python induct/induct.py $ALIGNMENT left  semsplit  $GDIR/grammar4.irtg /dev/null
python induct/induct.py $ALIGNMENT right semsplit  $GDIR/grammar5.irtg /dev/null
python induct/induct.py $ALIGNMENT both  semsplit  $GDIR/grammar6.irtg /dev/null

for i in 1 2 3 4 5 6
do
    echo "-- Generate weighted grammar $i"
    scala -J-Xmx4G -cp ".:bin/alto-1.1-SNAPSHOT-jar-with-dependencies.jar"  \
          RunAll.scala $GDIR/grammar${i}.irtg data/string_funql.txt \
          $GDIR/grammar${i}_em.irtg data/string.txt $GDIR/parsed$i.txt

done

for i in 1 2 3
do
    echo "-- Generate loglinear grammar $i"
    python induct/prepareLogLinModel.py $GDIR/grammar${i}.irtg > $GDIR/grammar${i}_llm.irtg
done

for i in 2 3 4 5 6 7 8 9 10
do
    echo "-- Generate grammar with $i splits"
    python induct/readIrtg.py $GDIR/grammar3_em.irtg $i > $GDIR/grammar3_split$i.irtg
done


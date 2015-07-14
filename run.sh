


python induct/induct.py data/string2geo.A3.final5BEST left  nosplit   > generated/grammar1.irtg
python induct/induct.py data/string2geo.A3.final5BEST right nosplit   > generated/grammar2.irtg
python induct/induct.py data/string2geo.A3.final5BEST both  nosplit   > generated/grammar3.irtg
python induct/induct.py data/string2geo.A3.final5BEST left  semsplit  > generated/grammar4.irtg
python induct/induct.py data/string2geo.A3.final5BEST right semsplit  > generated/grammar5.irtg
python induct/induct.py data/string2geo.A3.final5BEST both  semsplit  > generated/grammar6.irtg

for i in 1 2 3 4 5 6
do
    scala -cp ".:bin/alto-1.1-SNAPSHOT-jar-with-dependencies.jar"  \
          RunAll generated/grammar${i}.irtg data/string_funql.txt \
          generated/grammar${i}_w.irtg data/string.txt generated/parsed$i.txt -Xmx4G
done

for i in 2 3 4 5 6 7 8 9 10
do
    echo "Generate grammar with $i splits"
    python induct/readIrtg.py generated/grammar3_w.irtg $i > generated/grammar3_split$i.irtg
done


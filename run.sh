

for i in 1 2 3 4 5 6
do
    scala -cp ".:bin/alto-1.1-SNAPSHOT-jar-with-dependencies.jar"  \
          RunAll generated/grammar${i}.irtg data/string_funql.txt \
          generated/grammar${i}_w.irtg data/string.txt generated/parsed$i.txt -Xmx4G
done

for i in 2 3 4 5 6 7 8 9 10
do
    echo "Generate grammar with $i splits"
    python induct/readIrtg.py generated/grammar6_w.irtg $i > generated/grammar6_split$i.irtg
done


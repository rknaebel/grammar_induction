/**
* autor:
*
* date:
*
**/

// package

// import
import de.up.ling.irtg.corpus.Corpus;
import de.up.ling.irtg.InterpretedTreeAutomaton;
import de.up.ling.irtg.algebra.Algebra;
import de.up.ling.irtg.algebra.StringAlgebra;
import de.up.ling.irtg.algebra.TreeAlgebra;
import de.up.ling.irtg.corpus.Instance;

import de.saar.basic.StringTools;

import de.up.ling.tree.Tree;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;


import java.io.Reader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;

// class definition
public class ConvertToLisp {

    public static void main(String[] args) {
        
        try {
            FileInputStream grammarStream = new FileInputStream(args[0]);
            FileInputStream corpusStream  = new FileInputStream(args[1]);
            
            InterpretedTreeAutomaton irtg = InterpretedTreeAutomaton.read(grammarStream);
            Reader corpusReader           = new InputStreamReader(corpusStream);
            Corpus corpus = irtg.readCorpus(corpusReader);

            for (Instance ins : corpus) {
                Map<String,Object> tMap = ins.getInputObjects();
                List<String> s = (List<String>)tMap.get("s");
                List<String> strings = new ArrayList<String>();
                Tree t = (Tree)tMap.get("t");
                System.out.println(StringTools.join(s, " "));
                System.out.println(t.toLispString());
            }
        
        } catch(Exception e) {
            //System.out.println(e);
            e.printStackTrace();
        }
    }

}

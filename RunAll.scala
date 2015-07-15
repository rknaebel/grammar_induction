
import de.up.ling.irtg._
import de.up.ling.irtg.algebra._
import de.up.ling.irtg.automata._
import de.up.ling.irtg.hom._
import de.up.ling.irtg.signature._
import de.up.ling.irtg.corpus._
import de.up.ling.irtg.codec._
import de.up.ling.tree._
import de.saar.basic._
import de.up.ling.irtg.util.TestingTools._


import java.io._
import java.util.Date
import scala.collection.JavaConverters._

import scala.language.implicitConversions;

import ScalaShell._

//
// Start of the actual scala script
//
object RunAll extends App {
    
    val grammarFile = args(0)
    val trainingCorpusFile = args(1)
    val weightedGrammarFile = args(2)
    val stringFile = args(3)
    val parsedStringFile = args(4)
    
    //implicit def intmap2integermap(map:scala.collection.immutable.Map[String,Int]) = map.asJava.asInstanceOf[java.util.Map[String,java.lang.Integer]]
    //implicit def stringmap2java(map:scala.collection.immutable.Map[String,String]) = map.asJava
    //implicit def string2tree(s:String) = pt(s)

    println("Reading the grammar")
    val irtg = loadIrtg(grammarFile)
    
    println("Read the EM training corpus")
    val corpus = irtg.readCorpus(file(trainingCorpusFile))

    println("Compute parse charts and create charts.zip file")
    Charts.computeCharts(corpus, irtg, fostream("charts.zip"))
    corpus.attachCharts("charts.zip")

    println("Start EM training")
    irtg.trainEM(corpus)

    new File("charts.zip").delete()

    println("Write the weighted grammar")
    val writer = new PrintWriter(new File(weightedGrammarFile))
    writer.write(irtg.toString)
    writer.close

    println("Read bulk parse corpus")
    val testCorpus = irtg.readCorpus(file(stringFile))
    val output = new FileWriter(parsedStringFile)

    val s = "Parsed from " + testCorpus.getSource() + "\nat " + new Date().toString()
    val cw = new CorpusWriter(irtg, true, s, output)

    println("Bulkparse corpus and print to output file")
    irtg.bulkParse(testCorpus, cw, null)

    output.close
    
    //val parsedCorpus = irtg.readCorpus(file(parsedStringFile))
    //println(parsedCorpus)
    //parsedCorpus.asInstanceOf[Interable].foreach {
    //    instance => println(instance)
    //}

    //for (ins : Instance <- parsedCorpus) {
    //    println(ins)
    //    val tMap = ins.getInputObjects()
        //val tree : Tree = tMap.get("t").asInstanceOf[Tree]
        //println(tree.toLispString)
    //}
}

RunAll.main(args)







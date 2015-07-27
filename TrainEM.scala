
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

    println("Reading the grammar")
    val irtg = loadIrtg(grammarFile)
    
    println("Read the EM training corpus")
    val corpus = irtg.readCorpus(file(trainingCorpusFile))

    println("Compute parse charts and create charts.zip file")
    Charts.computeCharts(corpus, irtg, fostream("charts_em.zip"))
    corpus.attachCharts("charts_em.zip")

    println("Start EM training")
    irtg.trainEM(corpus)

    println("Write the weighted grammar")
    val writer = new PrintWriter(new File(weightedGrammarFile))
    writer.write(irtg.toString)

    new File("charts_em.zip").delete()
    writer.close
}

RunAll.main(args)







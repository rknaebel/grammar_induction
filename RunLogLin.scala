
import de.up.ling.irtg._
import de.up.ling.irtg.algebra._
import de.up.ling.irtg.automata._
import de.up.ling.irtg.hom._
import de.up.ling.irtg.signature._
import de.up.ling.irtg.corpus._
import de.up.ling.irtg.codec._
import de.up.ling.tree._
import de.up.ling.irtg.maxent._
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
    val weightedFeatures = args(2)
    val stringFile = args(3)
    val parsedStringFile = args(4)
    
    println("Reading the grammar")
    val irtg = loadIrtg(grammarFile).asInstanceOf[MaximumEntropyIrtg]
    
    println("Read the ME training corpus")
    val corpus = irtg.readCorpus(file(trainingCorpusFile))

    println("Compute parse charts and create charts.zip file")
    Charts.computeCharts(corpus, irtg, fostream("charts.zip"))
    corpus.attachCharts("charts.zip")

    println("Start ME training")
    irtg.trainMaxent(corpus)

    new File("charts.zip").delete()

    println("Write the weighted grammar")
    val writer = new PrintWriter(new File(weightedFeatures))
    irtg.writeWeights(writer)
    writer.close

    println("Read bulk parse corpus")
    val testCorpus = irtg.readCorpus(file(stringFile))
    val output = new FileWriter(parsedStringFile)

    val s = "Parsed from " + testCorpus.getSource() + "\nat " + new Date().toString()
    val cw = new CorpusWriter(irtg, true, s, output)
    
    println("Bulkparse corpus and print to output file")
    irtg.bulkParse(testCorpus, cw, null)
    
    output.close
}

RunAll.main(args)







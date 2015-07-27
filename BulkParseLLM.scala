
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
    val weightsFile = args(1)
    val stringFile = args(2)
    val parsedStringFile = args(3)
    
    println("Reading the grammar")
    val irtg = loadIrtg(grammarFile).asInstanceOf[MaximumEntropyIrtg]
    
    println("Read the feature weights")
    irtg.readWeights(file(weightsFile))

    println("Read bulk parse corpus")
    val testCorpus = irtg.readCorpus(file(stringFile))
    val output = new FileWriter(parsedStringFile)

    val s = "Parsed from " + testCorpus.getSource() + "\nat " + new Date().toString()
    val cw = new CorpusWriter(irtg, s, output)

    println("Bulkparse corpus and print to output file")
    irtg.bulkParse(testCorpus, cw, null)

    output.close
}

RunAll.main(args)







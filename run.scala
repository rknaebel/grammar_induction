val irtg = loadIrtg("data/grammar.irtg")

val corpus = irtg.readCorpus(file("data/alto.irtg"))

Charts.computeCharts(corpus, irtg, fostream("charts.zip"))
corpus.attachCharts(new Charts(new FileInputStreamSupplier(new File("charts.zip"))))

irtg.trainEM(corpus)

new File("charts.zip").delete()

val writer = new PrintWriter(new File("data/weighten_alto.irtg"))
writer.write(irtg.toString)
writer.close


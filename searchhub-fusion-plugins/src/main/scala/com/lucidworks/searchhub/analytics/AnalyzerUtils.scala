package com.lucidworks.searchhub.analytics

import com.lucidworks.spark.analysis.LuceneTextAnalyzer

/**
  * Created by jakemannix on 4/29/16.
  */
object AnalyzerUtils {
  val whitespaceSchema =
    """{ "analyzers": [
      |  { "name": "ws",
      |    "tokenizer": { "type": "whitespace"} }],
      |  "fields": [{ "regex": ".+", "analyzer": "ws" } ]}""".stripMargin

  val stdAnalyzerSchema =
    """{ "analyzers": [
      |  { "name": "StdTokLowerStop",
      |    "tokenizer": { "type": "standard" },
      |    "filters": [
      |    { "type": "lowercase" },
      |    { "type": "stop" }] }],
      |  "fields": [{ "regex": ".+", "analyzer": "StdTokLowerStop" } ]}
    """.stripMargin
  val germanStemSchema =
    """{ "analyzers": [
      |  { "name": "gstem",
      |    "tokenizer": { "type": "standard" },
      |    "filters": [
      |      {"type": "lowercase"},
      |      {"type": "stop"},
      |      {"type": "germanstem"}
      |    ]}],
      | "fields": [{ "regex": ".+", "analyzer": "gstem" } ]}""".stripMargin

  val porterStemSchema =
    """{ "analyzers": [
      |  { "name": "std",
      |    "tokenizer": { "type": "standard" },
      |    "filters": [
      |      {"type": "lowercase"},
      |      {"type": "stop"},
      |      {"type": "porterstem"}
      |     ]}],
      |  "fields": [{ "regex": ".+", "analyzer": "std" } ]}""".stripMargin

  def analyzerFn(schema: String): String => List[String] = {
    val analyzer = new LuceneTextAnalyzer(schema)
    (s: String) => analyzer.analyze("N/A", s).toList
  }
}

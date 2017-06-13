// package com.lucidworks.searchhub.analytics

// import org.apache.spark.mllib.linalg.{Vectors, Vector => SparkVector}
// import org.apache.spark.sql.DataFrame
// import org.apache.spark.sql.functions._

// /**
//   *
//   */
// case class TfIdfVectorizer(tokenizer: String => List[String],
//                            dictionary: Map[String, Int],
//                            idfs: Map[String, Double]) extends (String => SparkVector) {
//   override def apply(s: String): SparkVector = {
//     val tokenTfs = tokenizer(s).groupBy(identity).mapValues(_.size).toList
//     val tfIdfMap = tokenTfs.flatMap { case (token, tf) =>
//       dictionary.get(token).map(idx => (idx, tf * idfs.getOrElse(token, 1.0))) }
//     val norm = math.sqrt(tfIdfMap.toList.map(_._2).foldLeft(0d) { case (tot , w) => tot + w * w })
//     val normalizedWeights = if (norm > 0) tfIdfMap.map { case (idx, w) => (idx, w / norm)} else tfIdfMap
//     Vectors.sparse(dictionary.size, normalizedWeights)
//   }
// }

// object TfIdfVectorizer {
//   /**
//     *
//     * @param df
//     * @param tokenizer
//     * @param fieldName
//     * @return
//     */
//   def build(df: DataFrame, tokenizer: String => List[String], fieldName: String,
//             minSupport: Int = 5, maxSupportFraction: Double = 0.75) = {
//     val tokenField = fieldName + "_tokens"
//     val withWords = df.select(fieldName).explode(fieldName, tokenField)(tokenizer.andThen(_.distinct))
//     val numDocs = df.count().toDouble
//     val maxSupport = maxSupportFraction * numDocs
//     val tokenCountsDF =
//       withWords.groupBy(tokenField).count().filter(col("count") > minSupport && col("count") < maxSupport)
//     val idfs = tokenCountsDF.map(r => (r.getString(0), math.log(1 + (numDocs / (1 + r.getLong(1)))))).collect().toMap
//     val dictionary = idfs.keys.toArray.zipWithIndex.toMap
//     TfIdfVectorizer(tokenizer, dictionary, idfs)
//   }

//   def vectorize(df: DataFrame, vectorizer: TfIdfVectorizer, fieldName: String) = {
//     val vectorizerUdf = udf(vectorizer)
//     df.withColumn(fieldName + "_vect", vectorizerUdf(col(fieldName)))
//   }
// }

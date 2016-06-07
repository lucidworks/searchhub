package com.lucidworks.searchhub.analytics

import org.apache.spark.ml.param.IntParam
import org.apache.spark.ml.{PipelineModel, Model, Pipeline}
import org.apache.spark.ml.classification.RandomForestClassifier
import org.apache.spark.ml.clustering.{LDAModel, LDA, KMeans}
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator
import org.apache.spark.ml.feature.{IndexToString, StringIndexer, Word2Vec}
import org.apache.spark.ml.tuning.{CrossValidator, ParamGridBuilder}
import org.apache.spark.mllib.evaluation.MulticlassMetrics
import org.apache.spark.rdd.RDD
import org.apache.spark.mllib.linalg.{Vector => SparkVector, Vectors, DenseVector, SparseVector}
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions._

object ManyNewsgroups {

  def subtract(v1: SparkVector, v2: SparkVector): SparkVector = {
    (v1, v2) match {
      case (d1: DenseVector, d2: DenseVector) => {
        val (a1, a2) = (d1.toArray, d2.toArray)
        Vectors.dense(a1.indices.toArray.map(i => a1(i) - a2(i)))
      }
      case (sp1: SparseVector, sp2: SparseVector) => subtract(sp1.toDense, sp2.toDense) // TODO / FIXME!!!
      case _ => throw new IllegalArgumentException("all vectors are either dense or sparse!")
    }
  }

  def normSquaredL2(v: SparkVector) = v.toArray.foldLeft(0.0) { case(a: Double,b: Double) => a + b*b }

  def distSquaredL2(v1: SparkVector, v2: SparkVector) = normSquaredL2(subtract(v1, v2))

  def distL2Matrix(a: Array[SparkVector]) = {
    for {
      (v1, i) <- a.zipWithIndex
      (v2, j) <- a.zipWithIndex
    } yield {
      (i, j, distSquaredL2(v1, v2))
    }
  }

  def buildKmeansModel(df: DataFrame, k: Int = 5, maxIter: Int = 10, fieldName: String) = {
    val kMeans = new KMeans()
      .setK(k)
      .setMaxIter(maxIter)
      .setFeaturesCol(fieldName + "_vect")
      .setPredictionCol("kmeans_cluster_i")
    kMeans.fit(df)
  }

  def buildLDAModel(df: DataFrame, k: Int = 5, fieldName: String) = {
    val lda = new LDA().setK(k).setFeaturesCol(fieldName + "_vect")
    lda.fit(df)
  }

  /**
    * Helper method to let you inspect your LDA model
    * @param lda LDAModel fit to your corpus
    * @param vectorizer the weighted dictionary tokenizer + vectorizer struct
    * @return a map of topic id -> list of (token, weight) pairs sorted by probability
    */
  def tokensForTopics(lda: LDAModel, vectorizer: TfIdfVectorizer): Map[Int, List[(String, Double)]] = {
    val reverseDictionary = vectorizer.dictionary.toList.map(_.swap).toMap
    val topicDist = lda.topicsMatrix
    val tokenWeights = for { k <- 0 until lda.getK; i <- 0 until vectorizer.dictionary.size } yield {
      k -> (reverseDictionary(i), topicDist(i, k))
    }
    tokenWeights.groupBy(_._1).mapValues(_.map(_._2).toList.sortBy(-_._2))
  }


  def buildWord2VecModel(df: DataFrame, tokenzier: String => List[String], fieldName: String) = {
    val tokenize = udf(tokenzier)
    val withTokens = df.withColumn(fieldName + "_tokens", tokenize(col(fieldName)))
    val word2Vec = new Word2Vec()
      .setInputCol(fieldName + "_tokens")
      .setOutputCol(fieldName + "_w2v")
    word2Vec.fit(withTokens)
  }

  def trainRandomForestClassifier(trainingData: DataFrame,
                                  testData: DataFrame,
                                  labelColumnName: String,
                                  featuresColumnName: String,
                                  paramGrids: Map[RandomForestClassifier => IntParam, Array[Int]] = Map.empty) = {
    val labelIndexCol = labelColumnName + "_idx"
    val featureVectorCol = featuresColumnName + "_vect"
    val labelIndexer = new StringIndexer()
      .setInputCol(labelColumnName)
      .setOutputCol(labelIndexCol)
      .fit(trainingData)
    val randomForest: RandomForestClassifier = new RandomForestClassifier()
      .setLabelCol(labelIndexCol)
      .setFeaturesCol(featureVectorCol)
    val predictionCol = "prediction"
    val labelConverter = new IndexToString()
      .setInputCol(predictionCol)
      .setOutputCol("predicted_" + labelColumnName)
      .setLabels(labelIndexer.labels)
    val rfPipe = new Pipeline().setStages(Array(labelIndexer, randomForest, labelConverter))
    val paramGridMap = paramGrids.map { case (paramFn, grid) => (paramFn(randomForest), grid) }
    val paramGrid = new ParamGridBuilder()
      .addGrid(randomForest.maxDepth, paramGridMap.getOrElse(randomForest.maxDepth, Array(5, 20, 40)))
      .addGrid(randomForest.maxBins, paramGridMap.getOrElse(randomForest.maxBins, Array(8, 32, 64)))
      .addGrid(randomForest.numTrees, paramGridMap.getOrElse(randomForest.numTrees, Array(25, 100, 400)))
      .build()
    val evaluator = new MulticlassClassificationEvaluator()
      .setLabelCol(labelIndexCol)
      .setPredictionCol(predictionCol)
      .setMetricName("precision")  // "f1", "precision", "recall", "weightedPrecision", "weightedRecall"
    val cv =  // 5-fold cross-validation
      new CrossValidator().setEstimator(rfPipe).setEvaluator(evaluator).setEstimatorParamMaps(paramGrid).setNumFolds(5)

    val model = cv.fit(trainingData)
    val bestModel = model.bestModel.asInstanceOf[Model[PipelineModel]]

    // measure metrics on unseen-by-cross-validation held-out test data.
    val classifiedData = bestModel.transform(testData)
    val predictionsAndLabels: RDD[(Double, Double)] =
      classifiedData.select(predictionCol, labelIndexCol).map(r => (r.getDouble(0), r.getDouble(1)))
    val metrics = new MulticlassMetrics(predictionsAndLabels)
    (bestModel, metrics)
  }

}

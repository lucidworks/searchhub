package com.lucidworks.apollo.pipeline.index.stages.searchhub.lda;

import com.lucidworks.spark.analysis.LuceneTextAnalyzer;
import com.lucidworks.spark.ml.MLModel;
import com.lucidworks.spark.ml.SparkContextAware;
import org.apache.spark.SparkContext;
import org.apache.spark.mllib.clustering.LDAModel;
import org.apache.spark.mllib.feature.Word2VecModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import scala.Tuple2;
import org.apache.spark.api.java.function.VoidFunction;

import java.io.*;
import java.util.*;
import org.apache.spark.api.java.JavaRDD;


public class LDARelatedTerms implements MLModel, SparkContextAware {
    private static final Logger log = LoggerFactory.getLogger(LDARelatedTerms.class);
    protected String modelId;
    protected String[] featureFields;
    protected LuceneTextAnalyzer textAnalyzer;
    protected LDAModel ldaModel;
    protected SparkContext sparkContext;
    private static final String noHTMLstdAnalyzerSchema = "{ \'analyzers\': [{ \'name\': \'std_tok_lower\','charFilters': [{ 'type': 'htmlstrip' }] ,\'tokenizer\': { \'type\': \'standard\' },\'filters\': [{ \'type\': \'lowercase\' }]}],  \'fields\': [{ \'regex\': \'.+\', \'analyzer\': \'std_tok_lower\' }]}".replaceAll("\'", "\"").replaceAll("\\s+", " ");

    public String getId(){
        return this.modelId;
    }
    public String getType(){
        return "spark-mllib";//seems this info is redundant and not used.
    }
    public String[] getFeatureFields(){
        return this.featureFields;
    }

    public void init(String modelId, File modelDir, Map<String, Object> modelSpecJson) throws Exception {

    }

    public void initSparkContext(SparkContext sparkContext) {
        this.sparkContext = sparkContext;
    }

    public List<String> prediction(Object[] tuple) throws Exception {
        // Get the terms from the document and put them into terms
        LinkedList<String> terms = new LinkedList();
        Integer terms_count = 0;
        if(tuple[0] != null) {
            terms.addAll(this.textAnalyzer.analyzeJava(this.featureFields[0], tuple[0].toString()));
        }
        for (String term:terms){

        }
        for(Tuple2<String, Double> topTerm:topkTerms){
            if(this.w2vModel.wordIndex().contains(topTerm._1)){//elif words not in data, do nothing
                Tuple2<String,Object>[] synonyms=w2vModel.findSynonyms(topTerm._1, 2);//find 2 synonyms for each top word
                for(Tuple2 tuples: synonyms){
                    out.add((String)tuples._1);
                }
            }
        }

        return out;
    }
}
package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v;

import com.lucidworks.spark.analysis.LuceneTextAnalyzer;
import com.lucidworks.spark.ml.MLModel;
import com.lucidworks.spark.ml.SparkContextAware;
import org.apache.spark.SparkContext;
import org.apache.spark.mllib.feature.Word2VecModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import scala.Tuple2;
import org.apache.spark.api.java.function.VoidFunction;

import java.io.*;
import java.util.*;
import org.apache.spark.api.java.JavaRDD;


public class W2VRelatedTerms implements MLModel, SparkContextAware {
    private static final Logger log = LoggerFactory.getLogger(W2VRelatedTerms.class);
    protected String modelId;
    protected String[] featureFields;
    protected HashMap<String,Double> idfMap;
    protected LuceneTextAnalyzer textAnalyzer;
    protected Word2VecModel w2vModel;
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
        //requirements for the arguments:
        //modelSpecJson.featureFields exists. And it should be able to be casted to "List"
        //the object for init is to provide everything needed for prediction method and other methods
        this.idfMap=new HashMap();
        this.modelId = modelId;
        //get this.featureFields from modelSpecJson
        List fields = (List)modelSpecJson.get("featureFields");
        if(fields == null) {
            throw new IllegalArgumentException("featureFields is required metadata");
        } else {
            this.featureFields = (String[])fields.toArray(new String[0]);

            for(int labelsProp = 0; labelsProp < this.featureFields.length; ++labelsProp) {
                this.featureFields[labelsProp] = this.featureFields[labelsProp].trim();
            }

            //get this.idfMap. It is used to regenerate the idfMap(used to calculate tfidf)
            try {
                String mapDir=modelDir.getAbsolutePath()+"/idfMapData";
                JavaRDD<String> distFile = sparkContext.textFile(mapDir,2).toJavaRDD();
                distFile.foreach(new VoidFunction<String>(){
                    public void call(String line) {
                        String[] tmp=line.split(",");
                        idfMap.put(tmp[0].substring(1),Double.parseDouble(tmp[1].substring(0,tmp[1].length()-1))); //
                    }});

            } catch (Exception e) {
                e.printStackTrace();
            }

            this.textAnalyzer = new LuceneTextAnalyzer(noHTMLstdAnalyzerSchema);


            //deserialize w2v model
            try {
                this.w2vModel = Word2VecModel.load(this.sparkContext, modelDir.getAbsolutePath() + "/w2vModelData");
            } catch (Exception e){
                log.error("error when loading model");
                e.printStackTrace();
                throw e;
            }
        }

    }

    public void initSparkContext(SparkContext sparkContext) {
        this.sparkContext = sparkContext;
    }

    public List<String> prediction(Object[] tuple) throws Exception {
        //transform the input tuple to input vector(tokenized terms)
        LinkedList<String> terms = new LinkedList();
        if(tuple[0] != null) {
            terms.addAll(this.textAnalyzer.analyzeJava(this.featureFields[0], tuple[0].toString()));
        }
        //get a hashmap which stores the count of each term in terms. This is the tf map
        HashMap<String,Integer> tf=new HashMap();
        for(int i=0;i<terms.size();i++){
            tf.put(terms.get(i),tf.getOrDefault(terms.get(i),0)+1);
        }
        //combine tf and idf to get a tfidf hashmap
        HashMap<String,Double> tfidf=new HashMap();
        for(String key:tf.keySet()){
            //in tfidf, we only have terms in tf map. and if the term is not in idf, we give it a default value 1
            tfidf.put(key,tf.get(key)*this.idfMap.getOrDefault(key,1.0));
        }
        //find k top tuples
        Comparator<Tuple2<String,Double>> comparator=new Comparator<Tuple2<String, Double>>() {
            @Override
            public int compare(Tuple2<String, Double> o1, Tuple2<String, Double> o2) {
                return o1._2.compareTo(o2._2);
            }
        };
        PriorityQueue<Tuple2<String, Double>> largestTfIdf=new PriorityQueue<>(100, comparator);
        for(String key:tfidf.keySet()){
            if(largestTfIdf.size()<5){
                largestTfIdf.add(new Tuple2(key, tfidf.get(key)));
            }
            else{
                if(tfidf.get(key)>largestTfIdf.peek()._2){
                    largestTfIdf.remove();
                    largestTfIdf.add(new Tuple2(key, tfidf.get(key)));
                }
            }
        }

        //sort the top k tuples
        ArrayList<Tuple2<String, Double>> topkTerms=new ArrayList<Tuple2<String, Double>>();
        Iterator<Tuple2<String, Double>> iter=largestTfIdf.iterator();
        while(iter.hasNext()){
            topkTerms.add(iter.next());
        }
        topkTerms.sort(comparator);
        Collections.reverse(topkTerms);

        //find related terms for each of the topWords(according to tfidf)
        ArrayList<String> out=new ArrayList();

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

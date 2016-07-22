package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v;

import com.lucidworks.spark.analysis.LuceneTextAnalyzer;
import com.lucidworks.spark.ml.MLModel;
import org.apache.spark.SparkConf;
import org.apache.spark.SparkContext;
import org.apache.spark.mllib.feature.Word2VecModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import scala.Tuple2;

import java.io.*;
import java.net.UnknownHostException;
import java.util.*;
import java.net.InetAddress;


public class TfIdfTopTerms implements MLModel{
    private static final Logger log = LoggerFactory.getLogger(TfIdfTopTerms.class);
    protected String modelId;
    protected String[] featureFields;
    protected HashMap<String,Double> idfMap;
    protected LuceneTextAnalyzer textAnalyzer;
    protected Word2VecModel w2vModel;
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
                BufferedReader br=new BufferedReader(new FileReader(modelDir.getAbsolutePath()+"/tryToAddIdfMap"));
                String line;
                while ((line=br.readLine())!=null){
                    String[] splittedLine=line.split(",");
                    if(splittedLine.length==2){
                        this.idfMap.put(splittedLine[0],Double.parseDouble(splittedLine[1]));
                    }
                    else{
                        int length=splittedLine.length;
                        String tmp=String.join(",", Arrays.copyOfRange(splittedLine, 0, length-1));
                        this.idfMap.put(tmp,Double.parseDouble(splittedLine[length-1]));
                    }
                }
            } catch (Exception var10) {
                var10.printStackTrace();
            }

            this.textAnalyzer = new LuceneTextAnalyzer(noHTMLstdAnalyzerSchema);


            //begin w2v part
            SparkConf sconf=new SparkConf();
            try {
                sconf.setMaster("spark://" + InetAddress.getLocalHost().getHostAddress() + ":8766").setAppName("GetW2vModel");//TODO:MAKE SURE THIS IS A REASONABLE TREATMENT
            } catch (UnknownHostException e){
                System.out.println("cannot get ip");
            }
            SparkContext sc=SparkContext.getOrCreate(sconf);
            this.w2vModel=Word2VecModel.load(sc,modelDir.getAbsolutePath()+"/w2vModelData");

        }

    }

    public List<String> prediction(Object[] tuple) throws Exception {
        //1.transform the input tuple to input vector(tokenized terms)
        LinkedList<String> terms = new LinkedList();
        if(tuple[0] != null) {
            terms.addAll(this.textAnalyzer.analyzeJava(this.featureFields[0], tuple[0].toString()));
        }
        //2.make a predict function
        HashMap<String,Integer> tf=new HashMap();
        for(int i=0;i<terms.size();i++){
            tf.put(terms.get(i),tf.getOrDefault(terms.get(i),0)+1);
        }
        HashMap<String,Double> tfidf=new HashMap();
        for(String key:tf.keySet()){
            tfidf.put(key,tf.get(key)*this.idfMap.getOrDefault(key,1.0));
        }
        //TODO:find k largest values, may need to optimize
        List<Map.Entry<String, Double>> tfidfList =
                new LinkedList<Map.Entry<String, Double>>(tfidf.entrySet());
        // Sort list with comparator, to compare the Map values

        Collections.sort(tfidfList, new Comparator<Map.Entry<String, Double>>() {
            public int compare(Map.Entry<String, Double> o1,
                               Map.Entry<String, Double> o2) {
                return -(o1.getValue()).compareTo(o2.getValue());
            }
        });

        //3.feed the input vector into the predict function
        /*
        ArrayList<String> out=new ArrayList<String>();
        for(int i=0;i<Math.min(5,tfidfList.size());i++){
            out.add(tfidfList.get(i).getKey());
        }
        */
        ArrayList<String> topWords=new ArrayList();
        for (int i=0;i<Math.min(5,tfidfList.size());i++){
            topWords.add(tfidfList.get(i).getKey());
        }

        //begin w2v part
        ArrayList<String> out=new ArrayList();
        out.add("");
        for(String word:topWords){
            if(this.w2vModel.wordIndex().contains(word)){//elif words not in data, do nothing
                Tuple2<String,Object>[] synonyms=w2vModel.findSynonyms(word,2);//find 2 synonyms for each top word
                for(Tuple2 tuples: synonyms){
                    out.set(0,out.get(0)+tuples._1+",");
                }
            }
        }
        out.set(0,out.get(0).substring(0,out.get(0).length()-1));
        return out;


    }
}

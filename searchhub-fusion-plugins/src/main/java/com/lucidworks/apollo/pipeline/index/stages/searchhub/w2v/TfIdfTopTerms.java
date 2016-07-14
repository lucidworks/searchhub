package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v;

import com.lucidworks.spark.analysis.LuceneTextAnalyzer;
import com.lucidworks.spark.ml.MLModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.util.*;


public class TfIdfTopTerms implements MLModel{
    private static final Logger log = LoggerFactory.getLogger(TfIdfTopTerms.class);
    protected String modelId;
    protected String[] featureFields;
    protected String[] labels;
    protected HashMap<String,Double> idfMap;
    protected LuceneTextAnalyzer textAnalyzer;
    private static final String noHTMLstdAnalyzerSchema = "{ \'analyzers\': [{ \'name\': \'std_tok_lower\','charFilters': [{ 'type': 'htmlstrip' }] ,\'tokenizer\': { \'type\': \'standard\' },\'filters\': [{ \'type\': \'lowercase\' }]}],  \'fields\': [{ \'regex\': \'.+\', \'analyzer\': \'std_tok_lower\' }]}".replaceAll("\'", "\"").replaceAll("\\s+", " ");


    public String getId(){
        return this.modelId;
    }

    public String getType(){
        return "spark-mllib";//TODO:is this a reasonable return value??check at what place used it
    }

    public String[] getFeatureFields(){
        return this.featureFields;
    }

    public void init(String modelId, File modelDir, Map<String, Object> modelSpecJson) throws Exception {
        //requirements for the arguments:
        //modelSpecJson.featureFields exists. And it should be able to be casted to "List"
        this.idfMap=new HashMap();
        this.modelId = modelId;
        List fields = (List)modelSpecJson.get("featureFields");
        System.out.println(fields);
        if(fields == null) {
            throw new IllegalArgumentException("featureFields is required metadata for spark-mllib based models!");
        } else {

            this.featureFields = (String[])fields.toArray(new String[0]);

            for(int labelsProp = 0; labelsProp < this.featureFields.length; ++labelsProp) {
                this.featureFields[labelsProp] = this.featureFields[labelsProp].trim();
            }


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

        }

    }

    public List<String> prediction(Object[] tuple) throws Exception {
        //1.transform tuple into a good input Vector
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
        ArrayList<String> out=new ArrayList<String>();
        for(int i=0;i<Math.min(5,tfidfList.size());i++){
            out.add(tfidfList.get(i).getKey());
        }
        return out;
    }
}

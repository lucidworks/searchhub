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
        //TODO:check how the example supplies modelSpecJson

        this.modelId = modelId;
        List fields = (List)modelSpecJson.get("featureFields");
        if(fields == null) {
            throw new IllegalArgumentException("featureFields is required metadata for spark-mllib based models!");
        } else {
            this.featureFields = (String[])fields.toArray(new String[0]);

            for(int labelsProp = 0; labelsProp < this.featureFields.length; ++labelsProp) {
                this.featureFields[labelsProp] = this.featureFields[labelsProp].trim();
            }


            try {
                BufferedReader br=new BufferedReader(new FileReader(modelDir));
                String line;
                while ((line=br.readLine())!=null){
                    String[] splittedLine=line.split(",");
                    idfMap.put(splittedLine[0],Double.parseDouble(splittedLine[1]));
                }
            } catch (Exception var10) {
                var10.printStackTrace();
            }

            this.textAnalyzer = new LuceneTextAnalyzer(noHTMLstdAnalyzerSchema);
        }
    }

    public List<String> prediction(Object[] tuple) throws Exception {
        //1.transform tuple into a good input Vector
        LinkedList terms = new LinkedList();
        Object prediction;
        for(int vector = 0; vector < tuple.length; ++vector) {
            prediction = tuple[vector];
            if(prediction != null) {
                terms.addAll(this.textAnalyzer.analyzeJava(this.featureFields[vector], prediction.toString()));
            }
        }
        //2.make a predict function

        //3.feed the input vector into the predict function
        ArrayList<String> out=new ArrayList<String>();
        out.add("test");
        return out;
    }
}

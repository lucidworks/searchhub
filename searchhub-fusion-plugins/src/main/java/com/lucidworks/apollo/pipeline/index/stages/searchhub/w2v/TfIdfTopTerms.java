package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v;

import com.lucidworks.spark.analysis.LuceneTextAnalyzer;
import com.lucidworks.spark.ml.MLModel;
import com.lucidworks.spark.ml.SparkContextAware;
import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import org.apache.spark.SparkContext;
import org.apache.spark.mllib.feature.ChiSqSelectorModel;
import org.apache.spark.mllib.feature.HashingTF;
import org.apache.spark.mllib.feature.Normalizer;
import org.apache.spark.mllib.feature.StandardScalerModel;
import org.apache.spark.mllib.feature.VectorTransformer;
import org.apache.spark.mllib.linalg.Vector;
import org.apache.spark.mllib.linalg.Vectors;
import org.codehaus.jackson.map.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;



public class TfIdfTopTerms implements MLModel{
    protected String modelId;
    protected String featureFields;
    protected String[] labels;
    protected HashMap<String,Double> idfMap;
    protected LuceneTextAnalyzer textAnalyzer;


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
        //modelSpecJson.labels exists. And it should be able to be casted to "String". Each label should
        //be separated by ','.
        //modelSpecJson.modelClassName exists. And it should be able to be casted to "String".
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

            String var11 = (String)modelSpecJson.get("labels");
            if(var11 != null && !var11.isEmpty()) {
                this.labels = var11.split(",");

                for(int startMs = 0; startMs < this.labels.length; ++startMs) {
                    this.labels[startMs] = this.labels[startMs].trim();
                }
            } else {
                this.labels = null;
            }

            long var12 = System.currentTimeMillis();

            try {
                BufferedReader br=new BufferedReader(new FileReader(modelDir));
                String line=null;
                while ((line=br.readLine())!=null){
                    String[] splittedLine=line.split(",");
                    idfMap.put(splittedLine[0],Double.parseDouble(splittedLine[1]));
                }
            } catch (Exception var10) {
                var10.printStackTrace();
            }

            long diffMs = System.currentTimeMillis() - var12;
            log.info("Took {} ms to load Spark mllib ClassificationModel of type {}", Long.valueOf(diffMs), this.mllibModel.getClass().getName());//check to this point
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

    }
}

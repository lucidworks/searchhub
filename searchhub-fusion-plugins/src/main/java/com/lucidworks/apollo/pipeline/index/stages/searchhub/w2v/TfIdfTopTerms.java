package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v;

import com.lucidworks.spark.analysis.LuceneTextAnalyzer;
import com.lucidworks.spark.ml.MLModel;
import com.lucidworks.spark.ml.SparkContextAware;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
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

  public String getId(){
    return this.modelId;
  }

  public String getType(){
    return "spark-mllib";//TODO:is this a reasonable return value??
  }

  public String[] getFeatureFields(){
    return this.featureFields;
  }

  public void init(String modelId, File modelDir, Map<String, Object> modelSpecJson) throws Exception {
    //requirements for the arguments:
    //modelSpecJson.featureFields exists. And it should be able to be casted to "List"
    //modelSpecJson.labels exists. And it should be able to be casted to "String". Each label should
    //be separated by ','.

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

        long var12 = System.currentTimeMillis();//check to this point, TODO:check this.loadClassificationModel
        this.mllibModel = this.loadClassificationModel(modelDir, modelSpecJson);

        try {
            this.predictionMethod = this.mllibModel.getClass().getMethod("predict", new Class[]{Vector.class});
        } catch (Exception var10) {
            log.error("Invalid mllib model object " + this.mllibModel.getClass().getName() + " due to: " + var10.getMessage() + ". The model class must provide a predict(Vector) method.", var10);
            throw var10;
        }

        long diffMs = System.currentTimeMillis() - var12;
        log.info("Took {} ms to load Spark mllib ClassificationModel of type {}", Long.valueOf(diffMs), this.mllibModel.getClass().getName());
        this.initVectorizationSteps(modelSpecJson);
    }
  }

  public List<String> prediction(Object[] tuple) throws Exception {
  }




}

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

            long var12 = System.currentTimeMillis();//check to this point

            try {
                FileInputStream fileStream=new FileInputStream(modelDir);
                ObjectInputStream ois=new ObjectInputStream(fileStream);
                idfMap=(HashMap<String,Double>) ois.readObject();//TODO:need to check here, if cannot find such object
            } catch (Exception var10) {
                var10.printStackTrace();
            }

            long diffMs = System.currentTimeMillis() - var12;
            log.info("Took {} ms to load Spark mllib ClassificationModel of type {}", Long.valueOf(diffMs), this.mllibModel.getClass().getName());
            this.initVectorizationSteps(modelSpecJson);
        }
    }

    public List<String> prediction(Object[] tuple) throws Exception {
        //1.transform tuple into a good input Vector
        //2.make a predict function
        //3.feed the input vector into the predict function

    }


    protected Object loadClassificationModel(File modelDir, Map<String, Object> modelSpecJson) throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {
        String modelClassName = (String)modelSpecJson.get("modelClassName");
        if(modelClassName.startsWith("mllib.")) {
            modelClassName = "org.apache.spark." + modelClassName;
        }

        log.info("Loading model class: " + modelClassName);

        Class modelClass;
        try {//check to this point
            modelClass = this.getClass().getClassLoader().loadClass(modelClassName);//TODO:what does this line do?
        } catch (ClassNotFoundException var10) {
            log.error("Failed to load Spark ML Transformer class {} due to: {}", modelClassName, String.valueOf(var10));
            throw var10;
        }
        //to this point, 'modelClass' refers to this class we defined:TfIdfTopTerms TODO
        Method loadMethod;
        try {
            loadMethod = modelClass.getMethod("load", new Class[]{SparkContext.class, String.class});
            //modelClassName decides which class's method we are using
            //And that class must have a method 'load'
            //so actually I can just define a method here, which gets the data from modelDir and makes an instance
        } catch (NoSuchMethodException var9) {
            log.error("Spark model impl {} does provide a static \'load(sc:SparkContext, path:String)\' method!", modelClassName);
            throw var9;
        }
        //to this point, 'loadMethod' refers to method 'loadMethod' of this class. TODO
        log.info("Loading Spark ML Transformer from: " + modelDir.getAbsolutePath());
        //modelDir直到这里才被用到。前面只为了得到一个loadMethod-_-
        try {
            Object mllibModel = loadMethod.invoke((Object)null, new Object[]{this.sparkContext, modelDir.getAbsolutePath()});
            //read load function of Word2Vec.scala

            def load(sc: SparkContext, path: String): Word2VecModel = {
                val dataPath = Loader.dataPath(path)
                val sqlContext = SQLContext.getOrCreate(sc)
                val dataFrame = sqlContext.read.parquet(dataPath)
                // Check schema explicitly since erasure makes it hard to use match-case for checking.
                Loader.checkSchema[Data](dataFrame.schema)
                val dataArray = dataFrame.select("word", "vector").collect()
                val word2VecMap = dataArray.map(i => (i.getString(0), i.getSeq[Float](1).toArray)).toMap
                new Word2VecModel(word2VecMap)
                }

            //modelDir.getAbsolutePath() is path
            //let's see what we do with path
            //Loader.loadMetadata(sc, path)
            //^^^go to the path and find the metadata, return (clazz, version, metadata)
            //val model = SaveLoadV1_0.load(sc, path)
            //^^^
            return mllibModel;
        } catch (IllegalAccessException var11) {
            log.error("Cannot load Spark mllib model {} because the load(sc:SparkContext, path:String) method on {} is not accessible!", this.modelId, modelClassName);
            throw var11;
        } catch (InvocationTargetException var12) {
            Object targetException = var12.getTargetException();
            if(targetException == null) {
                targetException = var12;
            }

            log.error("Cannot load Spark mllib model {} because the load(sc:SparkContext, path:String) method on {} failed due to: {}", new Object[]{this.modelId, modelClassName, String.valueOf(targetException)});
            throw var12;
        }
    }
    




}

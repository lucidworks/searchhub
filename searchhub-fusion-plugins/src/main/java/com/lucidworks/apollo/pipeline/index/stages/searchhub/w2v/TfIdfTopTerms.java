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
    protected Object mllibModel;

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
        //modelSpecJson.modelClassName exists. And it should be able to be casted to "String".

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
            this.mllibModel = this.loadClassificationModel(modelDir, modelSpecJson);//TODO:not quite understand this part

            try {
                this.predictionMethod = this.mllibModel.getClass().getMethod("predict", new Class[]{Vector.class});
                //TODO:看上去好像例子的意思是，路径的位置有一个可以借用的类。这个例子就借用这个类包了一层，实现了接口。
                //TODO:如果找不到可以借用的类，那就要从头到尾自己实现。prediction应该不是问题。关键是mllibModel那部分怎么处理。
                //TODO:应该的流程是，我先创建了这个类，把他包成jar，放到Fusion的path。至此，Fusion可以知道有这个类了。
                //TODO:这个类的state是idf的map。这个类的操作包括一个predict函数，吃进去一个doc，输出tfidf最大的一串term。
                //TODO:然后，我在scala里面，pull出solr里面的数据，train一个这个类的instance。
                //TODO:至此，即使没有放到pipeline里面也可以进行测试：train一个这个类，然后看能不能输出应该的term串。
                //到此为止已经成功一大半了。剩下的就是打包zip文件，放到BLOB里面。再去fusion UI里设置一下MLStage，就差不多了。
                //所以modelDir到底是数据来源，还是数据出口？？我觉得是数据来源！
                //本model关键只要一个map，所以存在modelDir就是这个map数据。本model还要能够以这个map数据为参数construct，
                //那么load的过程很简单，就是把map数据提取出来，构造好这个model的一个instance，然后返回！
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


    protected Object loadClassificationModel(File modelDir, Map<String, Object> modelSpecJson) throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException {
        String modelClassName = (String)modelSpecJson.get("modelClassName");
        if(modelClassName.startsWith("mllib.")) {
            modelClassName = "org.apache.spark." + modelClassName;
        }

        log.info("Loading model class: " + modelClassName);

        Class modelClass;
        try {
            modelClass = this.getClass().getClassLoader().loadClass(modelClassName);//check to this point
        } catch (ClassNotFoundException var10) {
            log.error("Failed to load Spark ML Transformer class {} due to: {}", modelClassName, String.valueOf(var10));
            throw var10;
        }
        //to this point, 'modelClass' refers to this class we defined:TfIdfTopTerms TODO
        Method loadMethod;
        try {
            loadMethod = modelClass.getMethod("load", new Class[]{SparkContext.class, String.class});
            //so this class must have a method 'load'
        } catch (NoSuchMethodException var9) {
            log.error("Spark model impl {} does provide a static \'load(sc:SparkContext, path:String)\' method!", modelClassName);
            throw var9;
        }
        //to this point, 'loadMethod' refers to method 'loadMethod' of this class. TODO
        log.info("Loading Spark ML Transformer from: " + modelDir.getAbsolutePath());
        //modelDir直到这里才被用到。前面只为了得到一个loadMethod-_-
        try {
            Object mllibModel = loadMethod.invoke((Object)null, new Object[]{this.sparkContext, modelDir.getAbsolutePath()});
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

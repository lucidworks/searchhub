package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.testFiles;

import org.apache.spark.mllib.feature.Word2VecModel;
import org.apache.spark.SparkContext;
import org.apache.spark.SparkConf;

import scala.Tuple2;


import org.apache.spark.api.java.*;
import org.apache.spark.SparkConf;
import org.apache.spark.api.java.function.Function;


/**
 * Created by xiaoyehuang on 7/19/16.
 */
public class DeserializeTester {
    public static void main(String[] args) {
        SparkConf sconf=new SparkConf();
        sconf.setMaster("8766").setAppName("GetW2vModel");
        SparkContext sc=SparkContext.getOrCreate(sconf);
        Word2VecModel w2vModel=Word2VecModel.load(sc,"w2vModelData");
        System.out.println(w2vModel.findSynonyms("oozie",5));

        if(w2vModel.wordIndex().contains("oozie")){
            Tuple2<String,Object>[] synonyms=w2vModel.findSynonyms("oozie",2);
        }
        else{
            //words not in data, do nothing
        }
        //iterate over synonyms




    }
}

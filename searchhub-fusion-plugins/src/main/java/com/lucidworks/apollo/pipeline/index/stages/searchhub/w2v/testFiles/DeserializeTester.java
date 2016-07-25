package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.testFiles;

import org.apache.spark.mllib.feature.Word2VecModel;
import org.apache.spark.SparkContext;
import org.apache.spark.SparkConf;
import com.lucidworks.spark.ml.SparkContextAware;

import scala.Tuple2;

import java.net.InetAddress;
import java.net.UnknownHostException;

/**
 * Created by xiaoyehuang on 7/19/16.
 */
public class DeserializeTester {
    public static void main(String[] args) {
        SparkConf sconf=new SparkConf();
        try {
            sconf.setMaster("spark://" + InetAddress.getLocalHost().getHostAddress() + ":8766").setAppName("GetW2vModel");
        } catch (UnknownHostException e){
            System.out.println("cannot get ip");
        }
        SparkContext sc=SparkContext.getOrCreate(sconf);
        Word2VecModel w2vModel=Word2VecModel.load(sc,"modelId/w2vModelData");
        System.out.println(w2vModel.findSynonyms("oozie",5));
        if(w2vModel.wordIndex().contains("oozie")){
            Tuple2<String,Object>[] synonyms=w2vModel.findSynonyms("oozie",2);
            for(Tuple2 tuples: synonyms){
                System.out.println(tuples._1+","+tuples._2);
            }
        }



    }
}

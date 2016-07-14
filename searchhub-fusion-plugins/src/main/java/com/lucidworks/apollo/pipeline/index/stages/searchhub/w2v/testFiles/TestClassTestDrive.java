package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.testFiles;
import java.text.SimpleDateFormat;
import java.util.*;
import java.io.*;
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms;
import com.lucidworks.spark.fusion.FusionMLModelSupport;

class TestClassTestDrive{
    public static void main(String[] args){
        try{
            TfIdfTopTerms tfidf=new TfIdfTopTerms();
            HashMap<String,Object> modelSpecJson=new HashMap<String,Object>();
            List<String> featureList = Arrays.asList("body");
            modelSpecJson.put("featureFields",featureList);
            File idfMap=new File("modelId");
            tfidf.init("tfidfTop",idfMap,modelSpecJson);
            String testString="Overview \tPackage \tClass \tUse \t Tree \tDeprecated \tIndex \tHelp   PREV   NEXT\tFRAMES    NO FRAMES     All Classes Hierarchy For Package org.apache.oozie Package Hierarchies: All Packages Class Hierarchy java.lang.Object\torg.apache.oozie.BuildInfo Enum Hierarchy java.lang.Object\tjava.lang.Enum (implements java.lang.Comparable, java.io.Serializable) org.apache.oozie.AppType Overview";
            Object[] input=new Object[1];
            input[0]=testString;
            System.out.println(tfidf.prediction(input));

            //File modelDir = new File("modelId");
            //System.out.println(modelDir.isDirectory());
            //System.out.println(modelDir.getAbsolutePath());

            File modelDir = new File("modelId");
            String modelData=modelDir.getAbsolutePath()+"/tryToAddIdfMap";

            System.out.println(modelData);


        } catch(Exception ex){
            ex.printStackTrace();
        }
    }

}
package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.testFiles;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.*;
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms;
import java.util.List;
import java.util.Arrays;

class TestClassTestDrive{
    public static void main(String[] args){
        try{
            TfIdfTopTerms tfidf=new TfIdfTopTerms();
            HashMap<String,Object> modelSpecJson=new HashMap<String,Object>();
            List<String> featureList = Arrays.asList("body");
            modelSpecJson.put("featureFields",featureList);
            tfidf.init("tfidfTop",new File("tryToAddIdfMap"),modelSpecJson);
            String testString="Overview \tPackage \tClass \tUse \t Tree \tDeprecated \tIndex \tHelp   PREV   NEXT\tFRAMES    NO FRAMES     All Classes Hierarchy For Package org.apache.oozie Package Hierarchies: All Packages Class Hierarchy java.lang.Object\torg.apache.oozie.BuildInfo Enum Hierarchy java.lang.Object\tjava.lang.Enum (implements java.lang.Comparable, java.io.Serializable) org.apache.oozie.AppType Overview";
            Object[] input=new Object[1];
            input[0]=testString;
            System.out.println(tfidf.prediction(input));

        } catch(Exception ex){
            ex.printStackTrace();
        }
    }
}

package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.testFiles;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.io.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms;
import com.lucidworks.spark.fusion.FusionMLModelSupport;
import com.lucidworks.spark.fusion.FusionPipelineClient;
import org.apache.commons.compress.archivers.ArchiveException;
import org.apache.commons.compress.archivers.ArchiveOutputStream;
import org.apache.commons.compress.archivers.ArchiveStreamFactory;
import org.apache.commons.compress.archivers.zip.ZipArchiveEntry;
import org.apache.commons.compress.utils.IOUtils;
import org.apache.commons.io.FileUtils;
import org.apache.http.client.methods.HttpPut;

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

            File modelDir = new File("modelId");

            LinkedHashMap modelJson = new LinkedHashMap();
            modelJson.put("featureFields", featureList);
            modelJson.put("modelClassName","com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms");
            modelJson.put("className","com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms");

            File modelJsonFile1 = new File(modelDir, "spark-ml" + ".json");//TODO:to check whether mllib is a good name
            File modelJsonFile2 = new File(modelDir, "com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms" + ".json");//TODO:to check whether mllib is a good name
            OutputStreamWriter osw1 = null;
            OutputStreamWriter osw2 = null;
            try {
                ObjectMapper om = new ObjectMapper();
                osw1 = new OutputStreamWriter(new FileOutputStream(modelJsonFile1), StandardCharsets.UTF_8);
                om.writeValue(osw1, modelJson);
                osw2 = new OutputStreamWriter(new FileOutputStream(modelJsonFile2), StandardCharsets.UTF_8);
                om.writeValue(osw2, modelJson);

            } finally {
                if(osw1 != null) {
                    try {
                        osw1.flush();
                    } catch (IOException var25) {
                        ;
                    }

                    try {
                        osw1.close();
                    } catch (IOException var24) {
                        ;
                    }
                }
                if(osw2 != null) {
                    try {
                        osw2.flush();
                    } catch (IOException var25) {
                        ;
                    }

                    try {
                        osw2.close();
                    } catch (IOException var24) {
                        ;
                    }
                }

            }

            File zipFile1 = new File("modelId" + ".zip");

            addFilesToZip(modelDir, zipFile1);


            HashMap<String, String> mutableMetadata=new HashMap();
            mutableMetadata.put("abc","def");
            HttpPut putRequest = FusionMLModelSupport.buildPutRequestToFusion("modelId", "localhost:8764", mutableMetadata, zipFile1, "/api/apollo");
            System.out.println(putRequest.getRequestLine());
            System.out.println(putRequest.getURI());
            //FusionPipelineClient fusionClient = new FusionPipelineClient(putRequest.getRequestLine().getUri(), "admin", "password123", "native");
            //fusionClient.sendRequestToFusion(putRequest);


        } catch(Exception ex){
            ex.printStackTrace();
        }


    }


    protected static void addFilesToZip(File source, File destination) throws IOException, ArchiveException {
        FileOutputStream archiveStream = new FileOutputStream(destination);
        ArchiveOutputStream archive = (new ArchiveStreamFactory()).createArchiveOutputStream("zip", archiveStream);
        Collection fileList = FileUtils.listFiles(source, (String[])null, true);
        Iterator i$ = fileList.iterator();

        while(i$.hasNext()) {
            File file = (File)i$.next();
            String entryName = getEntryName(source, file);
            ZipArchiveEntry entry = new ZipArchiveEntry(entryName);
            archive.putArchiveEntry(entry);
            BufferedInputStream input = new BufferedInputStream(new FileInputStream(file));
            IOUtils.copy(input, archive);
            input.close();
            archive.closeArchiveEntry();
        }

        archive.finish();
        archiveStream.close();
    }

    protected static String getEntryName(File source, File file) throws IOException {
        int index = source.getAbsolutePath().length() + 1;
        String path = file.getCanonicalPath();
        return path.substring(index);
    }




}

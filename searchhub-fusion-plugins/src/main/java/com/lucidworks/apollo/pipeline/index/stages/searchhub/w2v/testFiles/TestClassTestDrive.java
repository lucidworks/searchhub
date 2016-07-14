package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.testFiles;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;
import java.io.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms;
import com.lucidworks.spark.fusion.FusionMLModelSupport;
import org.apache.commons.compress.archivers.ArchiveException;
import org.apache.commons.compress.archivers.ArchiveOutputStream;
import org.apache.commons.compress.archivers.ArchiveStreamFactory;
import org.apache.commons.compress.archivers.zip.ZipArchiveEntry;
import org.apache.commons.compress.utils.IOUtils;
import org.apache.commons.io.FileUtils;

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

            LinkedHashMap modelJson = new LinkedHashMap();
            modelJson.put("featureFields", featureList);
            File modelJsonFile1 = new File(modelDir, "mllib" + ".json");//TODO:to check whether mllib is a good name
            OutputStreamWriter osw1 = null;

            try {
                ObjectMapper om = new ObjectMapper();


                osw1 = new OutputStreamWriter(new FileOutputStream(modelJsonFile1), StandardCharsets.UTF_8);
                om.writeValue(osw1, modelJson);
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

            }

            File zipFile1 = new File("modelId" + ".zip");
            if(zipFile1.isFile()) {
                zipFile1.delete();
            }

            addFilesToZip(modelDir, zipFile1);


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

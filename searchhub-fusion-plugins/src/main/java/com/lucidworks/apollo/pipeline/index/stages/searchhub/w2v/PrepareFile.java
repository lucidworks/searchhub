package com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.compress.archivers.ArchiveException;
import org.apache.commons.compress.archivers.ArchiveOutputStream;
import org.apache.commons.compress.archivers.ArchiveStreamFactory;
import org.apache.commons.compress.archivers.zip.ZipArchiveEntry;
import org.apache.commons.compress.utils.IOUtils;
import org.apache.commons.io.FileUtils;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * This file will be called in w2v's scheduled job:FUSION_HOME/python/fusion_config/w2v_job.json
 * It assumes directory 'modelId' is already at the current directory.
 * What it does is to create the json file in the directory, and then pack all the 'modelId' into a zip file
 */
public class PrepareFile {
    public static void createZipFile(){
        try{
            List<String> featureList = Arrays.asList("body");//featureList which will be added into json
            File modelDir = new File("modelId");
            LinkedHashMap modelJson = new LinkedHashMap();
            modelJson.put("featureFields", featureList);
            modelJson.put("modelClassName","com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.W2VRelatedTerms");

            File modelJsonFile = new File(modelDir, "com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.W2VRelatedTerms" + ".json");
            OutputStreamWriter osw = null;
            try {
                ObjectMapper om = new ObjectMapper();
                osw = new OutputStreamWriter(new FileOutputStream(modelJsonFile), StandardCharsets.UTF_8);
                om.writeValue(osw, modelJson);

            } finally {
                if(osw != null) {
                    try {
                        osw.flush();
                    } catch (IOException e) {
                        ;
                    }

                    try {
                        osw.close();
                    } catch (IOException e) {
                        ;
                    }
                }

            }

            File zipFile = new File("modelId" + ".zip");//make a zip file

            addFilesToZip(modelDir, zipFile);//zip all the files under the directory modelDir

        } catch(Exception ex){
            ex.printStackTrace();
        }
    }

    //the following two functions are copied from com.lucidworks.spark.fusion.FusionMLModelSupport
    //they are protected so cannot be just imported
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

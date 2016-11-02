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

import com.lucidworks.spark.fusion.*;
import org.apache.log4j.Logger;

import org.apache.http.HttpEntity;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.EntityBuilder;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.ContentType;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
import org.apache.log4j.Logger;
import org.apache.spark.SparkContext;
import org.apache.spark.ml.util.MLWritable;
import org.apache.spark.mllib.util.Saveable;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URLEncoder;
import java.text.SimpleDateFormat;

/**
 * This file will be called in w2v's scheduled job:FUSION_HOME/python/fusion_config/w2v_job.json
 * It assumes directory 'modelId' is already at the current directory.
 * What it does is to create the json file in the directory, and then pack all the 'modelId' into a zip file
 */
public class PrepareFileModified {

    public static Logger logger = Logger.getLogger(PrepareFileModified.class);

    public static void createZipAndSendFile(){

        logger.info("In the create zip and send file");
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

            System.out.println("Done creating the appropriate zip file");

            HashMap<String, String> modelType = new HashMap();
            modelType.put("modelType", "com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.W2VRelatedTerms");

            HttpPut putRequest = FusionMLModelSupport.buildPutRequestToFusion("relatedTermModel", "localhost:8764", modelType, zipFile, "/api/apollo");
            System.out.println("Created put request successfully");

            FusionPipelineClient fusionClient = new FusionPipelineClient(putRequest.getRequestLine().getUri(), "admin", "vishalak1964", "native");
            System.out.println("Created client successfully");

            // Add these parameters for versions of fusion 3.0.0 and above
            // HttpEntity entity = null;

            try {
                // Add for 3.0.0 and up
                // entity = fusionClient.sendRequestToFusion(putRequest)
                fusionClient.sendRequestToFusion(putRequest);
                System.out.println("Created entity successfully");

            } catch (Exception e){
                System.out.print("Building request failed ");
                e.printStackTrace();
            }

            // Add for 3.0.0 and up 
            //if (entity != null) {
            //    try {
            //      EntityUtils.consume(entity);
            //    } catch (Exception ignore) {
            //      System.out.println("Failed to consume entity due to: "+ ignore);
            //    }
            //}
        } catch(Exception ex){
            ex.printStackTrace();
        }

    }

    public static HttpPut buildPutRequestToFusionInPrep(String modelId,
                                                String fusionHostAndPort,
                                                HashMap<String,String> mutableMetadata,
                                                File zipFile,
                                                String fusionApiPath)
          throws Exception{
        // convert metadata into query string parameters for the PUT request to Fusion
        List<NameValuePair> pairs = new ArrayList<>();
        for (Map.Entry<String,String> entry : mutableMetadata.entrySet()) {
          pairs.add(new BasicNameValuePair(entry.getKey(), URLEncoder.encode(entry.getValue(), "UTF-8")));
        }

        String[] pair = fusionHostAndPort.split(":");
        String fusionHost = fusionHostAndPort;
        int fusionPort = 8764;
        if (pair.length == 2) {
          fusionHost = pair[0];
          fusionPort = Integer.parseInt(pair[1]);
        }

        URIBuilder builder = new URIBuilder();
        builder.setScheme("http").setHost(fusionHost).setPort(fusionPort).setPath(fusionApiPath+"/blobs/"+modelId)
                .setParameters(pairs);
        HttpPut putRequest = new HttpPut(builder.build());
        putRequest.setHeader("Content-Type", "application/zip");

        EntityBuilder entityBuilder = EntityBuilder.create();
        entityBuilder.setContentType(ContentType.create("application/zip"));
        entityBuilder.setFile(zipFile);
        putRequest.setEntity(entityBuilder.build());

        return putRequest;
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

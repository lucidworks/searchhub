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
 * Created by xiaoyehuang on 8/3/16.
 */
public class PrepareFile {
    //assume files 'idfMapData' and 'w2vModelData' are already at the current directory
    public static void createZipFile(){
        try{
            List<String> featureList = Arrays.asList("body");//featureList which will be added into json
            File modelDir = new File("modelId");
            LinkedHashMap modelJson = new LinkedHashMap();
            modelJson.put("featureFields", featureList);
            modelJson.put("modelClassName","com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms");

            File modelJsonFile = new File(modelDir, "com.lucidworks.apollo.pipeline.index.stages.searchhub.w2v.TfIdfTopTerms" + ".json");
            OutputStreamWriter osw = null;
            try {
                ObjectMapper om = new ObjectMapper();
                osw = new OutputStreamWriter(new FileOutputStream(modelJsonFile), StandardCharsets.UTF_8);
                om.writeValue(osw, modelJson);

            } finally {
                if(osw != null) {
                    try {
                        osw.flush();
                    } catch (IOException var25) {
                        ;
                    }

                    try {
                        osw.close();
                    } catch (IOException var24) {
                        ;
                    }
                }

            }

            File zipFile1 = new File("modelId" + ".zip");//make a zip file

            addFilesToZip(modelDir, zipFile1);//zip all the files under the directory modelDir

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

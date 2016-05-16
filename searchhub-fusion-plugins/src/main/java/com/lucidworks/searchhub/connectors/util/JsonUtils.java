package com.lucidworks.searchhub.connectors.util;


import java.io.File;
import java.io.FileReader;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

public class JsonUtils {

  /**
   * Returns the JSON text contents of a file as a JSON array object
   *
   * @param fileName - Name of file containing JSON text for a JSON array object
   *
   * @return JSONObject - the JSON array object value for the text contents
   * @throws Exception
   */
  public static JSONArray readJsonArrayFile(String fileName) throws Exception {
    return readJsonArrayFile(new File(fileName));
  }

  /**
   * Returns the JSON text contents of a file as a JSON array object
   *
   * @param file - File for a file containing JSON text for a JSON array object
   *
   * @return JSONArray - the JSON array object value for the text contents
   * @throws Exception
   */
  public static JSONArray readJsonArrayFile(File file) throws Exception {
    return new JSONArray(new JSONTokener(new FileReader(file)));
  }

  /**
   * Returns the JSON text contents of a file as a JSON object
   *
   * @param fileName - Name of file containing JSON text for a JSON object
   *
   * @return JSONObject - the JSON object value for the text contents
   * @throws Exception
   */
  public static JSONObject readJsonFile(String fileName) throws Exception {
    return readJsonFile(new File(fileName));
  }

  /**
   * Returns the JSON text contents of a file as a JSON object
   *
   * @param file - File for a file containing JSON text for a JSON object
   *
   * @return JSONObject - the JSON object value for the text contents
   * @throws Exception
   */
  public static JSONObject readJsonFile(File file) throws Exception {
    return new JSONObject(new JSONTokener(new FileReader(file)));
  }
}

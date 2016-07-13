import java.util.HashMap;
import java.io.*;

class TestClassTestDrive{
    public static void main(String[] args){
        /*
        HashMap<String, Double> testMap=new HashMap<String, Double>();
        testMap.put("xiaoye",3.5);
        //save this hashmap to a file
        try{
            FileOutputStream fs=new FileOutputStream("classState");
            ObjectOutputStream os=new ObjectOutputStream(fs);
            os.writeObject(testMap);
            os.close();
        } catch(Exception ex){
            ex.printStackTrace();
        }
        */
        //get the hashmap back from the file

        try{
            HashMap<String, Double> testMap=new HashMap<String, Double>();
            BufferedReader br=new BufferedReader(new FileReader("tryToAddIdfMap"));
            String line=null;
            while ((line=br.readLine())!=null){
                String[] splittedLine=line.split(",");
                testMap.put(splittedLine[0],Double.parseDouble(splittedLine[1]));
            }
            System.out.println(testMap);

        } catch(Exception ex){
            ex.printStackTrace();
        }
    }
}

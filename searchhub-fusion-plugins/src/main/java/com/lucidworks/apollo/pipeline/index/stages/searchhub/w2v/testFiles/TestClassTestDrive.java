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
            FileInputStream fileStream=new FileInputStream("out");
            ObjectInputStream ois=new ObjectInputStream(fileStream);
            HashMap<Integer,String> outputMap=(HashMap<Integer,String>) ois.readObject();//TODO:need to check here, if cannot find such object
            TestClass t=new TestClass(outputMap);
            t.checkMap();
        } catch(Exception ex){
            ex.printStackTrace();
        }
    }
}

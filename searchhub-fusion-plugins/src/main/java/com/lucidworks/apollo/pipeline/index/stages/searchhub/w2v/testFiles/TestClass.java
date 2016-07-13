import java.util.HashMap;
class TestClass{
    private HashMap<String,Double> idf;
    public TestClass(HashMap<String,Double> mapIdf){
        idf=mapIdf;
    }
    void checkMap(){
        System.out.println(idf);
    }
}

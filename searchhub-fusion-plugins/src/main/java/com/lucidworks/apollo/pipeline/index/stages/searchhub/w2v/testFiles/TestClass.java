import java.util.HashMap;
class TestClass{
    private HashMap<Integer,String> idf;
    public TestClass(HashMap<Integer,String> mapIdf){
        idf=mapIdf;
    }
    void checkMap(){
        System.out.println(idf);
    }
}

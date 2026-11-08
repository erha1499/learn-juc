public class SizeMain {
    static class Point { int x; }
    static class Mixed { boolean flag; int x; long y; Object ref; }
    public static void main(String[] a) {
        System.out.println("new Object()  = " + SizeAgent.inst.getObjectSize(new Object()));
        System.out.println("new Point()   = " + SizeAgent.inst.getObjectSize(new Point()));
        System.out.println("new Mixed()   = " + SizeAgent.inst.getObjectSize(new Mixed()));
        System.out.println("new int[0]    = " + SizeAgent.inst.getObjectSize(new int[0]));
        System.out.println("new int[3]    = " + SizeAgent.inst.getObjectSize(new int[3]));
        System.out.println("Integer       = " + SizeAgent.inst.getObjectSize(Integer.valueOf(1000)));
    }
}

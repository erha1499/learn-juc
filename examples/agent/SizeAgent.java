import java.lang.instrument.Instrumentation;
public class SizeAgent {
    public static Instrumentation inst;
    public static void premain(String a, Instrumentation i) { inst = i; }
}

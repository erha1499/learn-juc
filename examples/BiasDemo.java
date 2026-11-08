import sun.misc.Unsafe;
import java.lang.reflect.Field;
public class BiasDemo {
    public static void main(String[] args) throws Exception {
        Field f = Unsafe.class.getDeclaredField("theUnsafe"); f.setAccessible(true);
        Unsafe U = (Unsafe) f.get(null);
        Object o = new Object();
        System.out.printf("new:        %016x%n", U.getLong(o, 0L));
        synchronized (o) { System.out.printf("locked:     %016x%n", U.getLong(o, 0L)); }
        System.out.printf("released:   %016x%n", U.getLong(o, 0L));
        o.hashCode();
        System.out.printf("hashCode:   %016x%n", U.getLong(o, 0L));
    }
}

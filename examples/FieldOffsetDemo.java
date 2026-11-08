import sun.misc.Unsafe;
import java.lang.reflect.Field;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 用 Unsafe 查看字段在对象里的偏移量（手册 1.5 节对象布局、4.2 节 valueOffset）。
 * JDK 17、64 位 HotSpot、默认开启压缩指针时的实测输出：
 *   Mixed.flag @ 24, Mixed.x @ 12, Mixed.y @ 16, Mixed.ref @ 28
 *   AtomicInteger.value @ 12
 */
public class FieldOffsetDemo {
    static class Mixed { boolean flag; int x; long y; Object ref; }

    public static void main(String[] args) throws Exception {
        Field f = Unsafe.class.getDeclaredField("theUnsafe");
        f.setAccessible(true);
        Unsafe u = (Unsafe) f.get(null);
        for (String name : new String[]{"flag", "x", "y", "ref"}) {
            System.out.println("Mixed." + name + " @ " + u.objectFieldOffset(Mixed.class.getDeclaredField(name)));
        }
        System.out.println("AtomicInteger.value @ " + u.objectFieldOffset(AtomicInteger.class.getDeclaredField("value")));
    }
}

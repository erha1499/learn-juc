import sun.misc.Unsafe;
import java.lang.reflect.Field;

public class MarkWordDemo {
    static class Point { int x; }

    private static final Unsafe U = getUnsafe();

    // 读对象开头的 8 个字节，就是 Mark Word（64 位 HotSpot）
    static String mark(Object o) {
        long m = U.getLong(o, 0L);
        String bits = String.format("%64s", Long.toBinaryString(m)).replace(' ', '0');
        String lock;
        switch ((int) (m & 0b11)) {
            case 0b01: lock = (m & 0b100) != 0 ? "偏向锁" : "无锁"; break;
            case 0b00: lock = "轻量级锁"; break;
            case 0b10: lock = "重量级锁"; break;
            default:   lock = "GC 标记";
        }
        return String.format("0x%016x  末三位 %s → %s", m, bits.substring(61), lock);
    }

    public static void main(String[] args) throws Exception {
        // ① 对象头有多大：看第一个字段从第几个字节开始
        System.out.println("Point.x 的偏移量 = " + U.objectFieldOffset(Point.class.getDeclaredField("x")));
        System.out.println("int[] 第一个元素的偏移量 = " + U.arrayBaseOffset(int[].class));

        // ② Mark Word 随锁状态变化
        Object o = new Object();
        System.out.println("1. 刚 new 出来      " + mark(o));

        int h = o.hashCode();
        long hashInMark = (U.getLong(o, 0L) >>> 8) & 0x7FFFFFFFL;
        System.out.println("2. 调用 hashCode 后  " + mark(o));
        System.out.printf("   hashCode() = 0x%x，Mark Word 第 8~38 位 = 0x%x%n", h, hashInMark);

        synchronized (o) {
            System.out.println("3. 单线程加锁中      " + mark(o));
        }
        System.out.println("4. 释放锁后          " + mark(o));

        Thread holder = new Thread(() -> {
            synchronized (o) { sleep(500); }
        });
        Thread contender = new Thread(() -> {
            synchronized (o) { }
        });
        holder.start();
        Thread.sleep(100);
        contender.start();
        Thread.sleep(100);
        System.out.println("5. 另一线程在抢锁    " + mark(o) + "（抢锁线程状态：" + contender.getState() + "）");
        holder.join();
        contender.join();

        Object p = new Object();
        synchronized (p) {
            System.out.println("6. 新对象加锁        " + mark(p));
            p.wait(10);
            System.out.println("7. 同一线程 wait 后  " + mark(p));
        }
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) { }
    }

    private static Unsafe getUnsafe() {
        try {
            Field f = Unsafe.class.getDeclaredField("theUnsafe");
            f.setAccessible(true);
            return (Unsafe) f.get(null);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}

public class OddEven {
    private static final Object LOCK = new Object();
    private static int num = 1;
    private static final int MAX = 100;

    public static void main(String[] args) {
        new Thread(() -> print(1), "odd").start();   // 余数 1 打印奇数
        new Thread(() -> print(0), "even").start();  // 余数 0 打印偶数
    }

    private static void print(int remainder) {
        synchronized (LOCK) {
            while (num <= MAX) {
                if (num % 2 == remainder) {
                    System.out.println(Thread.currentThread().getName() + ": " + num++);
                    LOCK.notify();                 // 只有两个线程，notify 足够
                } else {
                    try { LOCK.wait(); } catch (InterruptedException e) { return; }
                }
            }
            LOCK.notify();                         // 退出前叫醒对方，否则它会一直 wait
        }
    }
}

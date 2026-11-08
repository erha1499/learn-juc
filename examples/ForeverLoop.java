public class ForeverLoop {
    static volatile boolean stop = false;            // 加上 volatile 后循环就能停下

    public static void main(String[] args) throws InterruptedException {
        new Thread(() -> {
            try { Thread.sleep(100); } catch (InterruptedException ignored) {}
            stop = true;
            System.out.println("已把 stop 改为 true");
        }).start();

        int i = 0;
        while (!stop) {                     // JIT 优化后可能变成 while (true)
            i++;
        }
        System.out.println("循环结束，i = " + i);
    }
}

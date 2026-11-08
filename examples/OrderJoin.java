public class OrderJoin {
    public static void main(String[] args) {
        Thread t1 = new Thread(() -> System.out.println("t1"));
        Thread t2 = new Thread(() -> {
            try { t1.join(); } catch (InterruptedException e) { return; }   // 等 t1 结束
            System.out.println("t2");
        });
        Thread t3 = new Thread(() -> {
            try { t2.join(); } catch (InterruptedException e) { return; }   // 等 t2 结束
            System.out.println("t3");
        });
        t3.start(); t2.start(); t1.start();   // 启动顺序打乱，输出仍是 t1 t2 t3
    }
}

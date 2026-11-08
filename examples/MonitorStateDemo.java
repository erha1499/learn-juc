public class MonitorStateDemo {
    static final Object lock = new Object();

    public static void main(String[] args) throws Exception {
        Thread waiter = new Thread(() -> {
            synchronized (lock) {
                try { lock.wait(); } catch (InterruptedException ignored) { }  // 进 WaitSet，并释放锁
                System.out.println("waiter 被唤醒并重新拿到了锁");
            }
        }, "waiter");

        Thread owner = new Thread(() -> {
            synchronized (lock) {
                sleep(3000);        // 拿着锁睡觉：sleep 不释放锁
                lock.notify();      // 把 waiter 从 WaitSet 挪到 EntryList
                sleep(3000);        // 仍然拿着锁
            }
        }, "owner");

        Thread blocked = new Thread(() -> {
            synchronized (lock) { }  // 抢不到锁，进 EntryList
        }, "blocked");

        waiter.start();  Thread.sleep(100);
        owner.start();   Thread.sleep(100);
        blocked.start(); Thread.sleep(300);
        System.out.println("阶段一  owner=" + owner.getState()
                + "  blocked=" + blocked.getState() + "  waiter=" + waiter.getState());

        Thread.sleep(3000);  // 此时 owner 已经 notify，但还没释放锁
        System.out.println("阶段二  owner=" + owner.getState()
                + "  blocked=" + blocked.getState() + "  waiter=" + waiter.getState());

        owner.join(); blocked.join(); waiter.join();
    }

    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) { }
    }
}

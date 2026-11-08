import java.util.concurrent.*;

public class WaitForThree {
    public static void main(String[] args) throws Exception {
        // 方式一：CountDownLatch
        CountDownLatch latch = new CountDownLatch(3);
        for (int i = 1; i <= 3; i++) {
            final int id = i;
            new Thread(() -> {
                try { System.out.println("worker " + id + " done"); }
                finally { latch.countDown(); }
            }).start();
        }
        latch.await();
        System.out.println("latch: all done");

        // 方式二：CompletableFuture.allOf
        ExecutorService pool = Executors.newFixedThreadPool(3);
        CompletableFuture<?>[] fs = new CompletableFuture<?>[3];
        for (int i = 0; i < 3; i++) {
            final int id = i + 1;
            fs[i] = CompletableFuture.runAsync(() -> System.out.println("task " + id), pool);
        }
        CompletableFuture.allOf(fs).join();
        System.out.println("allOf: all done");
        pool.shutdown();
    }
}

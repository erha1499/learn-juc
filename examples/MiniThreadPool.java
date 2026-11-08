import java.util.*;
import java.util.concurrent.*;

public class MiniThreadPool {
    private final BlockingQueue<Runnable> queue;
    private final List<Worker> workers = new ArrayList<>();
    private volatile boolean running = true;

    public MiniThreadPool(int size, int queueCapacity) {
        queue = new ArrayBlockingQueue<>(queueCapacity);
        for (int i = 0; i < size; i++) {
            Worker w = new Worker("mini-pool-" + i);
            workers.add(w);
            w.start();
        }
    }

    public void execute(Runnable task) {
        if (!running) throw new IllegalStateException("pool is shut down");
        if (!queue.offer(task)) {                  // 队列满了，拒绝策略：抛异常
            throw new RejectedExecutionException("queue is full");
        }
    }

    public void shutdown() {
        running = false;
        for (Worker w : workers) w.interrupt();    // 叫醒阻塞在 take 上的线程
    }

    private class Worker extends Thread {
        Worker(String name) { super(name); }
        @Override public void run() {
            // 线程复用：循环从队列取任务；关闭后把剩余任务做完再退出
            while (running || !queue.isEmpty()) {
                try {
                    Runnable task = queue.poll(100, TimeUnit.MILLISECONDS);
                    if (task != null) task.run();
                } catch (InterruptedException e) {
                    // 被 shutdown 中断，回到循环判断是否退出
                } catch (RuntimeException e) {
                    e.printStackTrace();           // 任务异常不能让 Worker 死掉
                }
            }
        }
    }

    public static void main(String[] args) throws InterruptedException {
        MiniThreadPool pool = new MiniThreadPool(2, 10);
        for (int i = 1; i <= 5; i++) {
            final int id = i;
            pool.execute(() -> System.out.println(Thread.currentThread().getName() + " run task " + id));
        }
        Thread.sleep(300);
        pool.shutdown();
    }
}

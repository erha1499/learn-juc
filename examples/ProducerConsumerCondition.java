import java.util.concurrent.locks.*;

public class ProducerConsumerCondition {
    static class BoundedBuffer<T> {
        private final Object[] items;
        private int putIdx, takeIdx, count;
        private final ReentrantLock lock = new ReentrantLock();
        private final Condition notFull = lock.newCondition();
        private final Condition notEmpty = lock.newCondition();
        BoundedBuffer(int capacity) { items = new Object[capacity]; }

        public void put(T x) throws InterruptedException {
            lock.lock();
            try {
                while (count == items.length) notFull.await();
                items[putIdx] = x;
                putIdx = (putIdx + 1) % items.length;
                count++;
                notEmpty.signal();                 // 只叫醒消费者
            } finally { lock.unlock(); }
        }

        @SuppressWarnings("unchecked")
        public T take() throws InterruptedException {
            lock.lock();
            try {
                while (count == 0) notEmpty.await();
                T x = (T) items[takeIdx];
                items[takeIdx] = null;
                takeIdx = (takeIdx + 1) % items.length;
                count--;
                notFull.signal();                  // 只叫醒生产者
                return x;
            } finally { lock.unlock(); }
        }
    }

    public static void main(String[] args) throws InterruptedException {
        BoundedBuffer<Integer> buf = new BoundedBuffer<>(2);
        Thread p = new Thread(() -> { try { for (int i = 1; i <= 6; i++) buf.put(i); } catch (InterruptedException ignored) {} });
        Thread c = new Thread(() -> { try { for (int i = 1; i <= 6; i++) System.out.print(buf.take() + " "); } catch (InterruptedException ignored) {} });
        p.start(); c.start(); p.join(); c.join();
        System.out.println();
    }
}

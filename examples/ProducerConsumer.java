import java.util.LinkedList;
import java.util.Queue;

public class ProducerConsumer {
    static class BoundedBuffer<T> {
        private final Queue<T> queue = new LinkedList<>();
        private final int capacity;
        BoundedBuffer(int capacity) { this.capacity = capacity; }

        public synchronized void put(T item) throws InterruptedException {
            while (queue.size() == capacity) {     // 满了，生产者等
                wait();
            }
            queue.offer(item);
            notifyAll();                           // 叫醒消费者
        }

        public synchronized T take() throws InterruptedException {
            while (queue.isEmpty()) {              // 空了，消费者等
                wait();
            }
            T item = queue.poll();
            notifyAll();                           // 叫醒生产者
            return item;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        BoundedBuffer<Integer> buf = new BoundedBuffer<>(3);
        Thread p = new Thread(() -> {
            try { for (int i = 1; i <= 10; i++) { buf.put(i); System.out.println("put " + i); } }
            catch (InterruptedException ignored) {}
        });
        Thread c = new Thread(() -> {
            try { for (int i = 1; i <= 10; i++) System.out.println("take " + buf.take()); }
            catch (InterruptedException ignored) {}
        });
        p.start(); c.start(); p.join(); c.join();
    }
}

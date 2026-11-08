public class SyncBytecode {
    private final Object lock = new Object();
    private int count;

    public void block() {
        synchronized (lock) {
            count++;
        }
    }

    public synchronized void method() {
        count++;
    }
}

import java.util.concurrent.locks.*;

public class PrintABCCondition {
    private static final ReentrantLock lock = new ReentrantLock();
    private static final Condition[] conds = {lock.newCondition(), lock.newCondition(), lock.newCondition()};
    private static int state = 0;
    private static final int TIMES = 10;

    public static void main(String[] args) {
        for (int i = 0; i < 3; i++) {
            final int id = i;
            new Thread(() -> print((char) ('A' + id), id)).start();
        }
    }

    private static void print(char ch, int id) {
        for (int i = 0; i < TIMES; i++) {
            lock.lock();
            try {
                while (state != id) {
                    conds[id].await();             // 在自己的条件队列上等
                }
                System.out.print(ch);
                state = (id + 1) % 3;
                conds[state].signal();             // 只叫醒下一个，精准唤醒
            } catch (InterruptedException e) {
                return;
            } finally {
                lock.unlock();
            }
        }
    }
}

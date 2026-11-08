import java.util.concurrent.Semaphore;

public class PrintABCSemaphore {
    private static final Semaphore sA = new Semaphore(1);  // A 先走
    private static final Semaphore sB = new Semaphore(0);
    private static final Semaphore sC = new Semaphore(0);
    private static final int TIMES = 10;

    public static void main(String[] args) {
        new Thread(() -> print('A', sA, sB)).start();
        new Thread(() -> print('B', sB, sC)).start();
        new Thread(() -> print('C', sC, sA)).start();
    }

    private static void print(char ch, Semaphore mine, Semaphore next) {
        for (int i = 0; i < TIMES; i++) {
            try {
                mine.acquire();                    // 拿到自己的许可才能打印
                System.out.print(ch);
                next.release();                    // 把许可交给下一个
            } catch (InterruptedException e) {
                return;
            }
        }
    }
}

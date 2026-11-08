import java.util.concurrent.locks.LockSupport;

public class PrintABCPark {
    private static Thread tA, tB, tC;
    private static volatile int state = 0;
    private static final int TIMES = 10;

    public static void main(String[] args) {
        tA = new Thread(() -> print('A', 0, () -> tB));
        tB = new Thread(() -> print('B', 1, () -> tC));
        tC = new Thread(() -> print('C', 2, () -> tA));
        tA.start(); tB.start(); tC.start();
    }

    private static void print(char ch, int myTurn, java.util.function.Supplier<Thread> next) {
        for (int i = 0; i < TIMES; i++) {
            while (state != myTurn) {
                LockSupport.park();                // 没轮到就睡；被 unpark 或虚假唤醒后重新检查
            }
            System.out.print(ch);
            state = (myTurn + 1) % 3;              // volatile 写，下一个线程一定能看到
            LockSupport.unpark(next.get());        // 先 unpark 后 park 也不会丢
        }
    }
}

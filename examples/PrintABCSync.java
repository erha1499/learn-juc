public class PrintABCSync {
    private static final Object LOCK = new Object();
    private static int state = 0;          // 0 该 A，1 该 B，2 该 C
    private static final int TIMES = 10;

    public static void main(String[] args) {
        new Thread(() -> print('A', 0)).start();
        new Thread(() -> print('B', 1)).start();
        new Thread(() -> print('C', 2)).start();
    }

    private static void print(char ch, int myTurn) {
        for (int i = 0; i < TIMES; i++) {
            synchronized (LOCK) {
                while (state != myTurn) {          // 用 while 防止虚假唤醒
                    try { LOCK.wait(); } catch (InterruptedException e) { return; }
                }
                System.out.print(ch);
                state = (state + 1) % 3;
                LOCK.notifyAll();                  // 必须 notifyAll，notify 可能叫醒错的线程
            }
        }
    }
}

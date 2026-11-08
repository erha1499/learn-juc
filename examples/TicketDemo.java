public class TicketDemo {
    private int tickets = 10000;

    public void sell() {                    // 改成 synchronized void sell() 就不会多卖
        if (tickets > 0) {
            tickets--;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        TicketDemo demo = new TicketDemo();
        Thread[] ts = new Thread[4];
        for (int i = 0; i < 4; i++) {
            ts[i] = new Thread(() -> { for (int j = 0; j < 5000; j++) demo.sell(); });
            ts[i].start();
        }
        for (Thread t : ts) t.join();
        System.out.println("剩余票数：" + demo.tickets + "（正确应为 0）");
    }
}

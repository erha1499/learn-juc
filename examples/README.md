# 示例代码

手册里引用的全部示例，都在 JDK 17（64 位 HotSpot）上编译运行过。每个文件都是独立的类，没有包名，进入本目录后直接编译运行：

```bash
cd examples
javac -encoding UTF-8 MarkWordDemo.java
java MarkWordDemo
```

用到 `sun.misc.Unsafe` 的程序编译时会提示“内部专用 API”，可以忽略。

## 底层观察（单元一到三）

| 文件 | 对应章节 | 看什么 |
| --- | --- | --- |
| `ForeverLoop.java` | 2.0 | `stop` 不加 volatile 时循环停不下来，加上后立刻结束 |
| `TicketDemo.java` | 2.0 | 4 个线程卖票，余票对不上，而且每次结果不一样 |
| `MonitorStateDemo.java` | 1.5 | 三个线程分别待在 Owner、EntryList、WaitSet；运行期间用 `jstack <进程号>` 看线程栈 |
| `SyncBytecode.java` | 3.2 | 用 `javap -c -v SyncBytecode` 查看 `monitorenter`、两个 `monitorexit` 和异常表 |
| `MarkWordDemo.java` | 3.3 | 读出对象头的 64 位，看无锁、轻量级锁、重量级锁的比特变化 |
| `BiasDemo.java` | 3.3 | 偏向锁的 Mark Word。需要加参数运行：`java -XX:+UseBiasedLocking -XX:BiasedLockingStartupDelay=0 BiasDemo`（JDK 15 到 17 可用，JDK 18 起参数已移除） |
| `FieldOffsetDemo.java` | 1.5、4.2 | 字段在对象里的偏移量，以及 `AtomicInteger.value` 的偏移量 12 |
| `agent/` | 1.5 | 用 `Instrumentation.getObjectSize` 测对象大小，运行方法见下 |

`agent/` 需要先打成 Java Agent：

```bash
cd examples/agent
javac SizeAgent.java SizeMain.java
printf "Premain-Class: SizeAgent\n" > manifest.txt
jar cfm agent.jar manifest.txt SizeAgent.class
java -javaagent:agent.jar SizeMain
```

## 手写题（单元十一）

| 文件 | 对应章节 | 内容 |
| --- | --- | --- |
| `PrintABCSync.java` | 11.1 | 三个线程循环打印 ABC：synchronized + wait/notifyAll |
| `PrintABCCondition.java` | 11.1 | ReentrantLock + 多个 Condition 精准唤醒 |
| `PrintABCSemaphore.java` | 11.1 | 三个 Semaphore 接力 |
| `PrintABCPark.java` | 11.1 | LockSupport.park / unpark |
| `OddEven.java` | 11.2 | 两个线程交替打印 1 到 100 |
| `ProducerConsumer.java` | 11.3 | 生产者-消费者：synchronized + wait/notifyAll |
| `ProducerConsumerCondition.java` | 11.3 | 生产者-消费者：ReentrantLock + 两个 Condition |
| `WaitForThree.java` | 11.4 | 三个线程都执行完，第四个再执行（CountDownLatch 等写法） |
| `OrderJoin.java` | 11.4 | 打乱启动顺序，仍按 T1、T2、T3 的顺序执行 |
| `MiniThreadPool.java` | 11.5 | 手写一个简易线程池：阻塞队列 + Worker 循环取任务 |

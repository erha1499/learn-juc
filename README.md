# learn-juc

用“看得见”的方式学 Java 并发（JUC）。

**在线阅读**：[交互学习手册](https://erha1499.github.io/learn-juc/) · [可视化实验室](https://erha1499.github.io/learn-juc/lab/index.html) · [完整文字版](content/handbook.md)

这是一份按单元组织的 Java 并发学习手册，配有可以一步一步执行的交互演示：高亮的代码行是这一步正在执行的代码，旁边是这一刻对象头、CPU 缓存、等待队列里发生的变化。并发问题大多发生在“两个线程交错执行的那一刻”，只读文字很难在脑子里还原，所以关键机制都尽量做成能动手的演示。

目标是理解原理，而不是背题。文中的结论尽量附上可运行的代码和真实输出，示例都在 JDK 17 上实际跑过。

## 怎么读

| 入口 | 内容 | 状态 |
| --- | --- | --- |
| [交互学习手册](https://erha1499.github.io/learn-juc/)（`docs/index.html`） | 完整正文 + 嵌入式演示 + 可展开的面试回答 + 带答案的自测题 | 单元一到三已完成，含 14 个演示 |
| [可视化实验室](https://erha1499.github.io/learn-juc/lab/index.html)（`docs/lab/index.html`） | 5 个独立实验：count++ 竞态、CPU 缓存可见性、synchronized 与 Monitor、AQS 排队、线程池模拟器 | 可用 |
| [完整文字版](content/handbook.md)（`content/handbook.md`） | 11 个单元的全部正文，GitHub 上可直接阅读 | 完成 |

网站由 GitHub Pages 从 `main` 分支的 `/docs` 目录发布，推送后一两分钟自动更新。它是纯静态网页，克隆仓库后直接用浏览器打开 `docs/index.html` 也能离线看（字体从 Google Fonts 加载，离线时会退回系统字体）。

## 学习路线

| 单元 | 主题 | 一句话 | 交互版 |
| --- | --- | --- | --- |
| 一 | 线程基础 | Java 线程就是内核线程；排队、等待和唤醒都发生在对象的 monitor 上 | 已迁移 |
| 二 | JMM 与 volatile | 写进了自己的缓存，不等于别人看得见 | 已迁移 |
| 三 | synchronized | 锁记在对象头里，能不进内核就不进内核 | 已迁移 |
| 四 | CAS 与原子类 | 先比较再交换，失败了就重来 | 文字版 |
| 五 | AQS | AQS 只管排队，抢锁的规则交给子类 | 文字版 + 实验室 |
| 六 | 基于 AQS 的同步器 | 换一种 state 的算法，就是一个新的同步器 | 文字版 + 实验室 |
| 七 | 线程池 | 先核心，再排队，排满了加线程，线程满了就拒绝 | 文字版 + 实验室 |
| 八 | CompletableFuture | 别干等结果，先登记结果出来后要做什么 | 文字版 |
| 九 | ThreadLocal | 数据挂在线程身上，ThreadLocal 只是钥匙 | 文字版 |
| 十 | 并发容器与死锁 | 锁越细并发越高，加锁顺序一乱就会死锁 | 文字版 |
| 十一 | 手写实操题 | 没轮到就等，干完改状态并叫醒别人 | 文字版 |

每个单元按同一个节奏组织：先看现象（能复现的代码和真实结果），再讲原理，然后动手操作演示，最后用“面试这样说”和自测题检验。

## 仓库结构

```text
content/     正文和数据，文字内容只改这里
  handbook.md    完整手册（11 个单元），交互版的正文也从这里生成
  answers.json   自测题答案（键是题目原文）
  img/           文字版用到的配图
site/        网页源码
  build.py           构建脚本：把 handbook.md 转成交互网页，并插入演示
  course.shell.html  交互手册的页面框架、样式和全部演示代码
  lab.html           可视化实验室
docs/        构建产物，用浏览器直接打开，或用 GitHub Pages 发布（不要手改）
examples/    文中所有可运行的示例代码，见 examples/README.md
```

## 修改与构建

只依赖 Python 3 标准库：

```bash
python3 site/build.py
```

改了 `content/` 或 `site/` 下的文件后运行一次，会重新生成 `docs/index.html` 和 `docs/lab/index.html`。

把一个新单元迁移到交互版，大致是四步：

1. 在 `site/build.py` 末尾的单元列表和 `MOTTO`、`CN` 里加上这个单元。
2. 在 `RULES` 里登记演示要插在正文的哪一段之后（按段落开头文字匹配）。
3. 在 `site/course.shell.html` 里实现演示，并注册到 `LABS`。
4. 在 `content/answers.json` 里补上这个单元自测题的答案。

## 内容维护

正文只有一个来源：`content/handbook.md`。其他地方都是从它单向生成或同步的副本，不要在副本里直接修改。

| 副本 | 怎么更新 |
| --- | --- |
| 在线网站（`docs/`） | 运行 `python3 site/build.py`，提交并推送到 `main`，GitHub Pages 自动发布 |
| 飞书文档（可选） | 运行 `FEISHU_DOC=<飞书文档链接或 token> python3 scripts/sync_feishu.py`，整篇覆盖。需要已登录的飞书命令行工具 `lark-cli`；加 `--dry-run` 只生成转换结果，不上传 |

## 示例代码

`examples/` 里是手册中引用的全部示例，包括循环打印 ABC 的四种写法、生产者消费者、手写线程池，以及用 `Unsafe` 打印 Mark Word、用 jstack 观察 Monitor 区域、用 `javap` 查看 `monitorenter` 的演示程序。运行方法见 [examples/README.md](examples/README.md)。

## 内容来源

手册以下列资料为线索重新组织和改写，并补充了原理解释、交互演示和实测代码：

- [小林coding · Java 并发面试题](https://xiaolincoding.com/interview/juc.html)
- [JavaGuide · Java 并发常见面试题总结（上）](https://javaguide.cn/java/concurrent/java-concurrent-questions-01.html)
- [JavaGuide · Java 并发常见面试题总结（中）](https://javaguide.cn/java/concurrent/java-concurrent-questions-02.html)
- [JavaGuide · Java 并发常见面试题总结（下）](https://javaguide.cn/java/concurrent/java-concurrent-questions-03.html)

## 路线图

- [x] 单元一到三的交互版（14 个嵌入式演示）
- [ ] 单元四到六迁移：CAS 自旋、AQS 排队、Semaphore / CountDownLatch
- [ ] 单元七到十一迁移：线程池、CompletableFuture、ThreadLocal、并发容器与死锁、手写题
- [ ] 新演示：ThreadLocal 引用链与 GC、ABC 打印的 Condition 精准唤醒、死锁的环形等待

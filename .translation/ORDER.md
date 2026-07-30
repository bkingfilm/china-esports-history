# 翻译排班真源

这个目录是机器维护的翻译排班文件，不是书的内容。读者请看 [docs/zh](../docs/zh/index.md) 与 [docs/en](../docs/en/index.md)。

## 为什么真源在仓库里而不在某台机器上

翻译由定时任务执行，可能同时跑在多台机器上。任何写在单机本地文件里的「队列状态」都会两边不一致，导致同一章翻两遍。所以：

**真源是文件系统本身，不是任何一张台账。** 某章有没有翻过，看对应语言目录里有没有它的译文文件，而不是查表。台账（`海外推广计划.md` 里的队列表）降级为给人看的进度快照，回填失败不影响排班正确性。

## 章节号是主键

判定某章是否已翻，用**章节号前缀**匹配，不比对文件名其余部分（中文名和拼音名不可能机械对应）：

| 中文原文 | 译文位置 | 已翻判定 |
| --- | --- | --- |
| `docs/zh/chapters/NN-*.md` | `docs/<lang>/NN-*.md` | 该语言目录根下有 `NN-` 开头的文件 |
| `docs/zh/gamehistory/NN-*.md` | `docs/<lang>/gamehistory/NN-*.md` | 该语言的 gamehistory 子目录下有 `NN-` 开头的文件 |
| `docs/zh/appendix/NN-*.md` | `docs/<lang>/appendix/NN-*.md` | 该语言的 appendix 子目录下有 `NN-` 开头的文件 |

`chapters/` 的译文平铺在语言目录根下（沿用已入库的 8 篇的位置，不迁移）。`gamehistory/` 与 `appendix/` 的译文放同名子目录，**图片相对路径要多退一层**：子目录里是 `../../assets/`，语言目录根下是 `../assets/`。

## 无编号章节的文件名写死在这里

这几篇没有章节号，两台机器各自起名会撞。名字定死，不许另起：

| 中文原文 | 译文文件名 |
| --- | --- |
| `chapters/序章-TEDx演讲-让路更多一些.md` | `one-more-way-tedx-2015.md` |
| `chapters/00-自序.md` | `00-authors-preface.md` |
| `chapters/当事人篇-NeoTV前总经理熊剑明Neo亲述.md` | `witness-xiong-jianming-neotv.md` |
| `chapters/番外-三言两语说电竞.md` | `extra-a-few-words-on-esports.md` |
| `chapters/番外-刀工与大厨.md` | `extra-knife-skills-and-the-chef.md` |
| `gamehistory/00-前言.md` | `gamehistory/00-foreword.md` |
| `gamehistory/番外-波士顿棒球记.md` | `gamehistory/extra-boston-baseball.md` |

其余章节的译文文件名用拼音短横线式，模板 `13-matianyuan-sichuan-vanguard.md`：章节号 + 主角拼音 + 一句英文短标识。

## 英文（docs/en/）取章顺序

优先段翻完后，按后面的通则取。

1. `chapters/38-Razer创始人兼CEO-Min`
2. `chapters/15-贫民窟走出的电竞百万富翁-孟阳`
3. `chapters/25-左手会跳舞的男人-suhO`
4. `chapters/26-抗韩英雄-MagicYang`
5. `chapters/31-从剑舞红颜笑-到-IG.xiaoxiao`
6. `chapters/18-从俱乐部到联盟的演变`
7. `chapters/23-I-Rocks大韩-豁出来的人生传奇`
8. `chapters/01-从星际争霸说起`

通则：优先段清空后，先把 `chapters/` 里剩下的按章节号升序翻完（无编号的四篇排在编号章之后），再 `gamehistory/`，最后 `appendix/`。

已入库 8 篇：序章 TEDx、13、22、24、30、33、37、39。

## 韩语（docs/ko/）取章顺序

选韩语的依据是内容交集：全书至少六章有韩国主线（WEG 首尔联赛与 CJ Media 20 亿韩元、WCG 2001 与 2005 首尔、决赛胜 Project_kr、抗韩英雄、李晓峰 Sky、星际争霸）。**先翻已被校对人核过的章节**，史实已核一遍，且能拿 reviewed 英文加中文双向对照。

1. `chapters/24-当李晓峰成为SKY`（已 reviewed，韩语圈认知度最高）
2. `chapters/13-川军先锋-马天元`（已 reviewed，WCG 2001 首尔夺冠）
3. `chapters/序章-TEDx演讲-让路更多一些`（已 reviewed）
4. `chapters/37-格斗天王-小孩曾卓君`（已 reviewed）
5. `chapters/30-世界级中国CS指挥官-Alex卞正伟`（WEG 首尔，决赛胜 Project_kr）
6. `chapters/26-抗韩英雄-MagicYang`
7. `chapters/39-星际老男孩的不老青春`（星际共鸣最强）
8. `chapters/01-从星际争霸说起`

通则同英文。韩语的表记与文体规则在翻译班任务文件里，不在这里。

## 改顺序改这个文件

插队请求（GitHub Issue 里 `[EN]` 或 `[KO]` 开头的 Issue）优先于本表，由翻译班当班判断。要长期调整顺序，改这个文件即可，两台机器下次开工自动生效，不需要碰任何机器的本地配置。

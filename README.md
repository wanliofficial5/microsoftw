# E-Ink UI

## 介绍
这是一个由python编写，基于树莓派Zero W的水墨屏天气时钟。
这个仓库是対原仓库[eink-clock-mP](https://gitee.com/fu1fan/eink-clock-mP)的重构，提高了运行效率和代码规范。

目前仍在开发中。

## 各分支简介
### master
主分支，可以直接在树莓派zero w上运行。
### develop
开发分支，内含由@[xuanzhi33](https://gitee.com/xuanzhi33) 开发的**水墨屏模拟器**，可以直接在电脑上运行。
### web
web分支与Master分支都可以直接在树莓派zero w上运行，但有所不同。虽然主程序仍然使用Python编写，但是在UI层面采用了HTML+js开发，所以采用了chromium内核。原本以为树莓派zero w跑不动chromium，但是尝试了之后感觉体验还挺好，就开了个新分支。因为使用HTML+js开发界面比纯python写要简单（反正我是这么认为的），而且可以直接在电脑浏览器上调试，所以开发效率和调试效率都大大提升了。不足之处也是显而易见的，那就是开机会有点慢（与master分支相比慢了约13s），占用内存会有一点大，但是还是可以接受的。

## 运行

### 有树莓派zero w和微雪水墨屏

在树莓派zero w上克隆本仓库，安装相应依赖后，运行：
```
sudo python3 main.py
```
### 没有相应硬件

在电脑上克隆本仓库并切换到**develop**分支，安装相应依赖后，运行：
```
sudo python3 main.py
```
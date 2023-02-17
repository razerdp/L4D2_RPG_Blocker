# L4D2_RPG_Blocker
针对RPG服务器的火绒json生成软件

## 原理

跟游戏内openbrowser一样，扫描全区（本工程指定为亚洲）服务器。

根据用户配置的关键字和匹配精准度去模糊匹配每一个服务器名字，大于该匹配值的服务器会被标记并输出。

最后导出符合火绒IP黑名单的规则Json，导入火绒IP黑名单即可生效。

## 软件下载

请看[release](https://github.com/razerdp/L4D2_RPG_Blocker/releases)
其中exe是打好包的程序,json是软件包打出来后扫2000个服务器得到的规则文件，可以直接使用。

### 软件使用须知

由于pyinstaller打包很大，因此用upx进行压缩，部分杀软可能会报毒（加壳）

如果您实在不放心，可以下载源码自行编译

## 环境要求

python版本 >= 3.7

需要安装以下库：

  * pip3 install PyQt5
  * pip3 install PySide2
  * pip3 install steam
  * pip3 install python-a2s
  * pip3 install pyinstaller
  * pip3 install qasync
  * pip3 install asyncio
  * pip3 install qdarkstyle
  * pip3 install fuzzywuzzy[speedup]
  
## 打包须知

请使用以下指令，防止本工程文件没有进包

pyinstaller -F -w main.py -p $PROJECT_PATH --noconsole -n L4D2火绒屏蔽IP扫描生成器

* $PROJECT_PATH填入本工程根目录的路径

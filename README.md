# 更新记录 

## 2021-01-18
1. 在原作者的基础上, 写死了购物车结算按钮的x, y坐标, 不同的电脑分辨率不同, mac推荐使用(myPoint Coordinates), windows自行百度
   所有的坐标均是以chrome全屏展开为准

2. 修复了每隔60s刷新购物车防止掉线的时间戳取值错误问题

3. 修改了chromedriver中$cdc标识, 以绕过淘宝检测

4. 启用原作者的最后一条说明绕过淘宝检测:
   在完成3的基础上
   设置监听地址, 本地终端手动启动chrome浏览器, 代码接入,  并修改了chromedriver中 $cdc参数防止淘宝检测
   终端运行 /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222      
   (mac中chrome安装地址, windows找到chrome安装地址, 后缀参数保持不变, 启用这条命令前确保chrome完全退出状态!!!)
   终端执行后,会唤起chrome, 地址栏可以输入127.0.0.1:9200/json查看, 若能正常加载出插件信息则说明成功!

具体修改$cdc标识的方法参考  https://blog.csdn.net/taojian_/article/details/97758632 这位老哥的
此修改仅为个人学习兴趣


以下为原作者的说明：

# taobao_seckill
淘宝、天猫半价抢购，抢电视、抢茅台，干死黄牛党
## 依赖
### 安装chrome浏览器，根据浏览器的版本找到对应的[chromedriver](http://npm.taobao.org/mirrors/chromedriver/)

## 使用说明
1、抢购前需要校准本地时间，然后把需要抢购的商品加入购物车  
2、如果要打包成可执行文件，可使用pyinstaller自行打包  
3、不需要打包的，直接在项目根目录下 执行 python3 main.py  
4、程序运行后，会打开淘宝登陆页，需要自己手动点击切换到扫码登陆  

## 淘宝有针对selenium的检测，如果遇到验证码说明被反爬了，遇到这种情况应该换一个方案，凡是用到selenium的都会严重依赖网速、电脑配置。
## 如果想直接绕过淘宝的检测，可以手动打开浏览器登陆淘宝，然后再用selenium接管浏览器。只提供思路，具体实现大佬们可以自己摸索。


#!/usr/bin/env python3
# encoding=utf-8
import os
import platform
import time
from time import sleep
from random import choice
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import seckill.settings as utils_settings
from utils.utils import get_useragent_data

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import global_config

import pyautogui
pyautogui.PAUSE = 0.5


# 抢购失败最大次数
max_retry_count = 10


def default_chrome_path():

    driver_dir = getattr(utils_settings, "DRIVER_DIR", None)
    if platform.system() == "Windows":
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver.exe"))

        raise Exception("The chromedriver drive path attribute is not found.")
    else:
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver"))

        raise Exception("The chromedriver drive path attribute is not found.")


class ChromeDrive:
    def __init__(self, chrome_path=default_chrome_path(), seckill_time=None, password=None):
        self.chrome_path = chrome_path
        self.seckill_time = seckill_time
        self.seckill_time_obj = datetime.strptime(self.seckill_time, '%Y-%m-%d %H:%M:%S')
        self.password = password

    def start_driver(self):
        try:
            driver = self.find_chromedriver()
        except WebDriverException:
            print("Unable to find chromedriver, Please check the drive path.")
        else:
            return driver

    def find_chromedriver(self):
        try:
            driver = webdriver.Chrome(executable_path=global_config.get('config', 'chromePath'), options=self.build_chrome_options())

        except WebDriverException:
            try:
                driver = webdriver.Chrome(options=self.build_chrome_options(), executable_path=self.chrome_path, chrome_options=self.build_chrome_options())

            except WebDriverException:
                raise

        # 设置全屏浏览器
        driver.maximize_window()
        return driver

    def build_chrome_options(self):
        """配置启动项"""
        chrome_options = webdriver.ChromeOptions()
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium - 20210105实验证明对于阿里淘宝来说没用，一样被识别出来了
        # 设置监听地址, 本地启动chrome浏览器, 代码接入,  并修改了chromedriver中 $cdc参数防止淘宝检测
        # 终端运行 /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222      (mac地址, windows找到chrome安装地址)
        chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')

        return chrome_options

    def _login(self, login_url: str="https://login.taobao.com/member/login.jhtml"):
        if login_url:
            self.driver = self.start_driver()
        else:
            print("Please input the login url.")
            raise Exception("Please input the login url.")
        while True:
            self.driver.get(login_url)
            try:
                user = self.driver.find_element_by_id("fm-login-id")
                user.clear()
                user.send_keys(global_config.get('secret', 'username'))
                password = self.driver.find_element_by_id("fm-login-password")
                password.clear()
                password.send_keys(global_config.get('secret', 'pwd'))
                butt = self.driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/button')
                butt.click()
                time.sleep(0.5)
                element = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_SiteNavMytaobao"]/div[1]/a/span')))
                if element:
                    print("登陆成功")
                    break
                else:
                    print("登陆失败, 刷新重试, 请尽快登陆!!!")
                    continue
            except Exception as e:
                print(str(e))
                continue

    def keep_wait(self):
        self._login()
        print("等待到点抢购...")
        while True:
            current_time = time.mktime(datetime.now().timetuple())
            start_time = time.mktime(self.seckill_time_obj.timetuple())
            # 此处修判断
            if (start_time - current_time) > 120:
                self.driver.get("https://cart.taobao.com/cart.htm")
                print("每分钟刷新一次界面，防止登录超时...")
                sleep(60)
            else:
                print("抢购时间点将近，停止自动刷新，准备进入抢购阶段...")
                break


    def sec_kill(self):
        self.keep_wait()
        self.driver.get("https://cart.taobao.com/cart.htm")
        sleep(1)

        if self.driver.find_element_by_id("J_SelectAll1"):
            self.driver.find_element_by_id("J_SelectAll1").click()
            print("已经选中全部商品！！！")

        submit_succ = False
        retry_count = 0

        while True:
            if retry_count != 0:    # 重试进入后,需要再次全选
                if self.driver.find_element_by_id("J_SelectAll1"):
                    self.driver.find_element_by_id("J_SelectAll1").click()
                    print("已经选中全部商品！！！")

            now = datetime.now()
            if now >= self.seckill_time_obj:
                print(f"开始抢购, 尝试次数： {str(retry_count)}")
                retry_count = retry_count + 1
                if submit_succ:
                    print("订单已经提交成功，无需继续抢购...")
                    break
                if retry_count > max_retry_count:
                    print("重试抢购次数达到上限，放弃重试...")
                    break
                if not retry_count:  # 首次抢购时间稍微延后0.8秒,  设置开始时间一般为正式开始发售的前1s
                    sleep(0.8)
                print(datetime.now())
                try:
                    # 坐标写死从配置文件读取
                    width = pyautogui.size().width
                    height = pyautogui.size().height
                    x = global_config.get('config', 'xCoor')
                    y = global_config.get('config', 'yCoor')
                    print(f"屏幕宽高为：({width},{height})")
                    print(f"结算按钮坐标为：({x},{y})")
                    # 移动鼠标到指定坐标，方便定位
                    pyautogui.moveTo(x, y)
                    pyautogui.leftClick(x, y)
                    print("已经点击结算按钮...")
                    self.driver.find_element_by_link_text('提交订单').click()
                    print("已经点击提交订单按钮")
                    submit_succ = True
                except Exception as e:
                    submit_succ = False
                    link = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'mc-menu-hd')))
                    link = link.get_attribute('href')
                    self.driver.get(link)
                    time.sleep(0.1)
                    print("提交失败, 前方拥堵, 重新下单...")
                    continue

            sleep(0.1)
        if submit_succ:
            if self.password:
                self.pay()

    def pay(self):
        try:
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'sixDigitPassword')))
            element.send_keys(self.password)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'J_authSubmit'))).click()
            print("付款成功")
        except:
            print('付款失败')
        finally:
            sleep(60)
            self.driver.quit()

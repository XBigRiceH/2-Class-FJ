# -*- coding: utf-8 -*-
# fuck 2-class

import json
import random
import re
import warnings
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
warnings.filterwarnings('ignore')


class class_2:
    def __init__(self, usr, pwd):
        
        # some const and pls replace it by yourself //TODO
        self.DRIVER_PATH = '/opt/driver/bin/chromedriver'
        self.PATH = ""
        self.GRADE = "%E9%AB%98%E4%BA%8C" # URL ENCODED
        
        self.SID = ""
        self.REQUESTS_TOKEN = ""
        self.USER = usr
        self.PASS = pwd
        self.logs = []
        self.courseIds = []

    # 获取reqtoken+sid
    def get_params(self):
        try:
            cookie_result = requests.get("https://www.2-class.com/courses", verify=False)
            self.REQUESTS_TOKEN = re.findall(r"reqtoken:\"(.+?)\"", cookie_result.text)[0]
            self.SID = re.findall(r"sid=(.+?);", cookie_result.headers["Set-Cookie"])[0]
            self.logs.append("[+] 请求参数已获取")
            return True
        except Exception:
            self.logs.append("[+] 请求参数获取失败")
            return False

    # 获取登录态
    def login(self):
        login_result = requests.post("https://www.2-class.com/api/user/login", verify=False, headers={
            "Connection": "keep-alive",
            "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            "accept": "*/*",
            "Content-Type": "application/json;charset=UTF-8",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua-mobile": "?0",
            "Host": "www.2-class.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
            "sec-ch-ua-platform": '"Windows"',
            "Origin": "https://www.2-class.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.2-class.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": f"sid={self.SID}"
        }, data=json.dumps({
            "account": self.USER,
            "checkCode": "",
            "codeKey": "",
            "nvcVal": "",
            "password": self.PASS,
            "reqtoken": self.REQUESTS_TOKEN
        })).json()
        try:
            if not login_result['data']['result']:
                self.logs.append("[-] 用户名或密码错误")
                return False
        except Exception:
            self.logs.append("[-] 用户名或密码错误")
            return False
        self.logs.append(f"[+] {self.USER} 已登陆")
        return True

    # 获取待做普通题
    def get_courses(self):
        index = 1
        try:
            courses_result = requests.get(
                f"https://www.2-class.com/api/course/getHomepageCourseList?grade=%E9%AB%98%E4%BA%8C&pageSize=96&pageNo={index}",
                headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
                    "Connection": "keep-alive",
                    "Cookie": f"sid={self.SID}",
                    "Host": "www.2-class.com",
                    "Referer": "https://www.2-class.com/api/course",
                    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
                }, verify=False)
            for i in courses_result.json()['data']['list']:
                if i['isFinish']:
                    continue
                self.courseIds.append(i['id'])
            while len(courses_result.json()['data']['list']) == 96:
                index += 1
                courses_result = requests.get(
                    f"https://www.2-class.com/api/course/getHomepageCourseList?grade={self.GRADE}&pageSize=96&pageNo={index}",
                    headers="https://www.2-class.com/api/course", verify=False)
                for i in courses_result.json()['data']['list']:
                    if i['isFinish']:
                        continue
                    self.courseIds.append(i['id'])
            return True
        except Exception:
            self.logs.append("[-] 待做题获取失败")
            return False

    # 完成普通题目
    def complete_task(self, task_id):
        try:
            index = 1
            examCommitReqDataList = []
            info = requests.get(f"https://www.2-class.com/api/exam/getTestPaperList?courseId={task_id}", headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
                "Connection": "keep-alive",
                "Cookie": f"sid={self.SID}",
                "Host": "www.2-class.com",
                "Referer": f"https://www.2-class.com/courses/exams/{task_id}",
                "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
            }, verify=False).json()
            for i in info['data']['testPaperList']:
                examCommitReqDataList.append({"examId": index, "answer": i['answer']})
                index += 1
            return requests.post("https://www.2-class.com/api/exam/commit", verify=False, headers={
                "Connection": "keep-alive",
                "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                "accept": "*/*",
                "Content-Type": "application/json;charset=UTF-8",
                "accept-language": "en-US,en;q=0.9",
                "sec-ch-ua-mobile": "?0",
                "Host": "www.2-class.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
                "sec-ch-ua-platform": '"Windows"',
                "Origin": "https://www.2-class.com",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": f"https://www.2-class.com/courses/exams/{task_id}",
                "Accept-Encoding": "gzip, deflate, br",
                "Cookie": f"sid={self.SID}"
            }, data=json.dumps({
                "courseId": task_id,
                "reqtoken": self.REQUESTS_TOKEN,
                "examCommitReqDataList": examCommitReqDataList
            })).json()['success']
        except Exception:
            return False

    # 期末考试
    def finish_final_exam(self):
        try:
            if not requests.get(
                    "https://www.2-class.com/api/question/isPass",
                    headers={
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
                        "Connection": "keep-alive",
                        "Cookie": f"sid={self.SID}",
                        "Host": "www.2-class.com",
                        "Referer": "https://www.2-class.com/courses",
                        "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
                    }, verify=False).json()['data']:
                self.logs.append("[-] 期末考试还未作答, 开始作答")
                requests.get("https://www.2-class.com/api/question/getQuestionList?queNumber=10", headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
                    "Connection": "keep-alive",
                    "Cookie": f"sid={self.SID}",
                    "Host": "www.2-class.com",
                    "Referer": "https://www.2-class.com/courses/exams/finalExam",
                    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
                }, verify=False)
                result = requests.post("https://www.2-class.com/api/question/commit", verify=False, headers={
                    "Connection": "keep-alive",
                    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    "accept": "*/*",
                    "Content-Type": "application/json;charset=UTF-8",
                    "accept-language": "en-US,en;q=0.9",
                    "sec-ch-ua-mobile": "?0",
                    "Host": "www.2-class.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
                    "sec-ch-ua-platform": '"Windows"',
                    "Origin": "https://www.2-class.com",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://www.2-class.com/courses/exams/finalExam",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Cookie": f"sid={self.SID}"
                }, data=json.dumps({
                    "courseId": "final",
                    "reqtoken": self.REQUESTS_TOKEN,
                    "list": [
                        {"questionId": 677, "questionContent": "A"},
                        {"questionId": 678, "questionContent": "A"},
                        {"questionId": 679, "questionContent": "B"},
                        {"questionId": 680, "questionContent": "D"},
                        {"questionId": 681, "questionContent": "A"},
                        {"questionId": 682, "questionContent": "B"},
                        {"questionId": 683, "questionContent": "A"},
                        {"questionId": 684, "questionContent": "C"},
                        {"questionId": 685, "questionContent": "C"},
                        {"questionId": 686, "questionContent": "A"},
                    ]
                })).json()
                self.logs.append(f"[+] 期末考试已作答 等级 {result['data']['award']}")
            else:
                self.logs.append("[-] 期末考试已作答")
            return True
        except Exception:
            self.logs.append("[-] 期末考试作答失败")
            return False

    # 知识竞赛
    def finish_competition(self):
        try:
            if not requests.get(
                    "https://www.2-class.com/api/quiz/isPass",
                    headers={
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
                        "Connection": "keep-alive",
                        "Cookie": f"sid={self.SID}",
                        "Host": "www.2-class.com",
                        "Referer": "https://www.2-class.com/competition",
                        "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"',
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
                    }, verify=False).json()['data']:
                self.logs.append("[-] 知识竞赛还未作答, 开始作答")
                requests.get("https://www.2-class.com/api/quiz/getQuestionList?gradeType=%E9%AB%98%E4%BA%8C", headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
                    "Connection": "keep-alive",
                    "Cookie": f"sid={self.SID}",
                    "Host": "www.2-class.com",
                    "Referer": "https://www.2-class.com/competition",
                    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
                }, verify=False)
                rTime = str(random.randint(300, 600))
                result = requests.post("https://www.2-class.com/api/quiz/commit", verify=False, headers={
                    "Connection": "keep-alive",
                    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                    "accept": "*/*",
                    "Content-Type": "application/json;charset=UTF-8",
                    "accept-language": "en-US,en;q=0.9",
                    "sec-ch-ua-mobile": "?0",
                    "Host": "www.2-class.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
                    "sec-ch-ua-platform": '"Windows"',
                    "Origin": "https://www.2-class.com",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://www.2-class.com/competition",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Cookie": f"sid={self.SID}"
                }, data=json.dumps({
                    "time": rTime,
                    "reqtoken": self.REQUESTS_TOKEN,
                    "list": [{'questionId': 2915, 'questionContent': 'B'}, {'questionId': 2916, 'questionContent': 'A'},
                             {'questionId': 2949, 'questionContent': 'B'}, {'questionId': 2918, 'questionContent': 'A'},
                             {'questionId': 2888, 'questionContent': 'B'}, {'questionId': 2985, 'questionContent': 'D'},
                             {'questionId': 2889, 'questionContent': 'D'}, {'questionId': 2955, 'questionContent': 'D'},
                             {'questionId': 2958, 'questionContent': 'D'}, {'questionId': 2963, 'questionContent': 'A'},
                             {'questionId': 2964, 'questionContent': 'B'}, {'questionId': 2932, 'questionContent': 'D'},
                             {'questionId': 2965, 'questionContent': 'A'}, {'questionId': 2906, 'questionContent': 'B'},
                             {'questionId': 2939, 'questionContent': 'B'}, {'questionId': 2971, 'questionContent': 'A'},
                             {'questionId': 2941, 'questionContent': 'D'}, {'questionId': 2942, 'questionContent': 'D'},
                             {'questionId': 2944, 'questionContent': 'D'}, {'questionId': 2978, 'questionContent': 'D'}]
                })).json()
                self.logs.append(f"[+] 知识竞赛已作答, 成绩 {result['data']['point']} 分, 随机提交用时 {rTime} 秒")
            else:
                self.logs.append("[-] 知识竞赛已作答")
            return True
        except Exception:
            self.logs.append("[-] 知识竞赛作答失败")
            return False
    # 获取截图
        def get_screenshot(self):
            try:
                options = Options()
                options.add_argument('--no-sandbox')
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                driver = Chrome(executable_path=self.DRIVER_PATH, options=options)
                driver.maximize_window()
                driver.get("https://www.2-class.com/api")
                driver.add_cookie(cookie_dict={"name": "sid", "value": self.SID})
                driver.get("https://www.2-class.com/competition")
                driver.execute_script("document.documentElement.style.overflowY = 'hidden';")
                scroll_width = 1350
                scroll_height = 1080
                driver.set_window_size(scroll_width, scroll_height)
                filename = str(self.USER)
                filename = f"{self.PATH}\\{filename}.png"
                driver.get_screenshot_as_file(filename)
                driver.close()
                driver.quit()
                return filename
            except Exception:
                return None
        
    # 主入口
    def do(self):

        # 获取请求参数
        if not self.get_params():
            return self.logs

        # 获取登录态
        if not self.login():
            return self.logs

        # 处理待做普通题
        if not self.get_courses():
            return self.logs
        if len(self.courseIds) == 0:
            self.logs.append("[-] 没有待做普通题")
        else:
            self.logs.append(f"[+] 检测到 {str(len(self.courseIds))} 个普通练习, id = " + str(self.courseIds))
        for i in self.courseIds:
            success = self.complete_task(i)
            if success:
                self.logs.append(f"[+] 普通练习 {str(i)} 已提交")
            else:
                self.logs.append(f"[+] 普通练习 {str(i)} 提交失败")

        # 处理期末考试
        if not self.finish_final_exam():
            return self.logs

        # 处理知识竞赛
        if not self.finish_competition():
            return self.logs

        return self.logs, self.get_screenshot()

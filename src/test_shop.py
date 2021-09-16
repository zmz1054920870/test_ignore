# -*- coding: UTF-8 -*-
#  __author__ = 'zhy'

import pytest
import allure
import time
import json

from local_lib.API.common.api_login import ApiLogin
from local_lib.API.common.tbp_log import Log, readconfig
from API.tbp_api.问答.shop import ShopQuestionApi, ShopApi
from API.tbp_api.其它.search import SearchApi
from config.globalparam import pro_ini_path
from local_lib.API.common.utils import  dispatch


read = readconfig.ReadConfig(pro_ini_path)
test_comapny = read.getValue('projectConfig', 'test_comapny')
comapny_name_list = [test_comapny]


@allure.feature('店铺问答')
@pytest.mark.shop
class TestShop(object):
    def setup_class(self):
        self.log = Log()
        self.shop_question = ShopQuestionApi()
        self.shop = ShopApi()
        self.search = SearchApi()

    @pytest.mark.parametrize('comapny_name', comapny_name_list)
    @allure.story('新建关键词-问答测试-删除新建关键词')
    @allure.severity('normal')
    def test_is_keyword_question(self, comapny_name):
        """
        用例描述：新建关键词问答测试。
        """
        with allure.step('获取登录地址'):
            self.login = ApiLogin()
            result = self.login.login(company_name=comapny_name)
            self.log.info(result)
            assert result.get('test_code') == 'success'
            headers = result.get("headers")

        with allure.step('新建关键词'):
            result = self.shop_question.shop_question_new(headers=headers, questions=[{"question": "自动化测试"}])
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0
            shop_question_id = result["shop_question"]["id"]

        with allure.step('添加回复'):
            result = self.shop_question.shop_question_edit_replies(headers=headers, qid=shop_question_id,
                                                                   replies='[{"auto_send_in_auto_mode":true,'
                                                                           '"auto_send_in_hybrid_mode":true,'
                                                                           '"answer":"自动化测试回复"}]')
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0

        with allure.step('获取关键词列表，验证是否添加成功'):
            result = self.shop_question.shop_question_list(headers=headers, is_keyword='true', only_show_auto='false')
            self.log.info(result)
            allure.attach('测试结果', str(result))
            assert result.get('test_code') == 'success' and result.get("code") == 0
            assert shop_question_id in str(result)
            for q_list in result["shop_questions"]:
                if q_list["id"] == shop_question_id:
                    assert q_list["replies"][0]["answer"] == "自动化测试回复"
                break

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            spliter = str(int(time.time() * 1000000))
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试，验证机器人是否识别'):
            result = self.search.search2(headers=headers, keyword="自动化测试")
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0
            robot_reply = result.get("robot_reply")
            assert robot_reply

        with allure.step('客户端问答测试'):
            result = dispatch("TBP-01", "send_wangwang_msg", "自动化测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端数据'):
            allure.attach('待检查的消息标识', "自动化测试回复")
            # 休眠一下确保消息未接收到。
            time.sleep(2)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "自动化测试回复" in received_msg

        with allure.step('测试完成，删除测试数据'):
            time.sleep(1)
            result = self.shop_question.shop_question_delete(headers=headers, id=shop_question_id)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0

    @pytest.mark.parametrize('comapny_name', comapny_name_list)
    @allure.story('新建整句-整句测试-删除整句')
    @allure.severity('normal')
    def test_is_keyword_false_question(self, comapny_name):
        """
        用例描述：新建整句问答测试
        """
        with allure.step('获取登录地址'):
            self.login = ApiLogin()
            result = self.login.login(company_name=comapny_name)
            self.log.info(result)
            assert result.get('test_code') == 'success'
            headers = result.get("headers")

        with allure.step('新建整句'):
            result = self.shop_question.shop_question_new(headers=headers, questions=[{"question": "自动化测试整句"}],
                                                          is_keyword='false')
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0
            shop_question_id = result["shop_question"]["id"]

        with allure.step('添加回复'):
            result = self.shop_question.shop_question_edit_replies(headers=headers, qid=shop_question_id,
                                                                   replies='[{"auto_send_in_auto_mode":true,'
                                                                           '"auto_send_in_hybrid_mode":true,'
                                                                           '"answer":"自动化测试整句回复"}]')
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0

        with allure.step('获取关键词列表，验证是否添加成功'):
            result = self.shop_question.shop_question_list(headers=headers, is_keyword='false', only_show_auto='false')
            self.log.info(result)
            allure.attach('测试结果', str(result))
            assert result.get('test_code') == 'success' and result.get("code") == 0
            assert shop_question_id in str(result)
            for q_list in result["shop_questions"]:
                if q_list["id"] == shop_question_id:
                    assert q_list["replies"][0]["answer"] == "自动化测试整句回复"
                break

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            spliter = str(int(time.time() * 1000000))
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('客户端问答测试'):
            result = dispatch("TBP-01", "send_wangwang_msg", "自动化测试整句")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端数据'):
            allure.attach('待检查的消息标识', "自动化测试整句回复")
            # 休眠一下确保消息未接收到。
            time.sleep(2)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "自动化测试整句回复" in received_msg

        with allure.step('问答测试，验证机器人是否识别'):
            result = self.search.search2(headers=headers, keyword="自动化测试整句")
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0
            robot_reply = result.get("robot_reply")
            assert robot_reply

        with allure.step('测试完成，删除测试数据'):
            time.sleep(1)
            result = self.shop_question.shop_question_delete(headers=headers, id=shop_question_id)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get("code") == 0

    @allure.story('获取关键词列表-选取3-5个列表内有回复的关键词测试-关键词测试')
    @allure.severity('normal')
    def test_is_keyword_true_question_list(self):
        """
        用例描述：选取关键词列表内4个问题，进行问答测试。
        选取规则，列表第一页倒数4个的所有问题第一个。有+号的筛选加号
        """
        with allure.step('获取登录地址'):
            self.login = ApiLogin()
            result = self.login.login(company_name=comapny_name_list[0])
            self.log.info(result)
            assert result.get('test_code') == 'success'
            headers = result.get("headers")

        with allure.step('获取关键词列表'):
            result = self.shop_question.shop_question_list(headers=headers, is_keyword='true', only_show_auto='false')
            self.log.info(result)
            allure.attach('测试结果', str(result))
            assert result.get('test_code') == 'success' and result.get("code") == 0

        with allure.step('选取问答测试的问题'):
            q_list = result.get("shop_questions")
            q_list = q_list[-4:]
            question_list = []
            for q in q_list:
                q_ass = q["questions"][0]["question"]
                if "+" in q_ass:
                    q_jia_list = q_ass.split("+")
                    q_jia = ""
                    for q in q_jia_list:
                        q_jia += q
                    question_list.append(q_jia)
                else:
                    question_list.append(q_ass)
            self.log.info(question_list)
            allure.attach('选取的问题', str(question_list))

        with allure.step('问答测试，验证机器人是否识别'):
            sure_num = 0
            for q in question_list:
                result = self.search.search2(headers=headers, keyword=q)
                self.log.info(result)
                robot_reply = result.get("robot_reply")
                if robot_reply and robot_reply != "":
                    sure_num += 1
            if sure_num != len(question_list):
                assert sure_num == len(question_list), '问答测试结果有误,成功次数少于预期。'

    @allure.story('获取整句列表-选取3-5个列表内整句测试-整句测试')
    @allure.severity('normal')
    def test_is_keyword_false_question_list(self):
        """
        用例描述：选取整句列表内4个问题，进行问答测试。
        选取规则，列表第一页倒数4个的所有问题第一个。有+号的筛选加号
        """
        with allure.step('获取登录地址'):
            self.login = ApiLogin()
            result = self.login.login(company_name=comapny_name_list[0])
            self.log.info(result)
            assert result.get('test_code') == 'success'
            headers = result.get("headers")

        with allure.step('获取整句列表'):
            result = self.shop_question.shop_question_list(headers=headers, is_keyword='false', only_show_auto='false')
            self.log.info(result)
            allure.attach('测试结果', str(result))
            assert result.get('test_code') == 'success' and result.get("code") == 0

        with allure.step('选取问答测试的问题'):
            q_list = result.get("shop_questions")
            q_list = q_list[-4:]
            question_list = []
            for q in q_list:
                q_ass = q["questions"][0]["question"]
                if "+" in q_ass:
                    q_jia_list = q_ass.split("+")
                    q_jia = ""
                    for q in q_jia_list:
                        q_jia += q
                    question_list.append(q_jia)
                else:
                    question_list.append(q_ass)
            self.log.info(question_list)
            allure.attach('选取的问题', str(question_list))

        with allure.step('问答测试，验证机器人是否识别'):
            sure_num = 0
            for q in question_list:
                result = self.search.search2(headers=headers, keyword=q)
                self.log.info(result)
                robot_reply = result.get("robot_reply")
                if robot_reply and robot_reply != "":
                    sure_num += 1
            if sure_num != len(question_list):
                assert sure_num == len(question_list), '问答测试结果有误,成功次数少于预期。'


if __name__ == '__main__':
    pytest.main(['-s'])

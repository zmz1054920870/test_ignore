# -*- coding: UTF-8 -*-
#  __author__ = 'zhy'

import pytest
import allure
import time
import json

from conftest import read
from local_lib.API.common.tbp_log import Log
from local_lib.API.common.api_login import ApiLogin
from abandoned.wangwang import WangWangApi
from abandoned.qianniu import QianNiuApi
from API.tbp_api.问答.shop import ShopQuestionApi
from local_lib.API.common.utils import  dispatch

seller = read.getValue('reminder', 'seller')
buyer = read.getValue('reminder', 'buyer')
comapny_name_list = read.getValue('projectConfig', 'test_comapny')
target_url = read.getValue('projectConfig', 'target_url')
if target_url == 'http://wangcai.xiaoduoai.com':
    qid = '5c9c7791b04c18000f08a9fc'
else:
    qid = "5c6ba814bf1f8f205c1e74d2"


@allure.feature('时效标签')
@pytest.mark.ageing
class TestAgeing(object):
    def setup_class(self):
        self.log = Log()
        self.wangwang = WangWangApi()
        self.qianniu = QianNiuApi()
        self.shopq = ShopQuestionApi()

        self.login = ApiLogin()
        global headers
        result = self.login.login(comapny_name_list)
        self.log.info(result)
        assert result.get('test_code') == 'success'
        headers = result.get("headers")

    @allure.story('时效标签')
    @allure.severity('normal')
    def test_ageing_overdue(self):
        """
        用例描述：已过期
        时效标签优先级：固定时段的>单日循环>永久有效的>已过期或未生效的
        """
        spliter = str(int(time.time() * 1000000))
        if target_url == 'http://wangcai.xiaoduoai.com':
            s = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"已过期回复",' \
                '"ageing_id":"5c9c7a69b04c18001208b2f6","sale_statuses":[1,2,3]}]'
        else:
            s = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"已过期回复",' \
                '"ageing_id":"5c6ba7b1bf1f8f205c1e74c8"}]'

        with allure.step('修改固定自定义问题答案'):
            result = self.shopq.shop_question_edit_replies(headers=headers, replies=s, qid=qid)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-时效标签测试'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "时效标签测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("已过期回复"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "已过期回复" not in received_msg
            if "tb671067_2013" in received_msg:
                if "兜底话术" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('时效标签')
    @allure.severity('normal')
    def test_ageing_not_effective(self):
        """
        用例描述：未生效
        时效标签优先级：固定时段的>单日循环>永久有效的>已过期或未生效的
        """
        spliter = str(int(time.time() * 1000000))
        if target_url == 'http://wangcai.xiaoduoai.com':
            s = '[{"auto_send_in_auto_mode":true,"sale_statuses":[1,2,3],"auto_send_in_hybrid_mode":true,' \
                '"answer_trend_stats":[{"date":20190321,"stat":{"hit_order_percent":0}},{"date":20190322,' \
                '"stat":{"hit_order_percent":0}},{"date":20190323,"stat":{"hit_order_percent":0}},{"date":20190324,' \
                '"stat":{"hit_order_percent":0}},{"date":20190325,"stat":{"hit_order_percent":0}},{"date":20190326,' \
                '"stat":{"hit_order_percent":0}},{"date":20190327,"stat":{"hit_order_percent":0}}],' \
                '"answer":"已过期回复","ageing":{"status":-1,"end_time":"2019-01-03 15:40:19.000000",' \
                '"id":"5c9c7a69b04c18001208b2f6","name":"过期","start_time":"2019-01-01 15:40:09.000000",' \
                '"ageing_type":1},"ageing_id":"5c9c7a69b04c18001208b2f6","answer_id":"5c9c7acd4512b70010f93030"},' \
                '{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"未生效回复",' \
                '"ageing_id":"5c9c7a542452f6000f27634d"}]'
        else:
            s = '[{"ageing":{"name":"过期","start_time":"2019-01-01 14:52:24.000000","status":-1,' \
                '"end_time":"2019-01-01 14:52:28.000000","ageing_type":1,"id":"5c6ba7b1bf1f8f205c1e74c8"},' \
                '"answer_id":"5c6bce25bf1f8f205c1e7667","answer":"已过期回复","auto_send_in_hybrid_mode":true,' \
                '"ageing_id":"5c6ba7b1bf1f8f205c1e74c8","auto_send_in_auto_mode":true,"sale_statuses":[1,2,3]},' \
                '{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"未生效回复",' \
                '"ageing_id":"5c6ba7dfbf1f8f205c1e74cc"}]'

        with allure.step('修改固定自定义问题答案'):
            result = self.shopq.shop_question_edit_replies(headers=headers, replies=s, qid=qid)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-时效标签测试'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "时效标签测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("未生效回复"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "未生效回复" not in received_msg
            if "tb671067_2013" in received_msg:
                if "兜底话术" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('时效标签')
    @allure.severity('normal')
    def test_ageing_effective(self):
        """
        用例描述：永久有效的
        时效标签优先级：固定时段的>单日循环>永久有效的>已过期或未生效的
        """
        spliter = str(int(time.time() * 1000000))
        if target_url == 'http://wangcai.xiaoduoai.com':
            s = '[{"auto_send_in_hybrid_mode":true,"sale_statuses":[1,2,3],"ageing":{"name":"过期","status":-1,' \
                '"ageing_type":1,"start_time":"2019-01-01 15:40:09.000000","id":"5c9c7a69b04c18001208b2f6",' \
                '"end_time":"2019-01-03 15:40:19.000000"},"ageing_id":"5c9c7a69b04c18001208b2f6",' \
                '"answer_id":"5c9c7acd4512b70010f93030","answer_trend_stats":[{"date":20190321,' \
                '"stat":{"hit_order_percent":0}},{"date":20190322,"stat":{"hit_order_percent":0}},' \
                '{"date":20190323,"stat":{"hit_order_percent":0}},{"date":20190324,"stat":{"hit_order_percent":0}},' \
                '{"date":20190325,"stat":{"hit_order_percent":0}},{"date":20190326,"stat":{"hit_order_percent":0}},' \
                '{"date":20190327,"stat":{"hit_order_percent":0}}],"answer":"已过期回复","auto_send_in_auto_mode":true},' \
                '{"auto_send_in_hybrid_mode":true,"sale_statuses":[1,2,3],"ageing":{"name":"未生效","status":1,' \
                '"ageing_type":1,"start_time":"2046-03-28 15:39:35.000000","id":"5c9c7a542452f6000f27634d",' \
                '"end_time":"2056-08-03 15:39:52.000000"},"ageing_id":"5c9c7a542452f6000f27634d",' \
                '"answer_id":"5c9c7b432452f6000f276357","answer_trend_stats":[{"date":20190321,' \
                '"stat":{"hit_order_percent":0}},{"date":20190322,"stat":{"hit_order_percent":0}},' \
                '{"date":20190323,"stat":{"hit_order_percent":0}},{"date":20190324,"stat":{"hit_order_percent":0}},' \
                '{"date":20190325,"stat":{"hit_order_percent":0}},{"date":20190326,"stat":{"hit_order_percent":0}},' \
                '{"date":20190327,"stat":{"hit_order_percent":0}}],"answer":"未生效回复","auto_send_in_auto_mode":true},' \
                '{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"永久生效回复","ageing_id":""}]'
        else:
            s = '[{"ageing":{"name":"过期","start_time":"2019-01-01 14:52:24.000000","status":-1,' \
                '"end_time":"2019-01-01 14:52:28.000000","ageing_type":1,"id":"5c6ba7b1bf1f8f205c1e74c8"},' \
                '"answer_id":"5c6bce25bf1f8f205c1e7667","answer":"已过期回复","auto_send_in_hybrid_mode":true,' \
                '"ageing_id":"5c6ba7b1bf1f8f205c1e74c8","auto_send_in_auto_mode":true,"sale_statuses":[1,2,3]},' \
                '{"ageing":{"name":"未生效","start_time":"2026-10-19 14:52:52.000000","status":1,' \
                '"end_time":"2028-02-19 14:53:15.000000","ageing_type":1,"id":"5c6ba7dfbf1f8f205c1e74cc"},' \
                '"answer_id":"5c6bce2dbf1f8f205c1e7669","answer":"未生效回复","auto_send_in_hybrid_mode":true,' \
                '"ageing_id":"5c6ba7dfbf1f8f205c1e74cc","auto_send_in_auto_mode":true,"sale_statuses":[1,2,3]},' \
                '{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"永久生效回复","ageing_id":""}]'

        with allure.step('修改固定自定义问题答案'):
            result = self.shopq.shop_question_edit_replies(headers=headers, replies=s, qid=qid)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-时效标签测试'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "时效标签测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("永久生效回复"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "永久生效回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "永久生效回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('时效标签')
    @allure.severity('normal')
    def test_ageing_loop(self):
        """
        用例描述：单日循环
        时效标签优先级：固定时段的>单日循环>永久有效的>已过期或未生效的
        """
        spliter = str(int(time.time() * 1000000))
        if target_url == 'http://wangcai.xiaoduoai.com':
            s = '[{"sale_statuses":[1,2,3],"auto_send_in_auto_mode":true,"answer_id":"5c9c7acd4512b70010f93030",' \
                '"ageing":{"name":"过期","start_time":"2019-01-01 15:40:09.000000","status":-1,' \
                '"id":"5c9c7a69b04c18001208b2f6","ageing_type":1,"end_time":"2019-01-03 15:40:19.000000"},' \
                '"answer":"已过期回复","auto_send_in_hybrid_mode":true,' \
                '"answer_trend_stats":[{"stat":{"hit_order_percent":0},"date":20190321},' \
                '{"stat":{"hit_order_percent":0},"date":20190322},{"stat":{"hit_order_percent":0},"date":20190323},' \
                '{"stat":{"hit_order_percent":0},"date":20190324},{"stat":{"hit_order_percent":0},"date":20190325},' \
                '{"stat":{"hit_order_percent":0},"date":20190326},{"stat":{"hit_order_percent":0},"date":20190327}],' \
                '"ageing_id":"5c9c7a69b04c18001208b2f6"},{"sale_statuses":[1,2,3],"auto_send_in_auto_mode":true,' \
                '"answer_id":"5c9c7b432452f6000f276357","ageing":{"name":"未生效",' \
                '"start_time":"2046-03-28 15:39:35.000000","status":1,"id":"5c9c7a542452f6000f27634d","ageing_type":1,' \
                '"end_time":"2056-08-03 15:39:52.000000"},"answer":"未生效回复","auto_send_in_hybrid_mode":true,' \
                '"answer_trend_stats":[{"stat":{"hit_order_percent":0},"date":20190321},{"stat":{"hit_order_percent":0},' \
                '"date":20190322},{"stat":{"hit_order_percent":0},"date":20190323},{"stat":{"hit_order_percent":0},' \
                '"date":20190324},{"stat":{"hit_order_percent":0},"date":20190325},{"stat":{"hit_order_percent":0},' \
                '"date":20190326},{"stat":{"hit_order_percent":0},"date":20190327}],' \
                '"ageing_id":"5c9c7a542452f6000f27634d"},{"sale_statuses":[1,2,3],"auto_send_in_auto_mode":true,' \
                '"answer_id":"5c9c7bc2b04c18000f08aa36","answer":"永久生效回复","auto_send_in_hybrid_mode":true,' \
                '"answer_trend_stats":[{"stat":{"hit_order_percent":0},"date":20190321},{"stat":{"hit_order_percent":0},' \
                '"date":20190322},{"stat":{"hit_order_percent":0},"date":20190323},{"stat":{"hit_order_percent":0},' \
                '"date":20190324},{"stat":{"hit_order_percent":0},"date":20190325},{"stat":{"hit_order_percent":0}' \
                ',"date":20190326},{"stat":{"hit_order_percent":0},"date":20190327}],"ageing_id":""},' \
                '{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"单日循环回复",' \
                '"ageing_id":"5c9c7a7d4512b70010f9302b"}]'
        else:
            s = '[{"auto_send_in_auto_mode":true,"answer":"已过期回复","answer_id":"5c6bce25bf1f8f205c1e7667",' \
                '"ageing_id":"5c6ba7b1bf1f8f205c1e74c8","auto_send_in_hybrid_mode":true,"sale_statuses":[1,2,3],' \
                '"ageing":{"ageing_type":1,"name":"过期","status":-1,"start_time":"2019-01-01 14:52:24.000000",' \
                '"id":"5c6ba7b1bf1f8f205c1e74c8","end_time":"2019-01-01 14:52:28.000000"}},' \
                '{"auto_send_in_auto_mode":true,"answer":"未生效回复","answer_id":"5c6bce2dbf1f8f205c1e7669",' \
                '"ageing_id":"5c6ba7dfbf1f8f205c1e74cc","auto_send_in_hybrid_mode":true,"sale_statuses":[1,2,3],' \
                '"ageing":{"ageing_type":1,"name":"未生效","status":1,"start_time":"2026-10-19 14:52:52.000000",' \
                '"id":"5c6ba7dfbf1f8f205c1e74cc","end_time":"2028-02-19 14:53:15.000000"}},' \
                '{"auto_send_in_auto_mode":true,"answer_id":"5c6bce37bf1f8f205c1e766b","ageing_id":"",' \
                '"auto_send_in_hybrid_mode":true,"sale_statuses":[1,2,3],"answer":"永久有效回复"},' \
                '{"auto_send_in_auto_mode":true,"answer":"单日循环回复","answer_id":"5c6bce41bf1f8f205c1e766d",' \
                '"ageing_id":"5c6ba79bbf1f8f205c1e74c5","auto_send_in_hybrid_mode":true,"sale_statuses":[1,2,3],' \
                '"ageing":{"ageing_type":2,"everyday_end_time":"23:59:59","name":"每日重复","status":0,' \
                '"id":"5c6ba79bbf1f8f205c1e74c5","everyday_start_time":"00:00:00"}}]'

        with allure.step('修改固定自定义问题答案'):
            result = self.shopq.shop_question_edit_replies(headers=headers, replies=s, qid=qid)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-时效标签测试'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "时效标签测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("单日循环回复"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "单日循环回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "单日循环回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('时效标签')
    @allure.severity('normal')
    def test_ageing_sure_time(self):
        """
        用例描述：固定时段的
        时效标签优先级：固定时段的>单日循环>永久有效的>已过期或未生效的
        """
        spliter = str(int(time.time() * 1000000))
        if target_url == 'http://wangcai.xiaoduoai.com':
            s = '[{"ageing_id":"5c9c7a69b04c18001208b2f6","auto_send_in_hybrid_mode":true,"answer":"已过期回复",' \
                '"auto_send_in_auto_mode":true,"ageing":{"status":-1,"id":"5c9c7a69b04c18001208b2f6",' \
                '"start_time":"2019-01-01 15:40:09.000000","ageing_type":1,"end_time":"2019-01-03 15:40:19.000000",' \
                '"name":"过期"},"answer_id":"5c9c7acd4512b70010f93030","sale_statuses":[1,2,3],' \
                '"answer_trend_stats":[{"stat":{"hit_order_percent":0},"date":20190321},{"stat":{"hit_order_percent":0}' \
                ',"date":20190322},{"stat":{"hit_order_percent":0},"date":20190323},{"stat":{"hit_order_percent":0},' \
                '"date":20190324},{"stat":{"hit_order_percent":0},"date":20190325},{"stat":{"hit_order_percent":0},' \
                '"date":20190326},{"stat":{"hit_order_percent":0},"date":20190327}]},' \
                '{"ageing_id":"5c9c7a542452f6000f27634d","auto_send_in_hybrid_mode":true,"answer":"未生效回复",' \
                '"auto_send_in_auto_mode":true,"ageing":{"status":1,"id":"5c9c7a542452f6000f27634d",' \
                '"start_time":"2046-03-28 15:39:35.000000","ageing_type":1,"end_time":"2056-08-03 15:39:52.000000",' \
                '"name":"未生效"},"answer_id":"5c9c7b432452f6000f276357","sale_statuses":[1,2,3],' \
                '"answer_trend_stats":[{"stat":{"hit_order_percent":0},"date":20190321},{"stat":{"hit_order_percent":0},' \
                '"date":20190322},{"stat":{"hit_order_percent":0},"date":20190323},{"stat":{"hit_order_percent":0},' \
                '"date":20190324},{"stat":{"hit_order_percent":0},"date":20190325},{"stat":{"hit_order_percent":0},' \
                '"date":20190326},{"stat":{"hit_order_percent":0},"date":20190327}]},{"ageing_id":"",' \
                '"auto_send_in_hybrid_mode":true,"answer":"永久生效回复","auto_send_in_auto_mode":true,' \
                '"answer_id":"5c9c7bc2b04c18000f08aa36","sale_statuses":[1,2,3],' \
                '"answer_trend_stats":[{"stat":{"hit_order_percent":0},"date":20190321},{"stat":{"hit_order_percent":0},' \
                '"date":20190322},{"stat":{"hit_order_percent":0},"date":20190323},{"stat":{"hit_order_percent":0},' \
                '"date":20190324},{"stat":{"hit_order_percent":0},"date":20190325},{"stat":{"hit_order_percent":0},' \
                '"date":20190326},{"stat":{"hit_order_percent":0},"date":20190327}]},{"ageing_id":"5c9c7a7d4512b70010f9302b",' \
                '"auto_send_in_hybrid_mode":true,"answer":"单日循环回复","auto_send_in_auto_mode":true,' \
                '"ageing":{"everyday_end_time":"23:59:59","status":0,"everyday_start_time":"00:00:00",' \
                '"id":"5c9c7a7d4512b70010f9302b","ageing_type":2,"name":"每日重复"},' \
                '"answer_id":"5c9c7c4eb04c18001008aa87","sale_statuses":[1,2,3],' \
                '"answer_trend_stats":[{"stat":{"hit_order_percent":0},"date":20190321},{"stat":{"hit_order_percent":0},' \
                '"date":20190322},{"stat":{"hit_order_percent":0},"date":20190323},{"stat":{"hit_order_percent":0},' \
                '"date":20190324},{"stat":{"hit_order_percent":0},"date":20190325},{"stat":{"hit_order_percent":0},' \
                '"date":20190326},{"stat":{"hit_order_percent":0},"date":20190327}]},{"auto_send_in_auto_mode":true,' \
                '"auto_send_in_hybrid_mode":true,"answer":"固定时段回复","ageing_id":"5c9c7aa098ef410012b0b185"}]'
        else:
            s = '[{"ageing":{"name":"过期","start_time":"2019-01-01 14:52:24.000000","status":-1,' \
                '"end_time":"2019-01-01 14:52:28.000000","ageing_type":1,"id":"5c6ba7b1bf1f8f205c1e74c8"},' \
                '"answer_id":"5c6bce25bf1f8f205c1e7667","answer":"已过期回复","auto_send_in_hybrid_mode":true,' \
                '"ageing_id":"5c6ba7b1bf1f8f205c1e74c8","auto_send_in_auto_mode":true,"sale_statuses":[1,2,3]},' \
                '{"ageing":{"name":"未生效","start_time":"2026-10-19 14:52:52.000000","status":1,' \
                '"end_time":"2028-02-19 14:53:15.000000","ageing_type":1,"id":"5c6ba7dfbf1f8f205c1e74cc"},' \
                '"answer_id":"5c6bce2dbf1f8f205c1e7669","answer":"未生效回复","auto_send_in_hybrid_mode":true,' \
                '"ageing_id":"5c6ba7dfbf1f8f205c1e74cc","auto_send_in_auto_mode":true,"sale_statuses":[1,2,3]},' \
                '{"answer_id":"5c6bce37bf1f8f205c1e766b","answer":"永久有效回复","auto_send_in_hybrid_mode":true,' \
                '"ageing_id":"","auto_send_in_auto_mode":true,"sale_statuses":[1,2,3]},{"ageing":{"name":"每日重复",' \
                '"status":0,"everyday_end_time":"23:59:59","ageing_type":2,"everyday_start_time":"00:00:00",' \
                '"id":"5c6ba79bbf1f8f205c1e74c5"},"answer_id":"5c6bce41bf1f8f205c1e766d","answer":"单日循环",' \
                '"auto_send_in_hybrid_mode":true,"ageing_id":"5c6ba79bbf1f8f205c1e74c5","auto_send_in_auto_mode":true,' \
                '"sale_statuses":[1,2,3]},{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,' \
                '"answer":"固定时段回复","ageing_id":"5c6ba77dbf1f8f205c1e74c3"}]'

        with allure.step('修改固定自定义问题答案'):
            result = self.shopq.shop_question_edit_replies(headers=headers, replies=s, qid=qid)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-时效标签测试'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "时效标签测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("固定时段回复"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "固定时段回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "固定时段回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0


if __name__ == '__main__':
    pytest.main(['-s'])

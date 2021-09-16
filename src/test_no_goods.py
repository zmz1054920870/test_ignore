# -*- coding: UTF-8 -*-
#  __author__ = 'zhy'

import pytest
import allure
import time
import json

from local_lib.API.common import readconfig
from local_lib.API.common.tbp_log import Log
from local_lib.API.common.api_login import ApiLogin
from local_lib.API.tbp_api.问答.question import QuestionApi
from API.tbp_api.问答.shop import ShopApi, ShopQuestionApi
from config.globalparam import read_config
from local_lib.API.common.utils import  refresh_redis, dispatch
from config.globalparam import pro_ini_path


read = readconfig.ReadConfig(pro_ini_path)
target_url = read.getValue('projectConfig', 'target_url')
seller = read_config.getValue('reminder', 'seller')
buyer = read_config.getValue('reminder', 'buyer')
comapny_name_list = read.getValue('projectConfig', 'test_comapny')

if target_url == 'http://wangcai.xiaoduoai.com':
    man_clothes_category_id = '597ea5ea369f99105c6d2d4c'  # 男装专属（VIP版）id
    kitchen_category_id = '5a829b295a9f720c6c02cc15'  # 厨房电器（VIP版）id
else:
    man_clothes_category_id = '597ea5ea369f99105c6d2d4c'  # 男装专属（VIP版）id
    kitchen_category_id = '5a829b7bbf1f8f20bbd9189e'  # 厨房电器（VIP版）id

man_clothes_url = 'https://item.taobao.com/item.htm?id=586766818307'  # 尺码表焦点商品
material_url = "https://item.taobao.com/item.htm?id=586635349110"


@allure.feature('类目特有问题')
@pytest.mark.scene
class TestScene(object):
    def setup_class(self):
        self.log = Log()
        self.shop = ShopApi()
        self.shopq = ShopQuestionApi()
        self.question = QuestionApi()
        self.login = ApiLogin()
        global headers
        result = self.login.login(comapny_name_list)
        self.log.info(result)
        assert result.get('test_code') == 'success'
        headers = result.get("headers")

    @allure.story('关联商品回复')
    @allure.severity('normal')
    def test_question_b_goods_replies_no_same_goods(self):
        """
        用例描述：行业问题-关联商品回复-无焦点商品
        1.切换类目至男装
        2.针对固定的商品，添加商品回复
        3.验证是否添加成功
        4.准备好回复的问题，好的知道了。
        5.验证回复
        6.删除关联商品回复
        """
        spliter = str(int(time.time() * 1000000))

        plat_goods_ids = "586920031576"  # 固定商品id（猫猫）
        question_b_id = '597ea78981a8b207cef3a8e8'  # 固定问题的id
        replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                  '"answer_pics":[]}]'

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            time.sleep(0.5)
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('对好的知道了问题添加关联商品回复'):

            result = self.question.question_b_goods_replies_new_multi(headers=headers, plat_goods_ids=plat_goods_ids,
                                                                      question_b_id=question_b_id, replies=replies)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success' and result['code'] == 0

        with allure.step('验证关联上商品回复的添加是否成功'):
            result = self.question.question_b_goods_replies(headers=headers, question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success' and result['code'] == 0
            question_b_goods_replies_list = result["question_b_goods_replies"]
            allure.attach('关联商品回复列表', str(question_b_goods_replies_list))
            assert "关联商品回复" in str(question_b_goods_replies_list)

        with allure.step('刷新redis并重启晓多'):
            result = refresh_redis()
            assert result['test_code'] == 'success'
            result = dispatch("TBP-01", "restart_xiaoduo")
            # result = dispatch("TBP-01", "restart_xiaoduo")
            assert result['test_code'] == 'success'
            time.sleep(10)

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-好的知道了'):
            result = dispatch("TBP-01", "send_wangwang_msg", "好的知道了")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("你知道个啥"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "你知道个啥" in received_msg
            if "tb671067_2013" in received_msg:
                if "你知道个啥" in received_msg:
                    pass
                else:
                    assert received_msg == 0

        with allure.step('删除关联商品回复'):
            result = self.question.question_b_goods_replies_delete_multi(headers=headers, plat_goods_ids=plat_goods_ids,
                                                                         question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success' and result['code'] == 0

    @allure.story('关联商品回复')
    @allure.severity('normal')
    def test_shop_question_b_goods_replies_no_same_goods(self):
        """
        用例描述：自定义问题-关联商品回复-无焦点商品（关联商品测试）
        1.切换类目至男装
        2.针对固定的商品，添加商品回复
        3.验证是否添加成功
        4.刷新redis并重启晓多
        5.准备好回复的问题，好的知道了。
        6.验证回复
        7.删除关联商品回复
        """
        spliter = str(int(time.time() * 1000000))

        plat_goods_ids = "586920031576"
        question_b_id = '5c6e1cc3bf1f8f205c13e0ff'
        replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                  '"answer_pics":[]}]'
        shop_question_id = "5c6e1cc3bf1f8f205c13e0ff"
        goods_url = 'https://item.taobao.com/item.htm?id=586766818307'  # 与添加的商品不是一个

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            time.sleep(0.5)
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('对指定问题添加关联商品回复'):

            result = self.shopq.shop_question_goods_replies_new_multi(headers=headers, plat_goods_ids=plat_goods_ids,
                                                                      question_b_id=question_b_id, replies=replies,
                                                                      shop_question_id=shop_question_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success' and result['code'] == 0

        with allure.step('验证关联上商品回复的添加是否成功'):
            result = self.shopq.shop_questions_goods_replies(headers=headers, shop_question_id=shop_question_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success' and result['code'] == 0
            question_b_goods_replies_list = result["shop_question_goods_replies"]
            del_id = question_b_goods_replies_list[0]["id"]
            allure.attach('关联商品回复列表', str(question_b_goods_replies_list))
            assert "关联商品回复" in str(question_b_goods_replies_list)

        with allure.step('刷新redis并重启晓多'):
            result = refresh_redis()
            assert result['test_code'] == 'success'
            result = dispatch("TBP-01", "restart_xiaoduo")
            assert result['test_code'] == 'success'
            time.sleep(10)

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-关联商品测试'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "关联商品测试")
            # result = self.wangwang.send_msg(name=buyer, word="关联商品测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("关联商品自定义"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "关联商品自定义" in received_msg
            if "tb671067_2013" in received_msg:
                if "关联商品自定义" in received_msg:
                    pass
                else:
                    assert received_msg == 0
        with allure.step('删除关联商品回复'):
            result = self.shopq.shop_question_goods_replies_edit(headers=headers, id=del_id, replies="[]")
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success' and result['code'] == 0

    @allure.story('商品类型回复')
    @allure.severity('normal')
    def test_digc_replies_no_goods(self):
        """
        用例描述：行业问题-商品类型回复-没有焦点商品（关联商品测试）
        1.切换类目至男装
        2.发送焦点商品链接
        3.准备好回复的问题，纸条上写什么。
        4.验证回复
        """
        spliter = str(int(time.time() * 1000000))
        goods_url = 'https://item.taobao.com/item.htm?id=586920031576'  # 与添加的商品是一个

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            time.sleep(0.5)
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('刷新redis并重启晓多'):
            result = refresh_redis()
            assert result['test_code'] == 'success'
            result = dispatch("TBP-01", "restart_xiaoduo")
            assert result['test_code'] == 'success'
            time.sleep(10)

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-纸条上写什么'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "纸条上写什么")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("纸条上写什么"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "纸条上写什么" in received_msg
            if "tb671067_2013" in received_msg:
                if "纸条上写什么" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('商品类型回复')
    @allure.severity('normal')
    def test_digc_replies_no_goods(self):
        """
        用例描述：行业问题-商品类型回复-没有焦点商品（关联商品测试）
        1.切换类目至男装
        2.发送焦点商品链接
        3.准备好回复的问题，纸条上写什么。
        4.验证回复
        """
        spliter = str(int(time.time() * 1000000))
        goods_url = 'https://item.taobao.com/item.htm?id=586920031576'  # 与添加的商品是一个

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            time.sleep(0.5)
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('刷新redis并重启晓多'):
            result = refresh_redis()
            assert result['test_code'] == 'success'
            result = dispatch("TBP-01", "restart_xiaoduo")
            assert result['test_code'] == 'success'
            time.sleep(10)

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-纸条上写什么'):
            time.sleep(2)
            result = dispatch("TBP-01", "send_wangwang_msg", "纸条上写什么")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("纸条上写什么"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "纸条上写什么" in received_msg
            if "tb671067_2013" in received_msg:
                if "纸条上写什么" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('商品反问')
    @allure.severity('normal')
    def test_ask_url_enable(self):
        """
        用例描述：商品反问测试（裤脚多大）
        1.切换类目至男装
        2.开启商品反问
        2.刷新redis并重启晓多
        4.准备好回复的问题，裤脚多大。
        5.验证回复
        6.关闭商品反问
        """
        spliter = str(int(time.time() * 1000000))
        if "qa" in target_url:
            question_b_id_edit = '5c52d490bf1f8f31901ef8f0'
            ask_word = '口袋深浅'
        else:
            question_b_id_edit = '5ca2fe6b6f7d26000db6dc3a'
            ask_word = '裤脚多大'
        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            time.sleep(0.5)
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('开启商品反问'):
            result = self.question.question_b_edit_replies(headers=headers, question_b_id=question_b_id_edit,
                                                           is_rhetorical="true")
            self.log.info(result)
            assert result.get('test_code') == 'success'
            allure.attach('开启商品反问', str(result))

        with allure.step('刷新redis并重启晓多'):
            result = refresh_redis()
            assert result['test_code'] == 'success'
            result = dispatch("TBP-01", "restart_xiaoduo")
            assert result['test_code'] == 'success'
            time.sleep(10)

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试'):
            time.sleep(2)
            allure.attach('问答测试', str(ask_word))
            result = dispatch("TBP-01", "send_wangwang_msg", ask_word)
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("请问亲看的哪款宝贝，能发一下宝贝链接吗？"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            assert "请问亲看的哪款宝贝，能发一下宝贝链接吗？" in received_msg
            if "tb671067_2013" in received_msg:
                if "请问亲看的哪款宝贝，能发一下宝贝链接吗？" in received_msg:
                    pass
                else:
                    assert received_msg == 0

        with allure.step('关闭商品反问'):
            result = self.question.question_b_edit_replies(headers=headers, question_b_id=question_b_id_edit,
                                                           is_rhetorical="false")
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('关闭商品反问', str(result))

    @allure.story('商品反问')
    @allure.severity('normal')
    def test_ask_url_disable(self):
        """
        用例描述：商品反问测试（裤脚多大）
        1.切换类目至男装
        2.关闭商品反问
        2.刷新redis并重启晓多
        4.准备好回复的问题，裤脚多大。
        5.验证回复
        """
        spliter = str(int(time.time() * 1000000))
        if "test1" in target_url:
            question_b_id_edit = '5c52d490bf1f8f31901ef8f0'
            ask_word = '口袋深浅'
        else:
            question_b_id_edit = '5ca2fe6b6f7d26000db6dc3a'
            ask_word = '裤脚多大'

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            time.sleep(0.5)
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('开启商品反问'):
            result = self.question.question_b_edit_replies(headers=headers, question_b_id=question_b_id_edit,
                                                           is_rhetorical="false")
            self.log.info(result)
            assert result.get('test_code') == 'success'
            allure.attach('开启商品反问', str(result))

        with allure.step('刷新redis并重启晓多'):
            result = refresh_redis()
            assert result['test_code'] == 'success'
            result = dispatch("TBP-01", "restart_xiaoduo")
            assert result['test_code'] == 'success'
            time.sleep(10)

        with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
            result = dispatch("TBP-01", "send_qianniu_msg", spliter)
            assert result['test_code'] == 'success'

        with allure.step('问答测试'):
            time.sleep(2)
            allure.attach('问答测试', str(ask_word))
            result = dispatch("TBP-01", "send_wangwang_msg", ask_word)
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("裤脚多大回复"))
            # 休眠一下确保消息未接收到。
            time.sleep(5)
            result = dispatch("TBP-01", "get_qianniu_msg")
            self.log.info(result)
            assert result['test_code'] == 'success'
            received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
            allure.attach('客户端信息', str(received_msg))
            self.log.info(received_msg)
            if "test1" in target_url:
                assert "口袋深浅回复" in received_msg
                if "tb671067_2013" in received_msg:
                    if "口袋深浅回复" in received_msg:
                        pass
                    else:
                        assert received_msg == 0
            else:
                assert "裤脚多大回复" in received_msg
                if "tb671067_2013" in received_msg:
                    if "裤脚多大回复" in received_msg:
                        pass
                    else:
                        assert received_msg == 0


if __name__ == '__main__':
    pytest.main(['-s'])

# -*- coding: UTF-8 -*-
#  __author__ = 'zhy'

import pytest
import allure
import time

from local_lib.API.common import readconfig
from local_lib.API.common.tbp_log import Log
from local_lib.API.common.api_login import ApiLogin
from local_lib.API.tbp_api.问答.question import QuestionApi
from API.common.robot import RobotApi
from API.tbp_api.问答.shop import ShopApi, ShopQuestionApi
from config.globalparam import read_config
from config.globalparam import pro_ini_path
from src.scene_case.question.industry_scene_common import OtherCommon

read = readconfig.ReadConfig(pro_ini_path)
target_url = read.getValue('projectConfig', 'target_url')
seller = read_config.getValue('scence', 'seller')
buyer = read_config.getValue('scence', 'buyer')
comapny_name_list = read.getValue('scence', 'test_scence_company')

if target_url == 'http://wangcai.xiaoduoai.com':
    man_clothes_category_id = '597ea5ea369f99105c6d2d4c'  # 男装专属（VIP版）id
    kitchen_category_id = '5a829b295a9f720c6c02cc15'  # 厨房电器（VIP版）id
else:
    man_clothes_category_id = '597ea5ea369f99105c6d2d4c'  # 男装专属（VIP版）id
    kitchen_category_id = '5a829b7bbf1f8f20bbd9189e'  # 厨房电器（VIP版）id

man_clothes_url = 'https://item.taobao.com/item.htm?id=586766818307'  # 尺码表焦点商品
material_url = "https://item.taobao.com/item.htm?id=586635349110"
plat_goods_ids = "586920031576"  # 固定商品id（猫猫）
question_b_id = "597ea78981a8b207cef3a8e8"  # 问题qid


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
        self.common = OtherCommon()
        self.robot = RobotApi()

    @allure.story('安装费覆盖')
    @allure.severity('normal')
    def test_family_scenes(self):
        """
        用例描述：以特定场景触发安装费问答
        1.切换类目至厨房电器
        2.问安装费多少
        3.判断回复内容
        """
        self.common.change_category("厨房电器")
        self.common.other_robot_answer("安装费多少", "安装费回复")

    @allure.story('材质覆盖')
    @allure.severity('normal')
    def test_material(self):
        """
        用例描述：以特定场景触发材质问答
        1.切换类目至男装
        2.发送焦点商品（袜子）
        3.问，什么材质
        4.判断材质 蚕丝
        """
        self.common.change_category("男装专属")
        self.common.other_robot_answer(material_url)
        self.common.other_robot_answer("什么材质", "蚕丝")

    @allure.story('关联商品回复')
    @allure.severity('normal')
    def test_question_b_goods_replies_not_same_goods(self):
        """
        用例描述：行业问题-关联商品回复-不是一个焦点商品
        1.切换类目至男装
        2.针对固定的商品，添加商品回复
        3.验证是否添加成功
        4.发送焦点商品链接
        5.准备好回复的问题，好的知道了。
        6.验证回复
        7.删除关联商品回复
        """
        if target_url == 'http://wangcai.xiaoduoai.com':
            question_b_id = '597ea78981a8b207cef3a8e8'  # 固定问题的id
            replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                      '"answer_pics":[]}]'
        else:
            question_b_id = '597ea78981a8b207cef3a8e8'  # 固定问题的id
            replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                      '"answer_pics":[]}]'
        goods_url = 'https://item.taobao.com/item.htm?id=586766818307'  # 与添加的商品不是一个

        with allure.step('对好的知道了问题添加关联商品回复'):

            result = self.question.question_b_goods_replies_new_multi(headers=headers, plat_goods_ids=plat_goods_ids,
                                                                      question_b_id=question_b_id, replies=replies)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

        with allure.step('验证关联上商品回复的添加是否成功'):
            result = self.question.question_b_goods_replies(headers=headers, question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'
            question_b_goods_replies_list = result["question_b_goods_replies"]
            allure.attach('关联商品回复列表', str(question_b_goods_replies_list))
            assert "关联商品回复" in str(question_b_goods_replies_list)

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-好的知道了'):
            result = self.robot.robot_answer("好的知道了")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("你知道个啥"))
            received_msg = result['answer']
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
            assert result['test_code'] == 'success'

    @allure.story('关联商品回复')
    @allure.severity('normal')
    def test_question_b_goods_replies_same_goods(self):
        """
        用例描述：行业问题-关联商品回复-是一个焦点商品
        1.切换类目至男装
        2.针对固定的商品，添加商品回复
        3.验证是否添加成功
        4.发送焦点商品链接
        5.准备好回复的问题，好的知道了。
        6.验证回复
        7.删除关联商品回复
        """
        spliter = str(int(time.time() * 1000000))

        plat_goods_ids = "586920031576"  # 固定商品id（猫猫）
        question_b_id = '597ea78981a8b207cef3a8e8'  # 固定问题的id
        replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                  '"answer_pics":[]}]'
        goods_url = 'https://item.taobao.com/item.htm?id=586920031576'  # 与添加的商品是一个

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
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
            assert result['test_code'] == 'success'

        with allure.step('验证关联上商品回复的添加是否成功'):
            result = self.question.question_b_goods_replies(headers=headers, question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'
            question_b_goods_replies_list = result["question_b_goods_replies"]
            allure.attach('关联商品回复列表', str(question_b_goods_replies_list))
            assert "关联商品回复" in str(question_b_goods_replies_list)

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-好的知道了'):
            result = self.robot.robot_answer("好的知道了")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            received_msg = result['answer']
            self.log.info(received_msg)
            assert "关联商品回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "关联商品回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0
        with allure.step('删除关联商品回复'):
            result = self.question.question_b_goods_replies_delete_multi(headers=headers, plat_goods_ids=plat_goods_ids,
                                                                         question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

    @allure.story('关联商品回复')
    @allure.severity('normal')
    def test_shop_question_b_goods_replies_not_same_goods(self):
        """
        用例描述：自定义问题-关联商品回复-不是一个焦点商品（关联商品测试）
        1.切换类目至男装
        2.针对固定的商品，添加商品回复
        3.验证是否添加成功
        4.发送焦点商品链接
        5.准备好回复的问题，关联商品测试。
        6.验证回复
        7.删除关联商品回复
        """
        spliter = str(int(time.time() * 1000000))

        plat_goods_ids = "586920031576"
        if target_url == 'http://wangcai.xiaoduoai.com':
            question_b_id = '5c9c8dc5b04c180012882310'
            shop_question_id = "5c9c8dc5b04c180012882310"
        else:
            question_b_id = '5c6e1cc3bf1f8f205c13e0ff'
            shop_question_id = "5c6e1cc3bf1f8f205c13e0ff"
        replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                  '"answer_pics":[]}]'
        goods_url = 'https://item.taobao.com/item.htm?id=586766818307'  # 与添加的商品不是一个

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
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
            assert result['test_code'] == 'success'

        with allure.step('验证关联上商品回复的添加是否成功'):
            result = self.shopq.shop_questions_goods_replies(headers=headers, shop_question_id=shop_question_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'
            question_b_goods_replies_list = result["shop_question_goods_replies"]
            del_id = question_b_goods_replies_list[0]["id"]
            allure.attach('关联商品回复列表', str(question_b_goods_replies_list))
            assert "关联商品回复" in str(question_b_goods_replies_list)

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-关联商品测试'):
            result = self.robot.robot_answer("关联商品测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("关联商品自定义"))
            received_msg = result['answer']
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
            assert result['test_code'] == 'success'

    @allure.story('关联商品回复')
    @allure.severity('normal')
    def test_shop_question_b_goods_replies_same_goods(self):
        """
        用例描述：自定义问题-关联商品回复-是一个焦点商品（关联商品测试）
        1.切换类目至男装
        2.针对固定的商品，添加商品回复
        3.验证是否添加成功
        4.发送焦点商品链接
        5.准备好回复的问题，好的知道了。
        6.验证回复
        7.删除关联商品回复
        """
        spliter = str(int(time.time() * 1000000))
        if target_url == 'http://wangcai.xiaoduoai.com':
            question_b_id = '5c9c8dc5b04c180012882310'
            shop_question_id = "5c9c8dc5b04c180012882310"
        else:
            question_b_id = '5c6e1cc3bf1f8f205c13e0ff'
            shop_question_id = "5c6e1cc3bf1f8f205c13e0ff"

        plat_goods_ids = "586920031576"
        replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                  '"answer_pics":[]}]'
        goods_url = 'https://item.taobao.com/item.htm?id=586920031576'  # 与添加的商品不是一个

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
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
            assert result['test_code'] == 'success'

        with allure.step('验证关联上商品回复的添加是否成功'):
            result = self.shopq.shop_questions_goods_replies(headers=headers, shop_question_id=shop_question_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'
            question_b_goods_replies_list = result["shop_question_goods_replies"]
            del_id = question_b_goods_replies_list[0]["id"]
            allure.attach('关联商品回复列表', str(question_b_goods_replies_list))
            assert "关联商品回复" in str(question_b_goods_replies_list)

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-关联商品测试'):
            result = self.robot.robot_answer("关联商品测试")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("关联商品回复"))
            received_msg = result['answer']
            self.log.info(received_msg)
            assert "关联商品回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "关联商品回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0

        with allure.step('删除关联商品回复'):
            result = self.shopq.shop_question_goods_replies_edit(headers=headers, id=del_id, replies="[]")
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

    @allure.story('商品类型回复')
    @allure.severity('normal')
    def test_digc_replies_same_goods(self):
        """
        用例描述：行业问题-商品类型回复-是一个焦点商品（关联商品测试）
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
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-纸条上写什么'):
            result = self.robot.robot_answer("纸条上写什么")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("商品类型回复"))
            received_msg = result['answer']
            self.log.info(received_msg)
            assert "商品类型回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "商品类型回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('商品类型回复')
    @allure.severity('normal')
    def test_digc_replies_not_same_goods(self):
        """
        用例描述：行业问题-商品类型回复-不是一个焦点商品（关联商品测试）
        1.切换类目至男装
        2.发送焦点商品链接
        3.准备好回复的问题，纸条上写什么。
        4.验证回复
        """
        spliter = str(int(time.time() * 1000000))
        goods_url = 'http://item.taobao.com/item.htm?id=586587454967'  # 与添加的商品不是一个

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-纸条上写什么'):
            result = self.robot.robot_answer("纸条上写什么")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            received_msg = result['answer']
            self.log.info(received_msg)
            assert "纸条上写什么" in received_msg
            if "tb671067_2013" in received_msg:
                if "纸条上写什么" in received_msg:
                    pass
                else:
                    assert received_msg == 0

    @allure.story('自动回复优先级比较')
    @allure.severity('normal')
    def test_replies_level_01(self):
        """
        用例描述：关联商品回复和商品类型回复优先级比较
        1.切换类目至男装
        2.针对固定的商品，添加商品回复
        3.验证是否添加成功
        4.添加商品类型回复
        5.验证是否添加成功
        6.发送焦点商品链接
        7.准备好回复的问题，会不会短。
        8.验证回复
        9.删除关联商品回复
        10.删除商品类型回复
        """
        spliter = str(int(time.time() * 1000000))

        plat_goods_ids = "586920031576"  # 固定商品id（猫猫）

        if target_url == 'http://wangcai.xiaoduoai.com':
            question_b_id = '5c46f73fdbfb72054206be36'
            question_b_id_q = '5c46f73fdbfb72054206be36'
            category_id_q = '5c9c8ff90e95093a8d5635fb'
        else:
            question_b_id = '5c46f404bf1f8f0b23e81013'
            question_b_id_q = '5c46f404bf1f8f0b23e81013'
            category_id_q = '5c4ffcf21f76570001550cbc'

        replies = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"关联商品回复",' \
                  '"answer_pics":[]}]'
        goods_url = 'https://item.taobao.com/item.htm?id=586920031576'  # 与添加的商品是一个
        replies_q = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"商品类型回复",' \
                    '"answer_pics":[]}]'

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('添加关联商品回复'):

            result = self.question.question_b_goods_replies_new_multi(headers=headers, plat_goods_ids=plat_goods_ids,
                                                                      question_b_id=question_b_id, replies=replies)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

        with allure.step('验证是否添加成功'):
            result = self.question.question_b_goods_replies(headers=headers, question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'
            question_b_goods_replies_list = result["question_b_goods_replies"]
            allure.attach('关联商品回复列表', str(question_b_goods_replies_list))
            assert "关联商品回复" in str(question_b_goods_replies_list)

        with allure.step('添加商品类型回复'):

            result = self.question.new_digc_replies(replies=replies_q, category_id=category_id_q, headers=headers,
                                                    question_b_id=question_b_id_q)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

        with allure.step('验证是否添加成功'):
            result = self.question.digc_replies(headers=headers, question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'
            question_b_digc_replies_list = result["question_b_digc_replies"]
            allure.attach('商品类型回复列表', str(question_b_digc_replies_list))
            assert "商品类型回复" in str(question_b_digc_replies_list)
            del_id = result["question_b_digc_replies"][0]['id']

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-会不会短'):
            result = self.robot.robot_answer("会不会短")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            received_msg = result['answer']
            self.log.info(received_msg)
            assert "关联商品回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "关联商品回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0

        with allure.step('删除关联商品回复'):
            result = self.question.question_b_goods_replies_delete_multi(headers=headers, plat_goods_ids=plat_goods_ids,
                                                                         question_b_id=question_b_id)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

        with allure.step('删除商品类型回复'):
            result = self.question.edit_digc_replies(headers=headers, qid=del_id, replies="[]")
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

    # @allure.story('自动回复优先级比较')
    # @allure.severity('normal')
    # def test_replies_level_02(self):
    #     """
    #     用例描述：商品类型回复和尺码表优先级比较
    #     1.切换类目至男装
    #     2.添加商品类型回复
    #     3.验证是否添加成功
    #     4.发送焦点商品链接
    #     5.准备好回复的问题，高160重100穿多大。
    #     6.验证回复
    #     7.删除商品类型回复
    #     """
    #     spliter = str(int(time.time() * 1000000))
    #
    #     if target_url == 'http://wangcai.xiaoduoai.com':
    #         question_b_id = '597ea78881a8b207cef3a8ce'
    #         question_b_id_q = '597ea78881a8b207cef3a8ce'
    #         category_id_q = '5c9c8ff90e95093a8d5635fb'
    #     else:
    #         question_b_id = '597ea78881a8b207cef3a8ce'  # 固定问题的id
    #         question_b_id_q = '597ea78881a8b207cef3a8ce'
    #         category_id_q = '5c4ffcf21f76570001550cbc'
    #
    #     goods_url = 'https://item.taobao.com/item.htm?id=586920031576'  # 与添加的商品是一个
    #     replies_q = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"商品类型回复",' \
    #                 '"answer_pics":[]}]'
    #
    #     with allure.step('获取店铺初始信息'):
    #         result = self.shop.shop_default(headers=headers)
    #         self.log.info(result)
    #         assert result.get('test_code') == 'success' and result.get('code') == 0
    #         allure.attach('获取店铺初始信息成功，日志如下', str(result))
    #         deliver_goods_answer = result['doc']['deliver_goods_answer']
    #         return_goods_answer = result['doc']['return_goods_answer']
    #
    #     with allure.step('切换类目至男装'):
    #         result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
    #                                       deliver_goods_answer=deliver_goods_answer,
    #                                       return_goods_answer=return_goods_answer, express_name='undefined',
    #                                       other_express_name='undefined')
    #         self.log.info(result)
    #         assert result.get('test_code') == 'success' and result.get('code') == 0
    #         allure.attach('修改类目成功，日志如下', str(result))
    #
    #     with allure.step('添加商品类型回复'):
    #
    #         result = self.question.new_digc_replies(replies=replies_q, category_id=category_id_q, headers=headers,
    #                                                 question_b_id=question_b_id_q)
    #         allure.attach('测试结果', str(result))
    #         self.log.info(result)
    #         assert result['test_code'] == 'success'
    #
    #     with allure.step('验证是否添加成功'):
    #         result = self.question.digc_replies(headers=headers, question_b_id=question_b_id)
    #         allure.attach('测试结果', str(result))
    #         self.log.info(result)
    #         assert result['test_code'] == 'success'
    #         question_b_digc_replies_list = result["question_b_digc_replies"]
    #         allure.attach('商品类型回复列表', str(question_b_digc_replies_list))
    #         assert "商品类型回复" in str(question_b_digc_replies_list)
    #         del_id = result["question_b_digc_replies"][0]['id']
    #
    #     with allure.step('切换焦点商品'):
    #         allure.attach('焦点商品', str(goods_url))
    #         result = dispatch("TBP-01", "send_wangwang_msg", goods_url)
    #         assert result['test_code'] == 'success'
    #
    #     with allure.step('千牛主动发送一条消息，作为消息获取截断点。'):
    #         result = dispatch("TBP-01", "send_qianniu_msg", spliter)
    #         assert result['test_code'] == 'success'
    #
    #     with allure.step('问答测试-高160重100穿多大'):
    #         result = dispatch("TBP-01", "send_wangwang_msg", "高160重100穿多大")
    #         assert result['test_code'] == 'success'
    #
    #     with allure.step('获取客户端信息，判断回复是否正确'):
    #         allure.attach('待检查的消息标识', str("商品类型回复"))
    #         # 休眠一下确保消息未接收到。
    #         result = dispatch("TBP-01", "get_qianniu_msg")
    #         self.log.info(result)
    #         assert result['test_code'] == 'success'
    #         received_msg = json.loads(result.get("data")).get("contact").split(spliter)[-1]
    #         allure.attach('客户端信息', str(received_msg))
    #         self.log.info(received_msg)
    #         assert "商品类型回复" in received_msg
    #         if "tb671067_2013" in received_msg:
    #             if "商品类型回复" in received_msg:
    #                 pass
    #             else:
    #                 assert received_msg == 0
    #
    #     with allure.step('删除商品类型回复'):
    #         result = self.question.edit_digc_replies(headers=headers, qid=del_id, replies="[]")
    #         allure.attach('测试结果', str(result))
    #         self.log.info(result)
    #         assert result['test_code'] == 'success'

    @allure.story('自动回复优先级比较')
    @allure.severity('normal')
    def test_replies_level_03(self):
        """
        用例描述：商品类型回复和安装费优先级比较
        1.切换类目至厨房电器
        2.添加商品类型回复
        3.验证是否添加成功
        4.发送焦点商品链接
        5.准备好回复的问题，安装费是多少。
        6.验证回复
        7.删除商品类型回复
        """
        goods_url = 'https://item.taobao.com/item.htm?id=586766818307'  # 与添加的商品是一个
        replies_q = '[{"auto_send_in_auto_mode":true,"auto_send_in_hybrid_mode":true,"answer":"商品类型回复",' \
                    '"answer_pics":[]}]'
        if target_url == 'http://wangcai.xiaoduoai.com':
            question_b_id_q = '5a9115a71a6ab21e1f342e39'
            category_id_q = '5c9c8ff90e95093a8d5635fb'
        else:
            question_b_id_q = '5aa88837bf1f8f1c698e7cd7'
            category_id_q = '5c4ffcf21f76570001550cbc'

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至厨房电器'):
            result = self.shop.shop_setup(headers=headers, category_id=kitchen_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('添加商品类型回复'):

            result = self.question.new_digc_replies(replies=replies_q, category_id=category_id_q, headers=headers,
                                                    question_b_id=question_b_id_q)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

        with allure.step('验证是否添加成功'):
            result = self.question.digc_replies(headers=headers, question_b_id=question_b_id_q)
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'
            question_b_digc_replies_list = result["question_b_digc_replies"]
            allure.attach('商品类型回复列表', str(question_b_digc_replies_list))
            assert "商品类型回复" in str(question_b_digc_replies_list)
            del_id = result["question_b_digc_replies"][0]['id']

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(goods_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-安装费是多少'):
            result = self.robot.robot_answer("安装费是多少")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            received_msg = result['answer']
            self.log.info(received_msg)
            assert "商品类型回复" in received_msg
            if "tb671067_2013" in received_msg:
                if "商品类型回复" in received_msg:
                    pass
                else:
                    assert received_msg == 0

        with allure.step('删除商品类型回复'):
            result = self.question.edit_digc_replies(headers=headers, qid=del_id, replies="[]")
            allure.attach('测试结果', str(result))
            self.log.info(result)
            assert result['test_code'] == 'success'

    @allure.story('自动回复优先级比较')
    @allure.severity('normal')
    def test_replies_level_04(self):
        """
        用例描述：动态查询和行业问题比较
        1.切换类目至男装
        2.发送焦点商品链接
        3.准备好回复的问题，什么材质。
        4.验证回复
        """
        goods_url = 'https://item.taobao.com/item.htm?id=586920031576'

        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('获取店铺初始信息成功，日志如下', str(result))
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('切换类目至男装'):
            result = self.shop.shop_setup(headers=headers, category_id=man_clothes_category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach('修改类目成功，日志如下', str(result))

        with allure.step('切换焦点商品'):
            allure.attach('焦点商品', str(goods_url))
            result = self.robot.robot_answer(material_url)
            assert result['test_code'] == 'success'

        with allure.step('问答测试-什么材质'):
            result = self.robot.robot_answer("什么材质")
            assert result['test_code'] == 'success'

        with allure.step('获取客户端信息，判断回复是否正确'):
            allure.attach('待检查的消息标识', str("蚕丝"))
            received_msg = result['answer']
            self.log.info(received_msg)
            assert "蚕丝" in received_msg
            if "tb671067_2013" in received_msg:
                if "蚕丝" in received_msg:
                    pass
                else:
                    assert received_msg == 0


if __name__ == '__main__':
    pytest.main(['-s'])

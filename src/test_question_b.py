# -*- coding: UTF-8 -*-
#  __author__ = 'zhy'

import pytest
import allure
import time
import os
import xlrd

from local_lib.API.common.api_login import ApiLogin
from local_lib.API.common.tbp_log import Log
from API.tbp_api.设置.问答通用设置.category import CategoryApi
from local_lib.API.tbp_api.问答.question import QuestionApi
from API.common.robot import RobotApi
from API.tbp_api.问答.shop import ShopApi
from local_lib.API.common.utils import readconfig
from config.globalparam import pro_ini_path, read_config
from config.globalparam import project_abs_path

ask_path = 'ask.xls'
ask_folder = os.path.join(project_abs_path, 'testdata')
ask_data = os.path.join(ask_folder, ask_path)

data = xlrd.open_workbook(ask_data)
table = data.sheets()[0]
ask_list = []
for i in range(1, int(table.nrows)):
    ask_l = []
    categorys = table.row_values(i)[0]
    semantics = table.row_values(i)[1]
    ask1 = table.row_values(i)[2]
    ask_l.append(ask1)
    ask2 = table.row_values(i)[3]
    ask_l.append(ask2)
    ask3 = table.row_values(i)[4]
    ask_l.append(ask3)
    data = {
        "categorys": categorys,
        "semantics": semantics,
        "ask": ask_l,
    }
    ask_list.append(data)

headers = {}
read = readconfig.ReadConfig(pro_ini_path)
test_comapny = read.getValue('projectConfig', 'test_comapny')
#test_comapny = "杜可风按"
comapny_name_list = [test_comapny]
subcategory_list = [
    ('开始语', '586b8ffe89bc4629df21bbbe'),
    ('聊天互动', '5c385d05d0aed8145ec540ec'),
    ('商品问题', '5c385d05d0aed8145ec540eb')
]
all_categorys = []
qs_list_1 = ['这个多少钱', '明白了', '知道了']
qs_list_2 = ['大概什么时候有货', '这款什么时候能有货', '啥时候会有货啊？']
qs_list_t1 = list(set(qs_list_1).union(qs_list_2))
qs_list_3 = ['这个多少钱', '拍下多少钱？', '这款价格是多少啊？']
qs_list_4 = ['是正品吗', '亲，宝贝是正品么', '你们保证是正品吧']
qs_list_t2 = list(set(qs_list_3).union(qs_list_4))


def get_all_categorys():
    global all_categorys
    r = ApiLogin().login(company_name=test_comapny)
    headers = r.get("headers")
    result = CategoryApi().get_list(headers=headers)
    read = readconfig.ReadConfig(pro_ini_path)
    target_url = read.getValue('projectConfig', 'target_url')
    Log().info(result)
    if "qa" in target_url or "wangcai.xiaoduoai" in target_url:
        for ca in result['categories']:
            if ca["name"] in str(ask_list):
                data = (ca['name'], ca['id'])
                all_categorys.append(data)
    else:
        for ca in result['categorys']:
            if ca["name"] in str(ask_list):
                data = (ca['name'], ca['id'])
                all_categorys.append(data)
    # debug for only 1 category.
    # all_categorys = all_categorys[:1]
    return all_categorys


epic_platform = read_config.getValue('projectConfig', 'epic_platform')


@allure.epic(epic_platform)
@allure.feature('店铺问答')
@pytest.mark.question
class TestQuestion(object):
    def setup_class(self):
        global headers
        self.log = Log()
        self.shop = ShopApi()
        self.robotApi = RobotApi()
        self.login = ApiLogin()
        self.question = QuestionApi()
        self.category = CategoryApi()
        result = self.login.login(company_name=test_comapny)
        self.log.info(result)
        assert result.get('test_code') == 'success'
        headers = result.get("headers")

    @pytest.mark.parametrize('category_name, category_id', get_all_categorys())
    @allure.story('问答测试')
    @allure.title('问答测试')
    @allure.severity('normal')
    def test_update_category_and_search_question(self, category_name, category_id):
        """
        用例描述：更换类目，问答指定问题，验证机器人是否识别。
        """
        allure.attach('名称：' + str(category_name) + "\nid:" + str(category_id), '类目信息')
        # category_name='运动器械（VIP版）' category_id='5c385d14d68f6c330a1fd66e'
        with allure.step('获取店铺初始信息'):
            result = self.shop.shop_default(headers=headers)
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach(str(result), '获取店铺初始信息成功，日志如下')
            deliver_goods_answer = result['doc']['deliver_goods_answer']
            return_goods_answer = result['doc']['return_goods_answer']

        with allure.step('修改类目'):
            time.sleep(0.5)
            result = self.shop.shop_setup(headers=headers, category_id=category_id,
                                          deliver_goods_answer=deliver_goods_answer,
                                          return_goods_answer=return_goods_answer, express_name='undefined',
                                          other_express_name='undefined')
            self.log.info(result)
            assert result.get('test_code') == 'success' and result.get('code') == 0
            allure.attach(str(result), '修改类目成功，日志如下')

        with allure.step('验证识别'):
            ass_num = 0
            for i in ask_list:
                if i.get("categorys") == category_name:
                    semantics = i.get("semantics")
                    ask = i["ask"]
                    for j in ask:
                        result = self.robotApi.robot_answer(question=j)
                        self.log.info(result)
                        assert result.get('test_code') == 'success'
                        # matched_question = result.get("matched_question")
                        # assert matched_question is not None  # 一个类目有一组语义不识别，后面能识别的也不能进入判断了，需要后续优化
                        hit_question = result.get('matched_question').get('question')
                        allure.attach(str(hit_question), '问答识别击中的问题')
                        with allure.step("判断识别的正确性"):
                            allure.attach(str(semantics), "期望识别结果")
                            allure.attach(str(hit_question), "实际识别结果")
                        if hit_question == semantics:
                            pass
                        else:
                            ass_num += 1
            assert ass_num == 0, "有语义未识别"

            # @pytest.mark.parametrize('category_name, category_id', get_all_categorys())
            # @allure.story('问答测试')
            # @allure.severity('normal')
            # def test_update_category_and_search_question(self, category_name, category_id):
            #     """
            #     用例描述：更换类目，问答指定问题，验证机器人是否识别。
            #     备注：个别样本识别失败，是数据标注、识别准确的问题。同一个类目下，聊天互动可以识别，基本可以判定类目没有问题。
            #     """
            #     question_lists = []
            #     allure.attach('类目信息', '名称：' + str(category_name) + "\nid:" + str(category_id))
            #     # category_name='运动器械（VIP版）' category_id='5c385d14d68f6c330a1fd66e'
            #     with allure.step('获取店铺初始信息'):
            #         result = self.shop.shop_default(headers=headers)
            #         self.log.info(result)
            #         assert result.get('test_code') == 'success' and result.get('code') == 0
            #         allure.attach('获取店铺初始信息成功，日志如下', str(result))
            #         deliver_goods_answer = result['doc']['deliver_goods_answer']
            #         return_goods_answer = result['doc']['return_goods_answer']
            #
            #     with allure.step('修改类目'):
            #         time.sleep(0.5)
            #         result = self.shop.shop_setup(headers=headers, category_id=category_id,
            #                                       deliver_goods_answer=deliver_goods_answer,
            #                                       return_goods_answer=return_goods_answer, express_name='undefined',
            #                                       other_express_name='undefined')
            #         self.log.info(result)
            #         assert result.get('test_code') == 'success' and result.get('code') == 0
            #         allure.attach('修改类目成功，日志如下', str(result))
            #     '''
            #     with allure.step('随机选择问题-4个语义每个语义随机两个问题'):
            #         data1 = random.sample(list(range(3)), 2)
            #         for data in data1:
            #             question_lists.append(qs_list_1[data])
            #         data2 = random.sample(list(range(3)), 2)
            #         for data in data2:
            #             question_lists.append(qs_list_2[data])
            #         data3 = random.sample(list(range(3)), 2)
            #         for data in data3:
            #             question_lists.append(qs_list_3[data])
            #         data4 = random.sample(list(range(3)), 2)
            #         for data in data4:
            #             question_lists.append(qs_list_4[data])
            #         self.log.info(question_lists)
            #         allure.attach('随机出待验证的问题', str(question_lists))
            #     '''
            #     with allure.step('验证识别 - 开始语'):
            #         _check_index = 0
            #         for qs in qs_list_t1:
            #             time.sleep(0.5)
            #             result = self.search.search2(headers=headers, keyword=qs)
            #             self.log.info(result)
            #             assert result.get('test_code') == 'success' and result.get("code") == 0
            #             robot_reply = result.get("robot_reply")
            #             keyword = result.get("keyword")
            #             if robot_reply:
            #                 question = robot_reply['emed_object']['question']
            #                 allure.attach("Keyword: " + str(keyword) + " -> Question: " + str(question), str(result))
            #             else:
            #                 _check_index += 1
            #                 allure.attach("Keyword: " + str(keyword) + " -> 未识别。", str(result))
            #
            #         assert _check_index == 0, '类目问题识别失败' + str(_check_index) + '次。'
            #
            #     with allure.step('验证识别 - 聊天互动'):
            #         _check_index = 0
            #         for qs in qs_list_t2:
            #             time.sleep(0.5)
            #             result = self.search.search2(headers=headers, keyword=qs)
            #             self.log.info(result)
            #             assert result.get('test_code') == 'success' and result.get("code") == 0
            #             robot_reply = result.get("robot_reply")
            #             keyword = result.get("keyword")
            #             if robot_reply:
            #                 question = robot_reply['emed_object']['question']
            #                 allure.attach("Keyword: " + str(keyword) + " -> Question: " + str(question), str(result))
            #             else:
            #                 _check_index += 1
            #                 allure.attach("Keyword: " + str(keyword) + " -> 未识别。", str(result))
            #
            #         assert _check_index == 0, '类目问题识别失败' + str(_check_index) + '次。'

            # @allure.story('获取行业分类问题')
            # @allure.severity('normal')
            # def test_get_subcategorys(self):
            #     """
            #     用例描述：获取行业分类问题。开市语，聊天互动，商品问题等
            #     """
            #     global headers
            #     global subcategory_list
            #     with allure.step('获取分类信息'):
            #         result = self.shop.subcategorys(headers=headers)
            #         self.log.info(result)
            #         assert result.get('test_code') == 'success'
            #         for subcategory in result["subcategorys"]:
            #             if subcategory['name'] == '开始语':
            #                 begin_id = subcategory['id']
            #                 data = ('开始语', begin_id)
            #                 subcategory_list.append(data)
            #             if subcategory['name'] == '聊天互动':
            #                 contact_id = subcategory['id']
            #                 data = ('聊天互动', contact_id)
            #                 subcategory_list.append(data)
            #             if subcategory['name'] == '商品问题':
            #                 product_id = subcategory['id']
            #                 data = ('商品问题', product_id)
            #                 subcategory_list.append(data)

            # @pytest.mark.parametrize('subcategory_name, subcategory_id', subcategory_list)
            # @allure.story('获取待测试的问题')
            # @allure.severity('normal')
            # def test_get_question(self, subcategory_name, subcategory_id):
            #     """
            #     用例描述：获取行业分类问题。开市语，聊天互动，商品问题等
            #     """
            #     global headers
            #     question_list = []
            #     with allure.step('开始随机选择问题-分类'):
            #         result = self.question.question_b_list(headers=headers, subcategory_id=subcategory_id)
            #         self.log.info(result)
            #         assert result.get('test_code') == 'success'
            #         total = result.get("total")
            #         if subcategory_name == '开始语':
            #             if total <= 2:
            #                 for question in result.get("question_bs"):
            #                     question_list.append(question.get("question"))
            #             else:
            #                 if total <= 19:
            #                     question_list_num = random.sample(list(range(int(total))), 2)
            #                     for num in question_list_num:
            #                         question_list.append(result["question_bs"][num]["question"])
            #                 else:
            #                     question_list_num = random.sample(list(range(int(19))), 2)
            #                     for num in question_list_num:
            #                         question_list.append(result["question_bs"][num]["question"])
            #         if subcategory_name == '聊天互动':
            #             if total <= 3:
            #                 for question in result.get("question_bs"):
            #                     question_list.append(question.get("question"))
            #             else:
            #                 if total <= 19:
            #                     question_list_num = random.sample(list(range(int(total))), 3)
            #                     for num in question_list_num:
            #                         question_list.append(result["question_bs"][num]["question"])
            #                 else:
            #                     question_list_num = random.sample(list(range(int(19))), 3)
            #                     for num in question_list_num:
            #                         question_list.append(result["question_bs"][num]["question"])
            #         if subcategory_name == '商品问题':
            #             if total <= 3:
            #                 for question in result.get("question_bs"):
            #                     question_list.append(question.get("question"))
            #             else:
            #                 if total <= 19:
            #                     question_list_num = random.sample(list(range(int(total))), 3)
            #                     for num in question_list_num:
            #                         question_list.append(result["question_bs"][num]["question"])
            #                 else:
            #                     question_list_num = random.sample(list(range(int(19))), 3)
            #                     for num in question_list_num:
            #                         question_list.append(result["question_bs"][num]["question"])
            #         allure.attach('随机问题选择', str(question_list))
            #
            #     for qs in question_list:
            #         with allure.step('验证机器人是否识别'):
            #             result = self.search.search2(headers=headers, keyword=qs)
            #             self.log.info(result)
            #             assert result.get('test_code') == 'success' and result.get("code") == 0
            #             robot_reply = result.get("robot_reply")
            #             assert robot_reply


if __name__ == '__main__':
    pytest.main(['-s'])

# -*- coding: UTF-8 -*-
#  __author__ = 'zhy'

import pytest
import allure
import requests

from abandoned.fuwu_order_list import FuwuOrderApi
from abandoned import UserOrderInfoApi
from API.common.api_login import StatLoginApi
from local_lib.API.common.tbp_log import Log

headers = {}
r1 = requests.session()
r2 = requests.session()


@allure.feature('对比授权信息')
@pytest.mark.compare_auth
class TestChannel(object):
    def setup_class(self):
        self.log = Log()
        self.login = StatLoginApi()
        self.fuwu_order = FuwuOrderApi()
        self.user_order_info = UserOrderInfoApi()
        global headers
        account = 'admin'
        password = 'xiaoduoxmrlbz2018'
        result = self.login.login(account=account, password=password)
        assert result.get('test_code') == 'success'
        headers = {
            "Authorization": result.get('Authorization'),
        }

    @pytest.mark.parametrize('nick', ['tb425734443', '杜可风按', '杨伟伟673738818 ', '古迪家居旗舰店'])
    @allure.story('对比授权信息')
    @allure.severity('critical')
    def test_compare_auth_data(self, nick):
        """
        用例描述：对比客户的授权信息。
        """
        data = {}
        with allure.step('获取普通版订购数据信息'):
            fuwu = self.fuwu_order.fuwu_order_list(nick=nick, headers=headers, sort="tb_create_desc", limit=50,
                                                   session=r1)
            allure.attach('测试结果', str(fuwu))
            assert fuwu.get('test_code') == 'success'
        with allure.step('获取升级版订购数据信息'):
            plugin = self.fuwu_order.plugin_fuwu_order_list(nick=nick, headers=headers, sort="tb_create_desc", limit=50,
                                                            session=r1)
            allure.attach('测试结果', str(plugin))

            assert plugin.get('test_code') == 'success'
        with allure.step('获取客拉客订购数据信息'):
            klk_fuwu = self.fuwu_order.klk_fuwu_order_list(nick=nick, headers=headers, sort="tb_create_desc", limit=50,
                                                           session=r1)
            allure.attach('测试结果', str(klk_fuwu))
            assert klk_fuwu.get('test_code') == 'success'
        with allure.step('获取客拉客-客服外包订购数据信息'):
            klk_outsource = self.fuwu_order.klk_outsource_fuwu_order_list(nick=nick, headers=headers,
                                                                          sort="tb_create_desc", limit=50, session=r1)
            allure.attach('测试结果', str(klk_outsource))
            assert klk_outsource.get('test_code') == 'success'
        with allure.step('获取api接口信息'):
            api_data = self.user_order_info.api_method(usr_nick=nick, session=r2)
            allure.attach('测试结果', str(api_data))
            assert api_data.get('test_code') == 'success'

        if fuwu.get('nick_name'):
            data = fuwu
        if plugin.get('nick_name'):
            data = plugin
        if klk_fuwu.get('nick_name'):
            data = klk_fuwu
        if klk_outsource.get('nick_name'):
            data = klk_outsource
        if data.get('end_date') == api_data.get('expire_day') and data.get('is_auth') == api_data.get('is_authorized'):
            allure.attach('测试结果', "数据一致")
            print("数据一致")
        if data.get('end_date') != api_data.get('expire_day'):
            allure.attach('测试结果', "订购周期结束时间不一致")
            print("订购周期结束时间不一致")
            assert "订购周期结束时间不一致" == ''
        if data.get('is_auth') != api_data.get('is_authorized'):
            allure.attach('测试结果', "授权信息不一致")
            print("授权信息不一致")
            assert "授权信息不一致" == ''


if __name__ == '__main__':
    pytest.main(['-s'])

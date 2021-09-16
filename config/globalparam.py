import os
from local_lib.API.common import writeconfig, readconfig

project_abs_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

goods_intent_import_path = os.path.join(os.path.join(project_abs_path, 'import4.0'), 'goods_intent_import.xlsx')
goods_question_b_import_path = os.path.join(os.path.join(project_abs_path, 'import4.0'), 'goods_question_b_import.xlsx')
goods_shop_question_import_path = os.path.join(os.path.join(project_abs_path, 'import4.0'), 'goods_shop_question_import.xlsx')
intent_answer_import_path = os.path.join(os.path.join(project_abs_path, 'import4.0'), 'intent_answer_import.xlsx')
question_b_answer_import_path = os.path.join(os.path.join(project_abs_path, 'import4.0'), 'question_b_answer_import.xlsx')
shop_intent_import_path = os.path.join(os.path.join(project_abs_path, 'import4.0'), 'shop_intent_import.xlsx')
shop_question_import_path = os.path.join(os.path.join(project_abs_path, 'import4.0'), 'shop_question_import.xlsx')

# 项目参数设置
# prj_path = read_config.getValue('projectConfig', 'project_path')
# prj_path1 = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".")

# 日志路径
# log_path = os.path.join(prj_path, 'log')
log_path = os.path.join(project_abs_path, 'log')

# 商品对比里面导入文件的路径
goods_compare_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'goods_compare.xlsx')

# secmessage.dll文件
sec_message_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'SecMessage.dll')

# 商品列表导入文件路径
goods_list_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'goods_list.csv')

# 商品列表导入文件路径
intent_list_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'intent_list.xlsx')

# 商品推荐-搭配/相似商品导入文件路径
custom_list_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'custom_list.xlsx')

# 商品推荐-营销卖点导入文件路径
selling_point_list_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'selling_point_list.xlsx')

# session文件
session_path = os.path.join(os.path.join(os.path.join(os.path.join(project_abs_path, 'local_lib'), 'API'), 'common'),
                            'session.txt')
# mc_session文件
mc_session_path = os.path.join(os.path.join(os.path.join(os.path.join(project_abs_path, 'local_lib'), 'API'), 'common'),
                               'mc_session.txt')
# mc_质检词列表
qc_words_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'qc_words.xlsx')

# 打字王快捷短语
ms_words_path = os.path.join(os.path.join(project_abs_path, 'testdata'), '打字王快捷短语.xlsx')

# 知更-运营-专题问题包
special_topic_package = os.path.join(os.path.join(project_abs_path, 'testdata'), '问题包模板.xlsx')
# 废弃
pro_config_path = os.path.join(project_abs_path, 'config')
pro_ini_path = os.path.join(pro_config_path, 'pro_config.ini')
pic_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'upload.jpg')
pic_5M_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'upload_5M.png')
goods_import_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'goods_import.xlsx')
digc_import_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'digc_import.xlsx')
big_data_intent_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'big_data_intent.xlsx')
# shop_question_import_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'shop_question_import.xlsx')
activity_goods_import_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'activity_goods_import.xlsx')
exception_activity_goods_import_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'exception_goods_import.xlsx')
activity_question_import_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'activity_question_import.xlsx')
exception_activity_question_import_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'exception_activity_question_import.xlsx')

keyword_nlu_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'keyword_nlu_test.xlsx')
shop_question_nlu_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'shop_question_nlu_test.xlsx')
intenting_nlu_test_path = os.path.join(os.path.join(project_abs_path, 'testdata'), 'intent_nlu_test.xlsx')

write_config = writeconfig.WriteConfig(pro_ini_path)
read_config = readconfig.ReadConfig(pro_ini_path)
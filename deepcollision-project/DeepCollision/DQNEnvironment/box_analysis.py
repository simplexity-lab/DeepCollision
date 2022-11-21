import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import table

para8straight = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_para_1599837856_straight_data.csv', sep=',')['0'])
para8turning = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_para_1599615204_turning_data.csv', sep=',')['0'])
para12straight = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_more_para_1600264586_straight2_data.csv', sep=',')['0'])
para12turning = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_more_para_1599984542_turning_data.csv', sep=',')['0'])
para10turning = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_10paras_turning_1603096684_data.csv', sep=',')['0'])

# 没有Straight
para10straight = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_10para_1000i_straight_1603182795_data.csv', sep=',')['0'])

image_straight = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_1598707992_image_straight_data.csv', sep=',')['0'])

df = pd.DataFrame(image_straight)
print(df.describe())

image_turning = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_1603884120_image_turning_data.csv', sep=',')['0'])


para8_2s_straight = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_8_para_straight_1000i_2s_1605105733_data.csv', sep=',')['0'])

df = pd.DataFrame(image_turning)
print(df.describe())


para8_2s_turn = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/dqn_record_8_para_turning_1000i_2s_1604893531_data.csv', sep=',')['0'])

df = pd.DataFrame(image_turning)
print(df.describe())


random = np.array(
    pd.read_csv(filepath_or_buffer='./average_reward/random_record_turning_1604730750_data.csv', sep=',')['0'])

df = pd.DataFrame(image_turning)
print(df.describe())


# analysisData = {
#     '8Straight': para8straight,
#     '8Turning': para8turning,
#     '12Straight': para12straight,
#     '12Turning': para12turning,
#     '10Turning': para10turning,
#     '10Straight': para10straight
# }
#
# df = pd.DataFrame(analysisData)
# print(df.describe())
# np.round(df.describe(), 2).to_csv('./average_reward/describe.csv')
#
# fig, ax = plt.subplots(1, 1)
# table(ax, np.round(df.describe(), 2),
#       loc='upper right',
#       colWidths=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
# df.plot.box(title='Comparison of Different Strategies')
# plt.xlabel('Strategy')
# plt.ylabel('Award')
# plt.grid
# plt.grid(linestyle='--', alpha=0.3)
# plt.show()

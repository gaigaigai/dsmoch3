import streamlit as st
import pandas as pd
import pulp
import matplotlib.pyplot as plt
import japanize_matplotlib #日本語化matplotlib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ShiftScheduler import ShiftScheduler


# セッション状態の初期化
if 'optimization_done' not in st.session_state:
    st.session_state.optimization_done = False
    st.session_state.shift_scheduler = None

# タイトル
st.title("シフトスケジューリングアプリ")

# サイドバー
st.sidebar.header("データのアップロード")
calendar_file = st.sidebar.file_uploader("カレンダー", type=['csv'])
staff_file = st.sidebar.file_uploader("スタッフ", type=['csv'])


# タブ
tab1, tab2, tab3 = st.tabs(["カレンダー情報", "スタッフ情報", "シフト表作成"])

with tab1:
    st.markdown("## カレンダー情報")
    if calendar_file is not None:
        df_calendar = pd.read_csv(calendar_file)

        
        # テーブルの表示
        st.write("### アップロードされたテーブル")
        st.write(df_calendar)
        
with tab2:
    st.markdown("## スタッフ情報")
    if staff_file is not None:
        df_staff = pd.read_csv(staff_file)

        # テーブルの表示
        st.write("### アップロードされたテーブル")
        st.write(df_staff)

with tab3:
    if calendar_file is not None and staff_file is not None:
        shift_sch = ShiftScheduler()
        shift_sch.set_data(df_staff, df_calendar)
        shift_sch.build_model()
        shift_sch.solve()
        if st.button("最適化"):
            st.markdown("## 最適化結果")
            
            st.session_state.optimization_done = True
            st.session_state.shift_scheduler = shift_sch
        
        if st.session_state.optimization_done:
            shift_sch = st.session_state.shift_scheduler
            
            
            # 最適化結果の出力
            st.write("実行ステータス:", pulp.LpStatus[shift_sch.status])
            st.write("目的関数値:", pulp.value(shift_sch.model.objective))
            
            st.markdown("## シフト表")
            st.write(shift_sch.sch_df)
            st.markdown("## シフト数の充足確認")
            # Matplotlibで棒グラフを表示
            plt.figure(figsize=(15, 8))
            plt.bar(shift_sch.sch_df.index, shift_sch.sch_df.sum(axis=1))  # 色を適用
            #plt.xticks(rotation=90)  # x軸のラベルを傾けて読みやすくする
            st.pyplot(plt)
        
            st.markdown("## スタッフの希望の確認")
            plt.figure(figsize=(15, 8))
            plt.bar(df_calendar["日付"], df_calendar["出勤人数"])  # 色を適用
            #plt.xticks(rotation=90)  # x軸のラベルを傾けて読みやすくする
            st.pyplot(plt)
            
            st.markdown("## 責任者の合計シフト数の充足確認")
            plt.figure(figsize=(15, 8))
            plt.bar(shift_sch.sch_df.columns.values, shift_sch.sch_df.loc["A"]+shift_sch.sch_df.loc["D"])  # 色を適用
            #plt.xticks(rotation=90)  # x軸のラベルを傾けて読みやすくする
            st.pyplot(plt)

            if st.button("結果をダウンロード"):
                shift_sch.sch_df.to_csv('data/shift.csv')
                st.markdown("ダウンロード済")
        else:
            st.write("")


       



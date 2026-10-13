import streamlit as st
import pandas as pd
import numpy as np
import io

# ページの基本設定
st.set_page_config(page_title="仮想実験シミュレーター", layout="wide")

st.title("🧪 仮想実験シミュレーター")
st.write("Excel等から予測平均と標準偏差の表をコピーし、下の枠に直接ペーストしてください。")

# 1. データの入力 (テキストエリアへのペースト)
pasted_text = st.text_area("ここにデータをペースト（ヘッダー行を含めてください）", height=200)

if pasted_text:
    try:
        # ペーストされたテキスト（タブ区切り）をDataFrameとして読み込む
        df = pd.read_csv(io.StringIO(pasted_text), sep='\t')
        
        # タブ区切りで列が分かれなかった場合（カンマ区切り等を想定）のフォールバック
        if len(df.columns) < 2:
            df = pd.read_csv(io.StringIO(pasted_text), sep=',')
        
        st.subheader("📝 読み込まれた入力データ")
        st.dataframe(df)
        
        # 2. 実行ボタンと仮想結果の生成
        if st.button("🚀 このデータで実験を実行する", type="primary"):
            st.divider()
            
            # 「〇〇 GP 予測平均値」という列名から、出力対象の特性名を抽出
            mean_cols = [c for c in df.columns if "予測平均値" in c]
            
            results = []
            
            # 各行（各実験パターン）ごとに処理
            for index, row in df.iterrows():
                simulated_row = {}
                for mean_col in mean_cols:
                    prop_name = mean_col.replace(" GP 予測平均値", "")
                    std_col = f"{prop_name} GP 予測標準偏差"
                    
                    if std_col in df.columns:
                        mean_val = pd.to_numeric(row[mean_col], errors='coerce')
                        std_val = pd.to_numeric(row[std_col], errors='coerce')
                        
                        # 数値として正常に読み込めた場合のみ乱数生成
                        if pd.notna(mean_val) and pd.notna(std_val):
                            simulated_val = np.random.normal(loc=mean_val, scale=std_val)
                            simulated_row[prop_name] = round(simulated_val, 3)
                        else:
                            simulated_row[prop_name] = None
                
                results.append(simulated_row)
            
            # 結果をDataFrameに変換
            result_df = pd.DataFrame(results)
            # 行名を見やすく設定
            result_df.index = [f"パターン {i+1}" for i in range(len(result_df))]
            
            # 3. 結果の表示 (コピペ可能な形式)
            st.subheader("📊 仮想実験結果 (Y)")
            
            # 方法A: Streamlitの標準テーブル（右上にコピーボタンが自動で出ます）
            st.dataframe(result_df)
            
            # 方法B: 確実にExcel等にタブ区切りで貼り付けられるテキスト出力
            st.subheader("📋 コピー用テキスト")
            st.text_area(
                "以下のテキストを選択してコピーし、Excel等に貼り付けてください。", 
                result_df.to_csv(sep='\t'), 
                height=200
            )

    except Exception as e:
        st.error(f"データの読み込みに失敗しました。コピーした表の形式を確認してください。\n詳細エラー: {e}")
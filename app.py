import streamlit as st
import pandas as pd
import numpy as np

# ページの基本設定
st.set_page_config(page_title="仮想実験シミュレーター", layout="wide")

st.title("🧪 仮想実験シミュレーター")
st.write("実験データのCSVファイルをアップロードし、条件を選択して仮想実験を実行します。")

# 1. ファイルアップロードUIの作成
uploaded_file = st.file_uploader("実験データ (CSVファイル) をアップロードしてください", type=["csv"])

if uploaded_file is not None:
    # アップロードされたファイルを読み込む
    df = pd.read_csv(uploaded_file)
    
    # 出力対象の特性（CSVの列名から推測）
    target_properties = [
        "L値", "a値", "b値", "光沢", "DOI", 
        "ほう素溶出量", "フッ素溶出量", "耐酸性"
    ]
    
    # 2. ユーザーインターフェース (入力条件の選択)
    st.sidebar.header("🔬 実験条件の選択")
    experiment_idx = st.sidebar.selectbox(
        "実験パターン (行番号) を選択してください",
        options=df.index,
        format_func=lambda x: f"パターン {x+1}"
    )
    
    # 選択された行のデータを取得
    selected_row = df.loc[experiment_idx]
    
    # 入力条件の表示 (予測結果以外の列を抽出)
    st.subheader("📝 選択された入力条件 (X)")
    input_cols = [col for col in df.columns if "予測" not in col]
    input_data = selected_row[input_cols].to_frame().T
    st.dataframe(input_data, hide_index=True)
    
    # 3. 実行ボタンと仮想結果の生成
    if st.button("🚀 この条件で実験を実行する", type="primary"):
        st.divider()
        st.subheader("📊 仮想実験結果 (Y)")
        
        # 結果を表示するためのカラムを作成
        cols = st.columns(4)
        
        for i, prop in enumerate(target_properties):
            mean_col = f"{prop} GP 予測平均値"
            std_col = f"{prop} GP 予測標準偏差"
            
            if mean_col in df.columns and std_col in df.columns:
                mean_val = selected_row[mean_col]
                std_val = selected_row[std_col]
                
                # 正規分布に従う乱数を生成して仮想の実験結果とする
                simulated_value = np.random.normal(loc=mean_val, scale=std_val)
                
                # 結果をシンプルに数値のみ表示
                with cols[i % 4]:
                    st.metric(
                        label=f"{prop}",
                        value=f"{simulated_value:.3f}"
                    )
else:
    st.info("👆 上のボタンからCSVファイルをアップロードすると、シミュレーターが起動します。")
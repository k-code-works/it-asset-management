import streamlit as st
import csv
import os
from datetime import date

# ==================================
# 1. 基本設定
# ==================================

st.set_page_config(
    page_title="社内IT機器管理",
    page_icon="💻",
    layout="wide"
)

FILE = "assets_app.csv"

COLUMNS = [
    "管理番号", "資産名", "カテゴリ",
    "保管場所", "状態", "利用者", "貸出日"
]

# ==================================
# 2. 画面デザイン
# ==================================

st.markdown("""
<style>
.stApp {
    background-color: #F3F6FA;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #17365D;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# 3. データ読み込み・保存
# ==================================

def load_data():
    if not os.path.exists(FILE):
        return []

    with open(FILE, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save_data(data):
    with open(FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(data)


# ==================================
# 4. 共通ヘッダー
# ==================================

st.title("💻 社内IT機器・備品管理システム")
st.caption("INTERNAL IT ASSET MANAGEMENT")
st.divider()

assets = load_data()

menu = st.sidebar.radio(
    "メニュー",
    [
        "ダッシュボード",
        "機器登録",
        "貸出・返却",
        "資産一覧・検索"
    ]
)

st.sidebar.divider()
st.sidebar.caption("社内業務管理システム")
st.sidebar.caption("Python / Streamlit")


# ==================================
# 5. ダッシュボード
# ==================================

if menu == "ダッシュボード":

    st.subheader("資産管理ダッシュボード")

    total = len(assets)

    available = sum(
        1 for a in assets if a["状態"] == "使用可能"
    )

    loaned = sum(
        1 for a in assets if a["状態"] == "貸出中"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("登録資産数", f"{total} 件")
    col2.metric("使用可能", f"{available} 件")
    col3.metric("貸出中", f"{loaned} 件")

    st.divider()

    st.subheader("最新の登録資産")

    if assets:
        st.dataframe(
            assets[-10:][::-1],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("登録されている資産はありません。")


# ==================================
# 6. 機器登録
# ==================================

elif menu == "機器登録":

    st.subheader("IT機器・備品の新規登録")

    with st.form("asset_form"):

        name = st.text_input("資産名")
        category = st.selectbox(
            "カテゴリ",
            ["パソコン", "モニター", "周辺機器", "その他"]
        )
        location = st.text_input("保管場所")

        submitted = st.form_submit_button(
            "資産を登録する",
            use_container_width=True
        )

        if submitted:

            if not name.strip() or not location.strip():
                st.error("資産名と保管場所を入力してください。")

            else:

                new_id = f"PC{len(assets) + 1:03}"

                new_asset = {
                    "管理番号": new_id,
                    "資産名": name.strip(),
                    "カテゴリ": category,
                    "保管場所": location.strip(),
                    "状態": "使用可能",
                    "利用者": "",
                    "貸出日": ""
                }

                assets.append(new_asset)
                save_data(assets)

                st.success(f"{new_id} を登録しました。")
                st.rerun()


# ==================================
# 7. 貸出・返却
# ==================================

elif menu == "貸出・返却":

    st.subheader("貸出・返却管理")

    available = [
        a for a in assets if a["状態"] == "使用可能"
    ]

    loaned = [
        a for a in assets if a["状態"] == "貸出中"
    ]

    # 貸出処理

    st.markdown("### 機器の貸出")

    if available:

        with st.form("loan_form"):

            asset_id = st.selectbox(
                "貸し出す機器",
                [a["管理番号"] for a in available]
            )

            user = st.text_input("利用者名")

            submitted = st.form_submit_button(
                "貸出を登録する",
                use_container_width=True
            )

            if submitted:

                if not user.strip():
                    st.error("利用者名を入力してください。")

                else:

                    for a in assets:
                        if a["管理番号"] == asset_id:
                            a["状態"] = "貸出中"
                            a["利用者"] = user.strip()
                            a["貸出日"] = date.today().isoformat()

                    save_data(assets)
                    st.success("貸出を登録しました。")
                    st.rerun()

    else:
        st.info("貸出可能な機器はありません。")

    st.divider()

    # 返却処理

    st.markdown("### 機器の返却")

    if loaned:

        return_id = st.selectbox(
            "返却する機器",
            [a["管理番号"] for a in loaned],
            key="return_id"
        )

        if st.button("返却を完了する", use_container_width=True):

            for a in assets:
                if a["管理番号"] == return_id:
                    a["状態"] = "使用可能"
                    a["利用者"] = ""
                    a["貸出日"] = ""

            save_data(assets)
            st.success("返却しました。")
            st.rerun()

    else:
        st.info("返却対象の機器はありません。")



# ==================================
# 8. 資産一覧・検索・削除
# ==================================

elif menu == "資産一覧・検索":

    st.subheader("資産一覧・検索")

    # 検索条件

    keyword = st.text_input(
        "キーワード検索",
        placeholder="管理番号・資産名・利用者"
    )

    col1, col2 = st.columns(2)

    with col1:

        categories = ["すべて"] + list(set(
            a["カテゴリ"] for a in assets
        ))

        category = st.selectbox(
            "カテゴリ",
            categories
        )

    with col2:

        locations = ["すべて"] + list(set(
            a["保管場所"] for a in assets
        ))

        location = st.selectbox(
            "保管場所",
            locations
        )

    # 検索処理

    result = []

    for a in assets:

        keyword_match = (
            keyword.lower() in a["管理番号"].lower()
            or keyword.lower() in a["資産名"].lower()
            or keyword.lower() in a["利用者"].lower()
        )

        category_match = (
            category == "すべて"
            or a["カテゴリ"] == category
        )

        location_match = (
            location == "すべて"
            or a["保管場所"] == location
        )

        if keyword_match and category_match and location_match:
            result.append(a)

    st.divider()

    st.caption(f"検索結果：{len(result)}件")

    if result:

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        # CSVダウンロード

        csv_data = "\ufeff" + ",".join(COLUMNS) + "\n"

        for a in result:

            csv_data += ",".join(
                '"' + a[c].replace('"', '""') + '"'
                for c in COLUMNS
            ) + "\n"

        st.download_button(
            "📥 CSVをダウンロード",
            data=csv_data,
            file_name="資産管理一覧.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.divider()

        # 機器削除

        st.subheader("登録機器の削除")

        delete_ids = st.multiselect(
            "削除する機器を選択してください。",
            [a["管理番号"] for a in result]
        )

        if st.button(
            "選択した機器を削除",
            type="secondary",
            use_container_width=True
        ):

            if not delete_ids:

                st.warning("削除する機器を選択してください。")

            else:

                assets = [
                    a for a in assets
                    if a["管理番号"] not in delete_ids
                ]

                save_data(assets)

                st.success(
                    f"{len(delete_ids)}件の機器を削除しました。"
                )

                st.rerun()

    else:

        st.info("該当する資産はありません。")



# ==================================
# 9. フッター
# ==================================

st.divider()

st.caption(
    "社内IT機器・備品管理システム "
    "| 個人制作ポートフォリオ"
)

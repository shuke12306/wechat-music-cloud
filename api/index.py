# 文件路径: api/index.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ---------------------------------------------------------
# 配置区
# ---------------------------------------------------------
NODE_API_URL = "http://1310621164-f4a6ohqzp0.ap-shanghai.tencentscf.com"

# ⚠️ 这一大串是你的 VIP 身份，不要动它
MY_COOKIE = "MUSIC_U=00F6596B5B4EDF57B6B6069A0AB876181DB9E219FD3EDD19BD09634FE1027CCD7F1C3D101F9D7232E760DB6840B0FBCE72516F428EF57DEB7B391781023F2D001DBE2E6F799E1FA9D7E620F70716B12FA35831A348AFA7724D8CA2F9510ACEDCEAF9FE604AE83F1B52A40290EF24BEC41AF48981266E41389C97A69D90E8A1D2884EE4057B01562B229AE02524140B821D2C053F6C7BFC919E06EBF0FEE83E8EB35D754945157F7658DB2FB450B726DDB8E5D8FF33B4BD668B535AFA939740AD30678E8112C5D237B61A504F10FF3EB373364B4149B965EFB04FD2317082E4BCED0BD2CF37CB02FF54E9756B1470420CEFC58E7531C9C6DAF43725242AB660FCB53E6D001EDC37BEE3632BF21727C14F76B1C489BA5A25F830B7B4F5D493A8EAE7A1754E9D7BAC139F60101BD7C40E01183E412EF368EF478F346531CD2E2FF3E5477606EC794C239C995FD56EFB2196E5940F2B2CD3A4EDCBDC4B919F577090C367397A3F3635E0666337656A711E6C34;" 
# ---------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def music_handler():
    song_name = request.args.get('name')
    
    if not song_name:
        return jsonify({"code": 404, "msg": "歌名为空"})

    try:
        # --- 搜歌 ---
        search_url = f"{NODE_API_URL}/cloudsearch" 
        
        # ✅【关键修改 1】把 Cookie 塞进搜索参数里
        params = {
            'keywords': song_name, 
            'limit': 1,
            'cookie': MY_COOKIE 
        }
        
        headers = {"User-Agent": "Mozilla/5.0 (WeChat-Music-Proxy)"}
        
        r = requests.get(search_url, params=params, headers=headers, timeout=10)
        data = r.json()
        
        songs = data.get('result', {}).get('songs')
        if not songs:
            return jsonify({"code": 404, "msg": "搜不到"})

        target_song = songs[0]
        song_id = target_song['id']
        title = target_song['name']
        ar_list = target_song.get('ar', []) or target_song.get('artists', [])
        artist = ar_list[0]['name'] if ar_list else "未知歌手"
        al = target_song.get('al', {}) or target_song.get('album', {})
        cover_url = al.get('picUrl', '')

        # --- 拿链接 ---
        url_api = f"{NODE_API_URL}/song/url"
        
        # ✅【关键修改 2】把 Cookie 塞进获取链接参数里
        # 只有加了这一行，VIP 歌曲才能拿到播放链接
        url_params = {
            'id': song_id,
            'cookie': MY_COOKIE 
        }
        
        r_url = requests.get(url_api, params=url_params, headers=headers, timeout=10)
        url_data = r_url.json()
        
        music_url = ""
        if url_data.get('data'):
            music_url = url_data['data'][0]['url']
        
        # 兜底：如果没拿到链接，用官方直链
        if not music_url:
            music_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

        return jsonify({
            "code": 200,
            "title": title,
            "singer": artist,
            "cover": cover_url,
            "link": f"https://music.163.com/#/song?id={song_id}",
            "music_url": music_url
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})


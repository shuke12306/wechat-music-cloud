# 文件路径: api/index.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ---------------------------------------------------------
# 配置区
# ---------------------------------------------------------
NODE_API_URL = "http://1310621164-f4a6ohqzp0.ap-shanghai.tencentscf.com"

# 2. 【这里修改】填入你刚才复制的 MUSIC_U 的值
# ⚠️ 请把你刚才那一长串 Cookie 重新粘贴在下面的引号里！
MY_COOKIE = "MUSIC_U=00299593A21062FB9A0BFCFE704C3BCE4569070BB35B87AD3E57F271F569911D30E997C50122A16C973220EF24F54A739342D5CB6636F557B2A26E7CB17B8A50C43DE7C121012E9F7F9C6ABDABD0743EF2508504FB11916C35EFE01AD491B24CD3BBC6F8123957B3F8232FDA1921965FCE2D8AFB18DFF92E55BA6284931C3BC3EC0D0154CC04709B43B654716BC95F813AD0CDF04BA856F964ADFF960BCE22001F23A3F2849799CBAD2772DE64FF6066888DFC781CE86A22E3646D3A06B29BCF7C43832461179542E42FEA335BA6B97842D2FED8637D10036A6136A7C86A5FFA5E0833AC1D69AA42BA9595A0A358D6FD2000DDAC284441500C94041B125AC7A8FDCD24668B0EA7FE2254DDCEBC6AE7E5F8843676F6BC5F5B11100EF0AF87516947F637A0E0FECF50EF414604539FE5A1B0B06459482E6076386F7689D6B7F6206E5B7DE2B0DD9F363FB832B5DBA50F97CF9E37D3D96712D14EFD48BE9E0C6A2C893817569B123E2C622D59EB50E967C107" 
# ---------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def music_handler():
    # Vercel 有时会把参数放在 query string 里
    song_name = request.args.get('name')
    
    if not song_name:
        return jsonify({"code": 404, "msg": "歌名为空"})

    try:
        # --- 搜歌 ---
        search_url = f"{NODE_API_URL}/cloudsearch" 
        
        # ✅【修正点 1】把 Cookie 加入搜索参数
        params = {
            'keywords': song_name, 
            'limit': 1,
            'cookie': MY_COOKIE  # <--- 必须加这一行，大厨才知道你是VIP
        }
        
        # 增加 headers 伪装
        headers = {
            "User-Agent": "Mozilla/5.0 (WeChat-Music-Proxy)"
        }
        
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
        
        # ✅【修正点 2】把 Cookie 加入获取链接参数
        url_params = {
            'id': song_id,
            'cookie': MY_COOKIE  # <--- 必须加这一行，才能拿到 VIP 歌曲链接
        }
        
        r_url = requests.get(url_api, params=url_params, headers=headers, timeout=10)
        url_data = r_url.json()
        
        music_url = ""
        if url_data.get('data'):
            music_url = url_data['data'][0]['url']
        
        if not music_url:
            music_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

        # --- 返回 ---
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
